# ai.py
import re

def interpretar(mensaje):
    data = {}
    mensaje = mensaje.lower().strip()

    # Tipo de inmueble
    if "apartamento" in mensaje:
        data["tipo"] = "apartamento"
    elif "casa" in mensaje:
        data["tipo"] = "casa"

    # Números (presupuesto, selección día u hora)
    numeros = re.findall(r"\d+", mensaje.replace(".", ""))
    if numeros:
        data["numero"] = int(numeros[0])

    # Afirmación
    if mensaje in ["si", "sí", "claro", "dale", "ok", "de una"]:
        data["afirmacion"] = "si"
    elif mensaje in ["no", "nop", "ninguno", "ninguna"]:
        data["afirmacion"] = "no"

    return data
