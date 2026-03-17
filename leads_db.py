#leads_db.py

from db import get_connection

def guardar_lead(telefono, interes, presupuesto):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO leads (telefono, nombre, interes, presupuesto, estado)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (telefono)
            DO UPDATE SET
                interes = EXCLUDED.interes,
                presupuesto = EXCLUDED.presupuesto
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

    except Exception as e:
        print("❌ ERROR GUARDANDO LEAD:", e)

    cursor.close()
    conn.close()