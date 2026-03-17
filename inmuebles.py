#inmuebles.py
from db import get_connection



def buscar_inmuebles(tipo, presupuesto):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, tipo, barrio, precio, descripcion
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
            "id": r[0],
            "tipo": r[1],
            "barrio": r[2],
            "precio": r[3],
            "descripcion": r[4]
        })

    return resultados



from db import get_connection

def obtener_imagenes(inmueble_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT url
        FROM inmueble_imagenes
        WHERE inmueble_id = %s
        ORDER BY orden
        """,
        (inmueble_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [r[0] for r in rows]