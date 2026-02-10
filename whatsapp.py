import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
    SILENT_MODE
)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

TEMPLATE_INICIO = os.getenv("TWILIO_TEMPLATE_INICIO")

def enviar_template_inicio(numero):
    if not TEMPLATE_INICIO:
        print("❌ TEMPLATE_INICIO no definido")
        return

    print(f"📨 Enviando template {TEMPLATE_INICIO} a {numero}")

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        content_sid=TEMPLATE_INICIO
    )

def enviar_texto(numero, mensaje):
    if SILENT_MODE:
        print(f"[SILENT MODE] TEXTO a {numero}: {mensaje}")
        return

    try:
        client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{numero}",
            body=mensaje
        )
    except TwilioRestException as e:
        print(f"[Twilio error] {e}")

def enviar_imagen(numero, url, caption=None):
    if SILENT_MODE:
        print(f"[SILENT MODE] IMAGEN a {numero}: {url}")
        return

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        media_url=[url],
        body=caption or ""
    )
