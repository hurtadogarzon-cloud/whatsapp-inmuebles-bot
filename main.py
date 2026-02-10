# main.py
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime, timedelta

from estados import obtener_usuario
from ai import interpretar
from inmuebles import buscar_inmuebles
from whatsapp import (
    enviar_texto,
    enviar_imagen,
    enviar_template_inicio   # 👈 IMPORT CLAVE
)
from sheets import guardar_cita

app = FastAPI()

# ---------- UTILIDADES ----------
def generar_dias_disponibles(cantidad=10):
    dias = []
    fecha = datetime.now()

    while len(dias) < cantidad:
        fecha += timedelta(days=1)
        if fecha.weekday() <= 5:  # lunes a sábado
            dias.append(fecha)
    return dias

def generar_horarios(fecha):
    if fecha.weekday() <= 4:  # lunes a viernes
        return [f"{h}:00" for h in range(8, 18)]
    else:  # sábado
        return [f"{h}:00" for h in range(8, 17)]

# ---------- WEBHOOK ----------
@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()

    mensaje = form.get("Body", "").lower()
    numero = form.get("From", "").replace("whatsapp:", "")

    usuario = obtener_usuario(numero)
    estado = usuario["estado"]
    info = interpretar(mensaje)

    # ---------- INICIO ----------
    if estado == "INICIO":
        if usuario.get("ya_iniciado"):
            enviar_texto(numero, "Hola 😊 ¿En qué te ayudo hoy?")
        else:
            enviar_template_inicio(numero)
            usuario["ya_iniciado"] = True

        usuario["estado"] = "TIPO"
        return PlainTextResponse("OK")


    # ---------- TIPO ----------
    elif estado == "TIPO":
        if not info.get("tipo"):
            enviar_texto(numero, "¿Buscas casa o apartamento? 😊")
            return PlainTextResponse("OK")

        usuario["tipo"] = info["tipo"]
        enviar_texto(numero, "Perfecto 👍 ¿Cuál es tu presupuesto máximo? 💰")
        usuario["estado"] = "PRESUPUESTO"

    # ---------- PRESUPUESTO ----------
    elif estado == "PRESUPUESTO":
        numero_info = info.get("numero")

        if not numero_info:
            enviar_texto(numero, "Indícame el presupuesto en números 💵")
            return PlainTextResponse("OK")

        usuario["presupuesto"] = numero_info
        opciones = buscar_inmuebles(usuario["tipo"], numero_info)

        if not opciones:
            enviar_texto(numero, "😕 No encontré inmuebles con ese presupuesto.")
            usuario["estado"] = "INICIO"
            return PlainTextResponse("OK")

        usuario["opciones"] = opciones

        texto = "🏘️ *Opciones disponibles:*\n\n"
        for i, o in enumerate(opciones, 1):
            texto += f"{i}. {o['tipo'].title()} en {o['barrio']} - ${o['precio']}\n"

        texto += "\nEscribe el *número* de la opción que te interesa 😉"
        enviar_texto(numero, texto)
        usuario["estado"] = "SELECCION"

    # ---------- SELECCIÓN ----------
    elif estado == "SELECCION":
        sel = info.get("numero")

        if not sel or sel > len(usuario["opciones"]):
            enviar_texto(numero, "Dime el número de la opción 😊")
            return PlainTextResponse("OK")

        usuario["seleccion"] = sel
        enviar_texto(numero, "¿Deseas ver *imágenes* del inmueble? 📸 (si / no)")
        usuario["estado"] = "IMAGENES"

    # ---------- IMÁGENES ----------
    elif estado == "IMAGENES":
        if info.get("afirmacion") == "si":
            inmueble = usuario["opciones"][usuario["seleccion"] - 1]
            if inmueble.get("img_1"):
                enviar_imagen(
                    numero,
                    inmueble["img_1"],
                    inmueble.get("descripcion", "")
                )

        enviar_texto(numero, "¿Deseas agendar una visita? 😊 (si / no)")
        usuario["estado"] = "CONFIRMAR_AGENDA"

    # ---------- CONFIRMAR AGENDA ----------
    elif estado == "CONFIRMAR_AGENDA":
        if info.get("afirmacion") != "si":
            enviar_texto(numero, "Perfecto 👍 Quedo atento.")
            usuario["estado"] = "INICIO"
            return PlainTextResponse("OK")

        dias = generar_dias_disponibles()
        usuario["dias_disponibles"] = dias

        texto = "📅 *Días disponibles:*\n\n"
        for i, d in enumerate(dias, 1):
            texto += f"{i}. {d.strftime('%A %d de %B')}\n"

        texto += "\nEscribe el *número del día*"
        enviar_texto(numero, texto)
        usuario["estado"] = "AGENDAR_DIA"

    # ---------- AGENDAR DÍA ----------
    elif estado == "AGENDAR_DIA":
        idx = info.get("numero")

        if not idx or idx > len(usuario["dias_disponibles"]):
            enviar_texto(numero, "Elige un número válido 😊")
            return PlainTextResponse("OK")

        fecha = usuario["dias_disponibles"][idx - 1]
        usuario["fecha_seleccionada"] = fecha

        horarios = generar_horarios(fecha)
        usuario["horarios_disponibles"] = horarios

        texto = f"⏰ Horarios para {fecha.strftime('%A %d de %B')}:\n\n"
        for i, h in enumerate(horarios, 1):
            texto += f"{i}. {h}\n"

        texto += "\nEscribe el *número del horario*"
        enviar_texto(numero, texto)
        usuario["estado"] = "AGENDAR_HORA"

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

        usuario["estado"] = "INICIO"

    return PlainTextResponse("OK")
