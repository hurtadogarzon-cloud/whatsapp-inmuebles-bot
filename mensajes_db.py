# mensajes_db.py
from db import get_connection

def guardar_mensaje(telefono, direccion, mensaje):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO mensajes (telefono, direccion, mensaje)
        VALUES (%s, %s, %s)
        """,
        (telefono, direccion, mensaje)
    )

    conn.commit()

    cursor.close()
    conn.close()