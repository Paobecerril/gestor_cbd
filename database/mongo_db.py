from pymongo import MongoClient
import streamlit as st


# -------------------------------------------------
# CONEXIÓN CACHEADA — una sola conexión por sesión
# -------------------------------------------------
@st.cache_resource
def _get_client():
    """
    Crea el cliente de MongoDB una sola vez y lo reutiliza.
    Lee la URI desde st.secrets (Streamlit Cloud) o desde
    .streamlit/secrets.toml en local.
    """
    uri = st.secrets["MONGO_URI"]
    return MongoClient(uri)


def _get_db():
    return _get_client()["gestor_cbd"]


def get_collection(nombre):
    return _get_db()[nombre]


# -------------------------------------------------
# OPERACIONES CRUD
# -------------------------------------------------
def obtener_todos(nombre):
    """Devuelve todos los documentos de una colección (sin _id)."""
    col = get_collection(nombre)
    return list(col.find({}, {"_id": 0}))


def insertar(nombre, data):
    """Inserta un documento. Si tiene '_id' de Mongo previo, lo elimina."""
    data.pop("_id", None)
    col = get_collection(nombre)
    col.insert_one(data)


def actualizar(nombre, filtro, nuevos_datos):
    """Actualiza un documento con $set. Ignora el campo _id."""
    nuevos_datos.pop("_id", None)
    col = get_collection(nombre)
    col.update_one(filtro, {"$set": nuevos_datos})


def reemplazar(nombre, filtro, nuevo_documento):
    nuevo_documento.pop("_id", None)
    col = get_collection(nombre)
    col.replace_one(filtro, nuevo_documento)  # 👈 sin upsert=True


def eliminar_logico(nombre, filtro):
    """Soft-delete: marca TODOS los documentos que coincidan como inactivos."""
    col = get_collection(nombre)
    col.update_many(filtro, {"$set": {"activo": False}})  # 👈 update_many
