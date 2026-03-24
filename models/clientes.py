from database.mongo_db import obtener_todos, insertar, actualizar, eliminar_logico
from datetime import datetime

COLECCION = "clientes"


def _next_id():
    clientes = obtener_todos(COLECCION)
    return max((c.get("id", 0) for c in clientes), default=0) + 1


def limpiar_telefono(tel):
    return tel.replace(" ", "").replace("-", "").replace("+", "")


def crear_cliente(nombre, telefono, direccion, notas):
    telefono = limpiar_telefono(telefono)

    nuevo = {
        "id": _next_id(),
        "nombre": nombre.strip(),
        "telefono": telefono,
        "direccion": direccion.strip(),
        "notas": notas.strip(),
        "activo": True,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d")
    }

    insertar(COLECCION, nuevo)

def cliente_duplicado(nombre, telefono):
    telefono = limpiar_telefono(telefono)
    clientes = obtener_todos(COLECCION)

    for c in clientes:
        if not c.get("activo", True):
            continue

        nombre_db = c.get("nombre", "").strip().lower()
        telefono_db = limpiar_telefono(c.get("telefono", ""))

        if nombre_db == nombre.strip().lower():
            return True

        if telefono_db == telefono:
            return True

    return False


def obtener_clientes(activos_only=True):
    clientes = obtener_todos(COLECCION)

    if activos_only:
        clientes = [c for c in clientes if c.get("activo", True)]

    return clientes


def actualizar_cliente(id_cliente, datos):
    if "telefono" in datos:
        datos["telefono"] = limpiar_telefono(datos["telefono"])

    actualizar(COLECCION, {"id": int(id_cliente)}, datos)


def eliminar_cliente(id_cliente):
    eliminar_logico(COLECCION, {"id": int(id_cliente)})