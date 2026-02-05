#estados.py
usuarios = {}

def obtener_usuario(telefono):
    if telefono not in usuarios:
        usuarios[telefono] = {
            "estado": "INICIO",
            "tipo": None,
            "presupuesto": None,
            "opciones": [],
            "seleccion": None
        }
    return usuarios[telefono]


