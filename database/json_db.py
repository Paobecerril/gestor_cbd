import json
import os

DATA_FOLDER = "data"


def cargar_json(nombre):

    ruta = os.path.join(DATA_FOLDER, nombre)

    if not os.path.exists(ruta):
        return []

    with open(ruta, "r") as f:
        return json.load(f)


def guardar_json(nombre, data):

    ruta = os.path.join(DATA_FOLDER, nombre)

    with open(ruta, "w") as f:
        json.dump(data, f, indent=4)