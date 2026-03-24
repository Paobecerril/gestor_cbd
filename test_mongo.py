from database.mongo_db import insertar, obtener_todos

# insertar prueba
insertar("clientes", {"id": 1, "nombre": "Prueba Mongo", "activo": True})

# leer
clientes = obtener_todos("clientes")

print(clientes)

