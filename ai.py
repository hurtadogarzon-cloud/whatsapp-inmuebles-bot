# ai.py
import re

def interpretar(mensaje):
    data = {}
    mensaje = mensaje.lower()

    # Tipo de inmueble
    if "apartamento" in mensaje:
        data["tipo"] = "apartamento"
    elif "casa" in mensaje:
        data["tipo"] = "casa"

    # Números (presupuesto o selección)
    numeros = re.findall(r"\d+", mensaje.replace(".", ""))
    if numeros:
        valor = int(numeros[0])
        data["presupuesto"] = valor
        data["seleccion"] = valor

    # Afirmación
    if mensaje in ["si", "sí", "claro", "dale", "ok"]:
        data["afirmacion"] = "si"
    elif mensaje in ["no", "nop", "gracias"]:
        data["afirmacion"] = "no"

    return data













