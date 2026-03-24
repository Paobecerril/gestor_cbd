from database.mongo_db import obtener_todos, insertar
from datetime import datetime

COLECCION = "gastos"


def _next_id():
    gastos = obtener_todos(COLECCION)
    return max((g["id"] for g in gastos), default=0) + 1


def registrar_gasto(tipo, monto, descripcion, venta_id=None):
    """Registra un gasto, opcionalmente asociado a una venta."""
    nuevo_gasto = {
        "id": _next_id(),
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "tipo": tipo,
        "monto": float(monto),
        "descripcion": descripcion,
        "venta_id": venta_id
    }
    insertar(COLECCION, nuevo_gasto)
    return nuevo_gasto


def obtener_gastos():
    return obtener_todos(COLECCION)


def obtener_gastos_por_venta(venta_id):
    gastos = obtener_todos(COLECCION)
    return [g for g in gastos if g.get("venta_id") == venta_id]


def calcular_gastos_de_venta(venta_id):
    gastos = obtener_gastos_por_venta(venta_id)
    return sum(g["monto"] for g in gastos)