import streamlit as st
import pandas as pd

from models.productos import (
    crear_producto,
    obtener_productos,
    obtener_productos_activos,
    actualizar_producto,
    eliminar_producto,
    producto_duplicado
)

# =========================
# VALIDACIONES
# =========================
def texto_valido(texto):
    return texto and texto.strip() != ""


def productos_ui():

    st.title("📦 Gestión de Productos")

    # ── Mensaje persistente tras rerun ──────────────
    if st.session_state.get("msg_productos"):
        tipo, texto = st.session_state.msg_productos
        if tipo == "success":
            st.success(texto)
        elif tipo == "warning":
            st.warning(texto)
        elif tipo == "error":
            st.error(texto)
        st.session_state.msg_productos = None

    productos_activos = obtener_productos_activos()

    tab1, tab2, tab3 = st.tabs([
        "📋 Catálogo",
        "✏️ Editar / desactivar",
        "➕ Nuevo producto"
    ])

    # =========================
    # TAB 1 — CATÁLOGO
    # =========================
    with tab1:

        if not productos_activos:
            st.info("Todavía no hay productos activos.")
        else:
            df = pd.DataFrame(productos_activos)
            st.dataframe(df, use_container_width=True)

    # =========================
    # TAB 2 — EDITAR / DESACTIVAR
    # =========================
    with tab2:

        if not productos_activos:
            st.warning("Primero crea un producto en la pestaña ➕")
        else:

            producto = st.selectbox(
                "Seleccionar producto",
                productos_activos,
                format_func=lambda x: x["nombre"]
            )

            nombre      = st.text_input("Nombre *",      producto["nombre"])
            tipo        = st.text_input("Tipo *",        producto["tipo"])
            tamano      = st.text_input("Tamaño",        producto["tamano"])

            precio = st.number_input(
                "Precio sugerido *",
                min_value=0.0,
                max_value=10000.0,
                value=float(producto["precio_sugerido"])
            )

            costo = st.number_input(
                "Costo base *",
                min_value=0.0,
                max_value=10000.0,
                value=float(producto["costo_base"])
            )

            descripcion = st.text_area("Descripción", producto["descripcion"])

            col1, col2 = st.columns(2)

            # ── Actualizar ──────────────────────────
            with col1:
                if st.button("💾 Guardar cambios", key="btn_actualizar_producto"):

                    errores = []

                    if not texto_valido(nombre):
                        errores.append("El nombre es obligatorio.")

                    if not texto_valido(tipo):
                        errores.append("El tipo es obligatorio.")

                    if precio <= 0:
                        errores.append("El precio debe ser mayor a $0.")

                    if costo > precio:
                        errores.append("El costo no puede ser mayor al precio.")

                    if errores:
                        for e in errores:
                            st.error(e)
                    else:
                        actualizar_producto(
                            producto["id"],
                            nombre, tipo, tamano, precio, costo, descripcion
                        )
                        st.session_state.msg_productos = (
                            "success", "✅ Producto actualizado correctamente."
                        )
                        st.rerun()

            # ── Desactivar con doble confirmación ───
            with col2:

                confirm_key = f"confirmar_baja_producto_{producto['id']}"

                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                if not st.session_state[confirm_key]:

                    if st.button(
                        "🚫 Desactivar producto",
                        key=f"btn_deact_prod_{producto['id']}"
                    ):
                        st.session_state[confirm_key] = True
                        st.rerun()

                else:
                    st.warning(
                        f"⚠️ ¿Segura que quieres desactivar "
                        f"**{producto['nombre']}**?"
                    )
                    c1, c2 = st.columns(2)

                    with c1:
                        if st.button(
                            "✅ Sí, desactivar",
                            key=f"btn_si_prod_{producto['id']}"
                        ):
                            eliminar_producto(producto["id"])
                            st.session_state[confirm_key] = False
                            st.session_state.msg_productos = (
                                "warning",
                                f"⚠️ Producto '{producto['nombre']}' desactivado."
                            )
                            st.rerun()

                    with c2:
                        if st.button(
                            "❌ Cancelar",
                            key=f"btn_no_prod_{producto['id']}"
                        ):
                            st.session_state[confirm_key] = False
                            st.rerun()

    # =========================
    # TAB 3 — NUEVO PRODUCTO
    # =========================
    with tab3:

        st.markdown("Llena los datos del nuevo producto:")

        nombre      = st.text_input("Nombre *",   key="np_nombre")
        tipo        = st.text_input("Tipo *",      key="np_tipo")
        tamano      = st.text_input("Tamaño",      key="np_tamano")

        precio = st.number_input(
            "Precio sugerido *",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            key="np_precio"
        )

        costo = st.number_input(
            "Costo base *",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            key="np_costo"
        )

        descripcion = st.text_area("Descripción", max_chars=200, key="np_desc")

        if st.button("➕ Crear producto", key="btn_crear_producto"):

            errores = []

            if not texto_valido(nombre):
                errores.append("El nombre es obligatorio.")

            if not texto_valido(tipo):
                errores.append("El tipo es obligatorio.")

            if precio <= 0:
                errores.append("El precio debe ser mayor a $0.")

            if costo > precio:
                errores.append("El costo no puede ser mayor al precio.")

            # Validación anti-duplicados
            if texto_valido(nombre):
                if producto_duplicado(nombre):
                    errores.append(
                        "⚠️ Ya existe un producto con ese nombre. "
                        "Revisa el catálogo en la pestaña 📋 antes de crear uno nuevo."
                    )

            if errores:
                for e in errores:
                    st.error(e)
            else:
                crear_producto(nombre, tipo, tamano, precio, costo, descripcion)
                st.session_state.msg_productos = (
                    "success", "✅ ¡Producto guardado con éxito!"
                )
                st.balloons()
                st.rerun()