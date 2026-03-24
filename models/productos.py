from database.mongo_db import obtener_todos, insertar, actualizar, eliminar_logico

COLECCION = "productos"


def _next_id():
    productos = obtener_todos(COLECCION)
    return max((p["id"] for p in productos), default=0) + 1


def crear_producto(nombre, tipo, tamano, precio, costo, descripcion):
    nuevo = {
        "id": _next_id(),
        "nombre": nombre,
        "tipo": tipo,
        "tamano": tamano,
        "precio_sugerido": precio,
        "costo_base": costo,
        "descripcion": descripcion,
        "activo": True
    }
    insertar(COLECCION, nuevo)


def producto_duplicado(nombre):
    """Retorna True si ya existe un producto activo con el mismo nombre."""
    productos = obtener_todos(COLECCION)
    for p in productos:
        if not p.get("activo", True):
            continue
        if p["nombre"].strip().lower() == nombre.strip().lower():
            return True
    return False


def obtener_productos():
    return obtener_todos(COLECCION)


def obtener_productos_activos():
    productos = obtener_todos(COLECCION)
    return [p for p in productos if p.get("activo", True)]


def actualizar_producto(id_producto, nombre, tipo, tamano, precio, costo, descripcion):
    actualizar(COLECCION, {"id": id_producto}, {
        "nombre": nombre,
        "tipo": tipo,
        "tamano": tamano,
        "precio_sugerido": precio,
        "costo_base": costo,
        "descripcion": descripcion
    })


def eliminar_producto(id_producto):
    eliminar_logico(COLECCION, {"id": id_producto})