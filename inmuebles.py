#inmuebles.py
from db import get_connection

def buscar_inmuebles(tipo, presupuesto):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT tipo, barrio, precio, descripcion, img_1
        FROM inmuebles
        WHERE tipo = %s AND precio <= %s
        ORDER BY precio ASC
        LIMIT 5
        """,
        (tipo, presupuesto)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    resultados = []

    for r in rows:
        resultados.append({
            "tipo": r[0],
            "barrio": r[1],
            "precio": r[2],
            "descripcion": r[3],
            "img_1": r[4]
        })

    return resultados
