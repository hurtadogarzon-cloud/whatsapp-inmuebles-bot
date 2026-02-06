from sheets import guardar_cita
from fastapi import FastAPI, Request

from fastapi.responses import PlainTextResponse

from estados import obtener_usuario
from ai import interpretar
from inmuebles import buscar_inmuebles
from whatsapp import enviar_texto

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        form = await request.form()
    except Exception as e:
        print("Error leyendo form:", e)
        return PlainTextResponse("OK", status_code=200)
    
    

    mensaje = form.get("Body", "").lower()
    numero = form.get("From", "").replace("whatsapp:", "")

    usuario = obtener_usuario(numero)
    estado = usuario["estado"]

    info = interpretar(mensaje)

    # INICIO
    if estado == "INICIO":
        enviar_texto(
            numero,
            "¡Hola! 👋 ¿Buscas *casa* o *apartamento*? 🏠"
        )
        usuario["estado"] = "TIPO"

    # TIPO
    elif estado == "TIPO":
        if not info.get("tipo"):
            enviar_texto(numero, "¿Buscas casa o apartamento? 😊")
            return PlainTextResponse("OK", status_code=200)

        usuario["tipo"] = info["tipo"]
        enviar_texto(
            numero,
            "Perfecto 👍 ¿Cuál es tu presupuesto máximo? 💰"
        )
        usuario["estado"] = "PRESUPUESTO"

    # PRESUPUESTO
    elif estado == "PRESUPUESTO":
        if not info.get("presupuesto"):
            enviar_texto(numero, "Indícame el presupuesto en números 💵")
            return PlainTextResponse("OK", status_code=200)

        usuario["presupuesto"] = info["presupuesto"]

        resultados = buscar_inmuebles(
            usuario["tipo"],
            usuario["presupuesto"]
        )

        if not resultados:
            enviar_texto(
                numero,
                "😕 No encontré inmuebles con ese presupuesto."
            )
            usuario["estado"] = "INICIO"
            return PlainTextResponse("OK", status_code=200)

        usuario["opciones"] = resultados

        mensaje_opciones = "🏘️ *Opciones disponibles:*\n\n"
        for i, inm in enumerate(resultados, 1):
            mensaje_opciones += (
                f"{i}. {inm['tipo'].title()} en {inm['barrio']} "
                f"- ${inm['precio']}\n"
            )

        mensaje_opciones += "\nEscribe el *número* de la opción que te interesa 😉"

        enviar_texto(numero, mensaje_opciones)
        usuario["estado"] = "SELECCION"

    # SELECCION
    elif estado == "SELECCION":
        seleccion = info.get("seleccion")

        if not seleccion or seleccion > len(usuario["opciones"]):
            enviar_texto(numero, "Por favor dime el número de la opción 😊")
            return PlainTextResponse("OK", status_code=200)

        usuario["seleccion"] = seleccion

        enviar_texto(
            numero,
            "¡Excelente elección! 😄 ¿Deseas ver *imágenes* del inmueble? 📸 (si / no)"
        )
        usuario["estado"] = "IMAGENES"

    # IMAGENES
    elif estado == "IMAGENES":
        if info.get("afirmacion") == "si":
            inmueble = usuario["opciones"][usuario["seleccion"] - 1]

            from whatsapp import enviar_imagen

            #for campo in ["img_1", "img_2", "img_3"]:
            for campo in ["img_1"]:
                url = inmueble.get(campo)
                if url and isinstance(url, str):
                    enviar_imagen(
                        numero,
                        url,
                        inmueble.get("descripcion", "")
                    )

            enviar_texto(numero, "¿Deseas agendar una visita? 😊")

        else:
            enviar_texto(numero, "Perfecto 👍 Si deseas ver otra opción, dime.")

        usuario["estado"] = "INICIO"


    return PlainTextResponse("OK", status_code=200)

@app.get("/test-sheet")
def test_sheet():
    guardar_cita(
        telefono="3000000000",
        inmueble="Apartamento Chapinero",
        fecha="2026-02-06",
        hora="10:00",
        estado="prueba"
    )
    return {"ok": True}

