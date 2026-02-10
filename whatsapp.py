import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER
)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

TEMPLATE_INICIO = os.getenv("TWILIO_TEMPLATE_INICIO")



def enviar_template_inicio(numero):
    print("📤 Enviando template a:", numero)
    print("📄 TEMPLATE:", TEMPLATE_INICIO)
    print("📞 FROM:", TWILIO_WHATSAPP_NUMBER)

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        content_sid=TEMPLATE_INICIO
    )


def enviar_texto(numero, mensaje):
    
    try:
        client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{numero}",
            body=mensaje
        )
    except TwilioRestException as e:
        print(f"[Twilio error] {e}")

def enviar_imagen(numero, url, caption=None):

    client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=f"whatsapp:{numero}",
        media_url=[url],
        body=caption or ""
    )
