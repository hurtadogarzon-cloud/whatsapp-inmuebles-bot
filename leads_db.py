#leads_db.py

from db import get_connection

def guardar_lead(telefono, interes, presupuesto):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO leads (telefono, nombre, interes, presupuesto, estado)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            telefono,
            "cliente_whatsapp",
            interes,
            presupuesto,
            "nuevo"
        )
    )

    conn.commit()

    cursor.close()
    conn.close()