#inmuebles.py
import pandas as pd

df = pd.read_excel("inmuebles.xlsx")

def buscar_inmuebles(tipo, presupuesto):
    filtrado = df[
        (df["tipo"] == tipo) &
        (df["precio"] <= presupuesto)
    ]
    return filtrado.to_dict(orient="records")

