# whatsapp.py
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
    SILENT_MODE
)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_texto(numero, mensaje):
    if SILENT_MODE:
        print(f"[SILENT MODE] No se envía a {numero}: {mensaje}")
        return

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        body=mensaje
    )


def enviar_imagen(numero, url, caption=None):
    if SILENT_MODE:
        print(f"[SILENT MODE] No se envía imagen a {numero}: {url}")
        return

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        media_url=[url],
        body=caption or ""
    )







"""
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER
)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_texto(numero, mensaje):
    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        body=mensaje
    )

def enviar_imagen(numero, url, caption=None):
    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        media_url=[url],
        body=caption or ""
    )
"""