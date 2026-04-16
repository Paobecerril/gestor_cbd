from database.mongo_db import obtener_todos, insertar, reemplazar, eliminar_logico
from datetime import datetime

COLECCION = "ordenes"


def _next_id():
    ordenes = obtener_todos(COLECCION)
    return max((o["id"] for o in ordenes), default=0) + 1


def obtener_ordenes(activos_only=True):
    ordenes = obtener_todos(COLECCION)
    if activos_only:
        return [o for o in ordenes if o.get("activo", True)]
    return ordenes


def crear_orden(cliente):
    nueva = {
        "id": _next_id(),
        "cliente": cliente,
        "fecha": datetime.now().strftime("%Y-%m-%d"),

        "productos": [],

        "subtotal": 0,
        "descuento_global": 0,
        "tipo_descuento_global": "ninguno",
        "gasto_extra": 0,
        "total": 0,
        "ganancia": 0,

        "estado_pago": "pendiente",
        "estado_entrega": "pendiente",
        "estado_general": "borrador",

        "activo": True
    }
    insertar(COLECCION, nueva)
    return nueva


def actualizar_orden(orden_actualizada):
    """
    Reemplaza el documento completo de la orden.
    Se usa reemplazar() en lugar de actualizar() porque la orden
    contiene listas anidadas (productos) que deben guardarse enteras.
    """
    reemplazar(COLECCION, {"id": orden_actualizada["id"]}, orden_actualizada)


def desactivar_orden(id_orden):
    eliminar_logico(COLECCION, {"id": id_orden})