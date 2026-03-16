# ai.py
# ai.py
import re

def interpretar(mensaje):

    data = {}

    # ---------- LIMPIEZA DEL MENSAJE ----------
    mensaje = mensaje.lower()
    mensaje = mensaje.replace("\xa0", " ")
    mensaje = " ".join(mensaje.split())
    mensaje = mensaje.replace(".", "")

    # ---------- TIPO DE INMUEBLE ----------
    if any(p in mensaje for p in ["apartamento", "apto", "apart", "apt"]):
        data["tipo"] = "apartamento"

    elif "casa" in mensaje:
        data["tipo"] = "casa"

    # ---------- NUMEROS ----------
    numeros = re.findall(r"\d+", mensaje)

    if numeros:
        data["numero"] = int(numeros[0])

    # ---------- AFIRMACIONES ----------
    afirmaciones = [
        "si", "sí", "claro", "dale", "ok", "de una",
        "obvio", "listo", "perfecto"
    ]

    negativos = [
        "no", "nop", "ninguno", "ninguna",
        "no gracias", "negativo"
    ]

    if mensaje in afirmaciones:
        data["afirmacion"] = "si"

    elif mensaje in negativos:
        data["afirmacion"] = "no"

    return data
