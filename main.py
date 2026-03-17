from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime, timedelta
from leads_db import guardar_lead
from fastapi import Response
import time

from estados import obtener_usuario, actualizar_datos, actualizar_estado
from ai import interpretar
from whatsapp import enviar_texto, enviar_imagen, notificar_cita
from sheets import guardar_cita
from mensajes_db import guardar_mensaje

from inmuebles import buscar_inmuebles, obtener_imagenes

app = FastAPI()
PALABRAS_REINICIO = ["hola", "menu", "inicio", "empezar", "volver","hi","buenos","buenas"]

# ---------- UTILIDADES ----------
def generar_dias_disponibles(cantidad=10):
    dias = []
    fecha = datetime.now()

    while len(dias) < cantidad:
        fecha += timedelta(days=1)
        if fecha.weekday() <= 5:
            dias.append(fecha)
    return dias


def generar_horarios(fecha):
    if fecha.weekday() <= 4:
        return [f"{h}:00" for h in range(8, 18)]
    else:
        return [f"{h}:00" for h in range(8, 17)]



# ---------- WEBHOOK ----------
@app.post("/webhook")
async def webhook(request: Request):

    form = await request.form()

    mensaje = form.get("Body", "").lower().strip()
    numero = form.get("From", "").replace("whatsapp:", "")
    
    # Guardar mensaje del usuario
    guardar_mensaje(numero, "in", mensaje)
    
    # Reiniciar conversación si el usuario lo pide
    if any(p in mensaje for p in PALABRAS_REINICIO):

        actualizar_datos(
            numero,
            tipo=None,
            presupuesto=None,
            seleccion=None,
            fecha_seleccionada=None
        )

        actualizar_estado(numero, "INICIO")

        texto = (
            "Hola 👋 Bienvenido a Inmobiliaria Sierra.\n"
            "¿Buscas *casa* o *apartamento*?"
        )

        enviar_texto(numero, texto)
        guardar_mensaje(numero, "out", texto)

        return Response(status_code=200)
    
    
    nombre = form.get("ProfileName", "cliente")
    
    

    print(f"📩 Mensaje de {numero} | Body: {mensaje}")

    if not numero:
        print("❌ Número vacío")
        return PlainTextResponse(status_code=200)

    usuario = obtener_usuario(numero)
    estado = usuario["estado"]

    info = interpretar(mensaje)

    print(f"estado {estado} | numero: {numero}")

    # ---------- INICIO ----------
    if estado == "INICIO":

        actualizar_estado(numero, "TIPO")

        usuario["estado"] = "TIPO"

        estado = "TIPO"

    # ---------- TIPO ----------
    elif estado == "TIPO":

        if not info.get("tipo"):

            texto = "¿Buscas casa o apartamento? 😊"

            enviar_texto(numero, texto)
            guardar_mensaje(numero, "out", texto)

            return PlainTextResponse(status_code=200)

        actualizar_datos(numero, tipo=info["tipo"])

        texto = "Perfecto 👍 ¿Cuál es tu presupuesto máximo? 💰"

        enviar_texto(numero, texto)
        guardar_mensaje(numero, "out", texto)

        actualizar_estado(numero, "PRESUPUESTO")

    # ---------- PRESUPUESTO ----------
    elif estado == "PRESUPUESTO":

        numero_info = info.get("numero")

        if not numero_info:

            texto = "Indícame el presupuesto en números 💵"

            enviar_texto(numero, texto)
            guardar_mensaje(numero, "out", texto)

            return PlainTextResponse(status_code=200)

        actualizar_datos(numero, presupuesto=numero_info)

        tipo = usuario["tipo"]
        opciones = buscar_inmuebles(tipo, numero_info)

        if not opciones:

            texto = "😕 No encontré inmuebles con ese presupuesto."

            enviar_texto(numero, texto)
            guardar_mensaje(numero, "out", texto)

            actualizar_estado(numero, "INICIO")

            return PlainTextResponse(status_code=200)


        texto = "🏘️ *Opciones disponibles:*\n\n"

        for i, o in enumerate(opciones, 1):
            texto += f"{i}. {o['tipo'].title()} en {o['barrio']} - ${o['precio']:,}\n"

        texto += "\nEscribe el *número* de la opción que te interesa 😉"

        enviar_texto(numero, texto)
        guardar_mensaje(numero, "out", texto)

        actualizar_estado(numero, "SELECCION")
        return PlainTextResponse(status_code=200)

    # ---------- SELECCION ----------
    # ---------- SELECCION ----------
    elif estado == "SELECCION":

        sel = info.get("numero")

        if not sel:
            texto = "Escríbeme el número de la opción que te gustó 😊"
            enviar_texto(numero, texto)
            guardar_mensaje(numero, "out", texto)
            return PlainTextResponse(status_code=200)

        # Siempre reconstruimos las opciones
        opciones = buscar_inmuebles(usuario["tipo"], usuario["presupuesto"])

        if sel < 1 or sel > len(opciones):

            texto = "Escríbeme el número de la opción que te gustó 😊"

            enviar_texto(numero, texto)
            guardar_mensaje(numero, "out", texto)

            return PlainTextResponse(status_code=200)

        inmueble = opciones[sel - 1]

        actualizar_datos(numero, seleccion=sel)

        usuario = obtener_usuario(numero)
        
        interes = f"{inmueble['tipo']} {inmueble['barrio']}"

        guardar_lead(
            numero,
            interes,
            usuario["presupuesto"]
        )

        texto = "¿Deseas ver *imágenes* del inmueble? 📸 (si / no)"

        enviar_texto(numero, texto)
        guardar_mensaje(numero, "out", texto)

        actualizar_estado(numero, "IMAGENES")

        return PlainTextResponse(status_code=200)
    
    elif estado == "IMAGENES":

        if info.get("afirmacion") == "si":

            opciones = buscar_inmuebles(usuario["tipo"], usuario["presupuesto"])

            inmueble = opciones[usuario["seleccion"] - 1]

            texto = (
                f"🏠 *{inmueble['tipo'].title()} en {inmueble['barrio']}*\n"
                f"💰 ${inmueble['precio']:,}\n\n"
                "📸 Estas son algunas fotos:"
            )

            enviar_texto(numero, texto)

            imagenes = obtener_imagenes(inmueble["id"])

            if imagenes:

                for i, img in enumerate(imagenes):

                    caption = inmueble["descripcion"] if i == 0 else None

                    enviar_imagen(numero, img, caption)

                    time.sleep(1.2)   # pausa entre imágenes

            else:
                enviar_texto(numero, "⚠️ Este inmueble aún no tiene fotos disponibles.")

        # pausa final antes de preguntar
        time.sleep(4)

        texto = "¿Deseas agendar una visita? 😊 (si / no)"

        enviar_texto(numero, texto)
        guardar_mensaje(numero, "out", texto)

        actualizar_estado(numero, "CONFIRMAR_AGENDA")

        return PlainTextResponse(status_code=200)
    
    
    # ---------- CONFIRMAR AGENDA ----------
    elif estado == "CONFIRMAR_AGENDA":

        if info.get("afirmacion") != "si":

            texto = "Perfecto 👍 Quedo atento."

            enviar_texto(numero, texto)
            guardar_mensaje(numero, "out", texto)

            actualizar_estado(numero, "INICIO")

            return PlainTextResponse(status_code=200)

        dias = generar_dias_disponibles()

        usuario["dias_disponibles"] = dias

        texto = "📅 *Días disponibles:*\n\n"

        for i, d in enumerate(dias, 1):
            texto += f"{i}. {d.strftime('%A %d de %B')}\n"

        texto += "\nEscribe el *número del día*"

        enviar_texto(numero, texto)
        guardar_mensaje(numero, "out", texto)

        actualizar_estado(numero, "AGENDAR_DIA")

    
    # ---------- AGENDAR DIA ----------
    elif estado == "AGENDAR_DIA":

        idx = info.get("numero")

        if not idx or idx > len(usuario["dias_disponibles"]):

            texto = "Elige un número válido 😊"

            enviar_texto(numero, texto)
            guardar_mensaje(numero, "out", texto)

            return PlainTextResponse(status_code=200)

        fecha = usuario["dias_disponibles"][idx - 1]

        actualizar_datos(numero, fecha_seleccionada=fecha)

        horarios = generar_horarios(fecha)

        usuario["horarios_disponibles"] = horarios

        texto = f"⏰ Horarios para {fecha.strftime('%A %d de %B')}:\n\n"

        for i, h in enumerate(horarios, 1):
            texto += f"{i}. {h}\n"

        texto += "\nEscribe el *número del horario*"

        enviar_texto(numero, texto)
        guardar_mensaje(numero, "out", texto)

        actualizar_estado(numero, "AGENDAR_HORA")    

        return PlainTextResponse(status_code=200)