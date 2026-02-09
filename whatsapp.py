# whatsapp.py
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
    SILENT_MODE
)

# Cliente Twilio (una sola vez)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Template SID (WhatsApp Meta)
TEMPLATE_INICIO = os.getenv("TWILIO_TEMPLATE_INICIO")


def enviar_template_inicio(numero):
    if SILENT_MODE:
        print(f"[SILENT MODE] TEMPLATE a {numero}")
        return

    if not TEMPLATE_INICIO:
        print("❌ TEMPLATE_INICIO no está definido")
        return

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        content_sid=TEMPLATE_INICIO
    )


def enviar_texto(numero, mensaje, usar_template_si_falla=True):
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

        if usar_template_si_falla:
            print("➡️ Enviando template de inicio como fallback")
            enviar_template_inicio(numero)


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
