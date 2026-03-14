from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime, timedelta

from estados import obtener_usuario, actualizar_datos, actualizar_estado
from ai import interpretar
from inmuebles import buscar_inmuebles
from whatsapp import enviar_texto, enviar_imagen
from sheets import guardar_cita
from mensajes_db import guardar_mensaje

app = FastAPI()

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

    mensaje = form.get("Body", "").lower()
    guardar_mensaje(numero, "in", mensaje)
    numero = form.get("From", "").replace("whatsapp:", "")

    print(f"📩 Mensaje de {numero} | Body: {mensaje}")

    if not numero:
        print("❌ Número vacío")
        return PlainTextResponse("OK")

    usuario = obtener_usuario(numero)
    estado = usuario["estado"]

    info = interpretar(mensaje)

    print(f"estado {estado} | numero: {numero}")

    # ---------- INICIO ----------
    if estado == "INICIO":

        enviar_texto(
            numero,
            "Hola 👋 Gracias por escribir a Inmobiliaria Sierra.\n"
            "¿Buscas casa o apartamento?"
        )

        actualizar_estado(numero, "TIPO")

        return PlainTextResponse("OK")

    # ---------- TIPO ----------
    elif estado == "TIPO":

        if not info.get("tipo"):
            enviar_texto(numero, "¿Buscas casa o apartamento? 😊")
            return PlainTextResponse("OK")

        actualizar_datos(numero, tipo=info["tipo"])

        enviar_texto(
            numero,
            "Perfecto 👍 ¿Cuál es tu presupuesto máximo? 💰"
        )

        actualizar_estado(numero, "PRESUPUESTO")

    # ---------- PRESUPUESTO ----------
    elif estado == "PRESUPUESTO":

        numero_info = info.get("numero")

        if not numero_info:
            enviar_texto(numero, "Indícame el presupuesto en números 💵")
            return PlainTextResponse("OK")

        actualizar_datos(numero, presupuesto=numero_info)

        opciones = buscar_inmuebles(usuario["tipo"], numero_info)

        if not opciones:

            enviar_texto(
                numero,
                "😕 No encontré inmuebles con ese presupuesto."
            )

            actualizar_estado(numero, "INICIO")

            return PlainTextResponse("OK")

        usuario["opciones"] = opciones

        texto = "🏘️ *Opciones disponibles:*\n\n"

        for i, o in enumerate(opciones, 1):

            texto += f"{i}. {o['tipo'].title()} en {o['barrio']} - ${o['precio']}\n"

        texto += "\nEscribe el *número* de la opción que te interesa 😉"

        enviar_texto(numero, texto)

        actualizar_estado(numero, "SELECCION")

    # ---------- SELECCION ----------
    elif estado == "SELECCION":

        sel = info.get("numero")

        if not sel or sel > len(usuario["opciones"]):

            enviar_texto(numero, "Dime el número de la opción 😊")

            return PlainTextResponse("OK")

        actualizar_datos(numero, seleccion=sel)

        enviar_texto(
            numero,
            "¿Deseas ver *imágenes* del inmueble? 📸 (si / no)"
        )

        actualizar_estado(numero, "IMAGENES")

    # ---------- IMAGENES ----------
    elif estado == "IMAGENES":

        if info.get("afirmacion") == "si":

            inmueble = usuario["opciones"][usuario["seleccion"] - 1]

            if inmueble.get("img_1"):

                enviar_imagen(
                    numero,
                    inmueble["img_1"],
                    inmueble.get("descripcion", "")
                )

        enviar_texto(
            numero,
            "¿Deseas agendar una visita? 😊 (si / no)"
        )

        actualizar_estado(numero, "CONFIRMAR_AGENDA")

    # ---------- CONFIRMAR AGENDA ----------
    elif estado == "CONFIRMAR_AGENDA":

        if info.get("afirmacion") != "si":

            enviar_texto(numero, "Perfecto 👍 Quedo atento.")

            actualizar_estado(numero, "INICIO")

            return PlainTextResponse("OK")

        dias = generar_dias_disponibles()

        usuario["dias_disponibles"] = dias

        texto = "📅 *Días disponibles:*\n\n"

        for i, d in enumerate(dias, 1):

            texto += f"{i}. {d.strftime('%A %d de %B')}\n"

        texto += "\nEscribe el *número del día*"

        enviar_texto(numero, texto)

        actualizar_estado(numero, "AGENDAR_DIA")

    # ---------- AGENDAR DIA ----------
    elif estado == "AGENDAR_DIA":

        idx = info.get("numero")

        if not idx or idx > len(usuario["dias_disponibles"]):

            enviar_texto(numero, "Elige un número válido 😊")

            return PlainTextResponse("OK")

        fecha = usuario["dias_disponibles"][idx - 1]

        actualizar_datos(numero, fecha_seleccionada=fecha)

        horarios = generar_horarios(fecha)

        usuario["horarios_disponibles"] = horarios

        texto = f"⏰ Horarios para {fecha.strftime('%A %d de %B')}:\n\n"

        for i, h in enumerate(horarios, 1):

            texto += f"{i}. {h}\n"

        texto += "\nEscribe el *número del horario*"

        enviar_texto(numero, texto)

        actualizar_estado(numero, "AGENDAR_HORA")

    # ---------- AGENDAR HORA ----------
    elif estado == "AGENDAR_HORA":

        idx = info.get("numero")

        if not idx or idx > len(usuario["horarios_disponibles"]):

            enviar_texto(numero, "Elige un horario válido 😊")

            return PlainTextResponse("OK")

        hora = usuario["horarios_disponibles"][idx - 1]

        inmueble = usuario["opciones"][usuario["seleccion"] - 1]

        guardar_cita(
            telefono=numero,
            inmueble=f"{inmueble['tipo']} {inmueble['barrio']}",
            fecha=usuario["fecha_seleccionada"].strftime("%Y-%m-%d"),
            hora=hora,
            estado="pendiente"
        )

        enviar_texto(
            numero,
            f"✅ Visita agendada para el {usuario['fecha_seleccionada'].strftime('%d/%m')} "
            f"a las {hora}.\nUn asesor la confirmará 😊"
        )

        actualizar_estado(numero, "INICIO")

    return PlainTextResponse("OK")