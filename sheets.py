# sheets.py
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SHEET_ID = "1-hW8cJP-o7AtAuShtyuA16J03L7gj15Lppt-WUcTqdA"

def obtener_hoja():
    creds_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        creds_info,
        scopes=scopes
    )

    client = gspread.authorize(credentials)
    sheet = client.open_by_key(SHEET_ID)
    return sheet.sheet1

def guardar_cita(telefono, inmueble, fecha, hora, estado="pendiente"):
    hoja = obtener_hoja()
    hoja.append_row([
        telefono,
        inmueble,
        fecha,
        hora,
        estado,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])
