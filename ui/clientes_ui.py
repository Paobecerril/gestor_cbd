import streamlit as st
import pandas as pd

from models.clientes import (
    crear_cliente,
    obtener_clientes,
    actualizar_cliente,
    eliminar_cliente,
    cliente_duplicado
)

# =========================
# VALIDACIÓN TELÉFONO
# =========================
def telefono_valido(tel):
    tel = tel.replace(" ", "").replace("-", "").replace("+", "")
    return tel.isdigit() and len(tel) >= 8


def clientes_ui():

    st.title("👥 Gestión de Clientes")

    # ── Mensajes ─────────────
    if st.session_state.get("msg_clientes"):
        tipo, texto = st.session_state.msg_clientes

        if tipo == "success":
            st.success(texto)
        elif tipo == "warning":
            st.warning(texto)
        elif tipo == "error":
            st.error(texto)

        st.session_state.msg_clientes = None

    tab1, tab2, tab3 = st.tabs([
        "📋 Directorio",
        "✏️ Editar / desactivar",
        "➕ Nuevo cliente"
    ])

    # =========================
    # TAB 1 — DIRECTORIO
    # =========================
    with tab1:

        clientes = obtener_clientes()

        if not clientes:
            st.info("No hay clientes registrados.")
        else:

            busqueda = st.text_input("🔍 Buscar cliente")

            df = pd.DataFrame(clientes)

            for col in ["nombre", "telefono", "direccion"]:
                if col not in df.columns:
                    df[col] = ""

            df = df.astype(str)

            if busqueda:
                termino = busqueda.lower()

                df = df[
                    df["nombre"].str.lower().str.contains(termino, na=False) |
                    df["telefono"].str.lower().str.contains(termino, na=False) |
                    df["direccion"].str.lower().str.contains(termino, na=False)
                ]

            st.dataframe(df, use_container_width=True)

    # =========================
    # TAB 2 — EDITAR
    # =========================
    with tab2:

        clientes = obtener_clientes()

        if not clientes:
            st.warning("Primero crea un cliente.")
        else:

            cliente = st.selectbox(
                "Seleccionar cliente",
                clientes,
                format_func=lambda x: x.get("nombre", "Sin nombre")
            )

            nombre = st.text_input("Nombre", cliente.get("nombre", ""))
            telefono = st.text_input("Teléfono", cliente.get("telefono", ""))
            direccion = st.text_input("Dirección", cliente.get("direccion", ""))
            notas = st.text_area("Notas", cliente.get("notas", ""))

            col1, col2 = st.columns(2)

            # GUARDAR
            with col1:
                if st.button("💾 Guardar"):

                    errores = []

                    if not nombre.strip():
                        errores.append("Nombre obligatorio")

                    if not telefono_valido(telefono):
                        errores.append("Teléfono inválido")

                    if errores:
                        for e in errores:
                            st.error(e)
                    else:
                        actualizar_cliente(
                            cliente.get("id"),
                            {
                                "nombre": nombre,
                                "telefono": telefono,
                                "direccion": direccion,
                                "notas": notas
                            }
                        )

                        st.session_state.msg_clientes = ("success", "Cliente actualizado")
                        st.rerun()

            # ELIMINAR
            with col2:
                if st.button("🚫 Desactivar"):
                    eliminar_cliente(cliente.get("id"))
                    st.session_state.msg_clientes = ("warning", "Cliente desactivado")
                    st.rerun()

    # =========================
    # TAB 3 — NUEVO
    # =========================
    with tab3:

        nombre = st.text_input("Nombre *", key="nc_nombre")
        telefono = st.text_input("Teléfono *", key="nc_telefono")
        direccion = st.text_input("Dirección", key="nc_direccion")
        notas = st.text_area("Notas", key="nc_notas")

        if st.button("➕ Crear cliente"):

            errores = []

            if not nombre.strip():
                errores.append("Nombre obligatorio")

            if not telefono_valido(telefono):
                errores.append("Teléfono inválido")

            if nombre and telefono:
                if cliente_duplicado(nombre, telefono):
                    errores.append("Cliente duplicado")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                crear_cliente(nombre, telefono, direccion, notas)

                st.session_state.msg_clientes = ("success", "Cliente creado")
                st.balloons()
                st.rerun()