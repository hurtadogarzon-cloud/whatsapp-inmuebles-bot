# estados.py
from db import get_connection
from datetime import datetime

def _fila_a_dict(row):
    # row: (id, telefono, estado, tipo, presupuesto, seleccion, fecha_seleccionada)
    return {
        "id": row[0],
        "telefono": row[1],
        "estado": row[2],
        "tipo": row[3],
        "presupuesto": row[4],
        "seleccion": row[5],
        "fecha_seleccionada": row[6],
        # estos siguen siendo temporales en memoria de la request
        "opciones": [],
        "dias_disponibles": [],
        "horarios_disponibles": []
    }

def obtener_usuario(telefono):
    """
    Devuelve un dict compatible con tu main.py.
    Si no existe el usuario, lo crea con estado INICIO.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, telefono, estado, tipo, presupuesto, seleccion, fecha_seleccionada
        FROM usuarios
        WHERE telefono = %s
        """,
        (telefono,)
    )
    row = cursor.fetchone()

    if not row:
        cursor.execute(
            """
            INSERT INTO usuarios (telefono, estado)
            VALUES (%s, 'INICIO')
            RETURNING id, telefono, estado, tipo, presupuesto, seleccion, fecha_seleccionada
            """,
            (telefono,)
        )
        row = cursor.fetchone()
        conn.commit()

    cursor.close()
    conn.close()

    return _fila_a_dict(row)


def actualizar_estado(telefono, estado):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE usuarios SET estado = %s WHERE telefono = %s",
        (estado, telefono)
    )

    conn.commit()
    cursor.close()
    conn.close()


def actualizar_datos(telefono, **campos):
    """
    Permite actualizar tipo, presupuesto, seleccion, fecha_seleccionada
    ejemplo: actualizar_datos(numero, tipo="casa", presupuesto=200000000)
    """
    if not campos:
        return

    conn = get_connection()
    cursor = conn.cursor()

    columnas = []
    valores = []

    for k, v in campos.items():
        columnas.append(f"{k} = %s")
        valores.append(v)

    valores.append(telefono)

    query = f"""
        UPDATE usuarios
        SET {', '.join(columnas)}
        WHERE telefono = %s
    """

    cursor.execute(query, tuple(valores))
    conn.commit()

    cursor.close()
    conn.close()