import streamlit as st

from models.clientes import obtener_clientes
from models.productos import obtener_productos_activos
from models.ordenes import (
    obtener_ordenes,
    crear_orden,
    actualizar_orden,
    desactivar_orden
)


# =========================
# HELPERS
# =========================
def safe_num(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


def recalcular(orden):

    subtotal = 0
    costo_total = 0

    for p in orden["productos"]:
        precio   = safe_num(p.get("precio"))
        cantidad = int(safe_num(p.get("cantidad")))
        subtotal    += precio * cantidad
        costo_total += safe_num(p.get("costo")) * cantidad

    total    = subtotal + safe_num(orden.get("gasto_extra"))
    ganancia = total - costo_total

    orden["subtotal"] = round(subtotal, 2)
    orden["total"]    = round(total, 2)
    orden["ganancia"] = round(ganancia, 2)

    return orden


def mostrar_ticket(orden):

    ganancia = safe_num(orden.get("ganancia"))

    col_id, col_cliente = st.columns([1, 2])
    col_id.markdown(f"**🧾 Orden #{orden['id']}** · {orden.get('fecha', '')}")
    col_cliente.markdown(f"👤 **{orden.get('cliente', '')}**")

    if orden["productos"]:
        filas = []
        for p in orden["productos"]:
            cantidad = int(p.get("cantidad", 1))
            precio   = safe_num(p.get("precio"))
            filas.append({
                "Producto": p.get("producto", ""),
                "Cant":     cantidad,
                "Precio":   f"${precio:.2f}",
                "Total":    f"${precio * cantidad:.2f}"
            })
        st.table(filas)
    else:
        st.caption("Sin productos")

    col1, col2, col3 = st.columns(3)
    col1.metric("Subtotal", f"${orden.get('subtotal', 0):.2f}")
    col2.metric("Total",    f"${orden.get('total', 0):.2f}")
    col3.metric("Ganancia", f"${ganancia:.2f}")


# =========================
# UI PRINCIPAL
# =========================
def ordenes_ui():

    st.title("🧾 Órdenes")

    # 👇 CAMBIO: inicializar set de ids borrados
    if "ids_borrados" not in st.session_state:
        st.session_state.ids_borrados = set()

    clientes  = obtener_clientes()
    productos = obtener_productos_activos()

    if not clientes or not productos:
        st.warning("⚠️ Necesitas clientes y productos para crear órdenes.")
        return

    tab1, tab2 = st.tabs(["🗂️ Pendientes", "➕ Nueva orden"])

    # =========================
    # TAB 1 — PENDIENTES
    # =========================
    with tab1:

        ordenes = obtener_ordenes()

        borradores = [
            o for o in ordenes
            if o.get("estado_general") == "borrador"
            and o.get("activo", True)
            and o["id"] not in st.session_state.ids_borrados  # 👈 CAMBIO: filtro local
        ]

        st.markdown("### 🗂️ Órdenes pendientes")

        if not borradores:
            st.info("No hay órdenes en borrador.")
        else:
            for o in borradores:
                with st.container(border=True):
                    mostrar_ticket(o)

                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        if st.button("✏️ Editar", key=f"edit_{o['id']}"):
                            st.session_state.orden_actual = o
                            st.rerun()

                    with col2:
                        if st.button("✅ Confirmar", key=f"confirm_{o['id']}"):
                            o["estado_general"] = "confirmada"
                            actualizar_orden(o)
                            st.success(f"Orden #{o['id']} confirmada")
                            st.rerun()

                    with col3:
                        if st.button("🗑️", key=f"delete_{o['id']}"):
                            st.session_state.ids_borrados.add(o["id"])  # 👈 CAMBIO: oculta inmediatamente
                            desactivar_orden(o["id"])
                            st.rerun()

    # =========================
    # TAB 2 — NUEVA ORDEN
    # =========================
    with tab2:

        st.markdown("### ➕ Crear nueva orden")

        if "orden_actual" not in st.session_state:
            st.session_state.orden_actual = None

        cliente = st.selectbox(
            "Cliente",
            clientes,
            format_func=lambda x: x["nombre"]
        )

        # Solo crear la orden cuando el usuario lo pide explícitamente
        if st.session_state.orden_actual is None:
            if st.button("🆕 Iniciar orden"):
                st.session_state.orden_actual = crear_orden(cliente["nombre"])
                st.rerun()

        elif st.session_state.orden_actual["cliente"] != cliente["nombre"]:
            # Si cambió el cliente, avisar y ofrecer reiniciar
            st.warning("⚠️ El cliente seleccionado cambió. ¿Deseas cancelar la orden actual e iniciar una nueva?")
            if st.button("🔄 Nueva orden para este cliente"):
                desactivar_orden(st.session_state.orden_actual["id"])
                st.session_state.orden_actual = crear_orden(cliente["nombre"])
                st.rerun()

        else:
            orden = st.session_state.orden_actual

            st.caption(f"Orden #{orden['id']}")

            # =========================
            # AGREGAR PRODUCTO
            # =========================
            with st.container(border=True):

                st.markdown("#### ➕ Agregar producto")

                col1, col2, col3 = st.columns(3)

                with col1:
                    producto = st.selectbox(
                        "Producto",
                        productos,
                        format_func=lambda x: x["nombre"]
                    )

                with col2:
                    cantidad = st.number_input("Cantidad", 1, 100, 1)

                with col3:
                    precio = st.number_input(
                        "Precio",
                        0.0,
                        10000.0,
                        float(producto["precio_sugerido"])
                    )

                if st.button("➕ Agregar"):
                    orden["productos"].append({
                        "producto": producto["nombre"],
                        "cantidad": cantidad,
                        "precio":   precio,
                        "costo":    producto["costo_base"]
                    })
                    orden = recalcular(orden)
                    actualizar_orden(orden)
                    st.rerun()

            # =========================
            # LISTA PRODUCTOS
            # =========================
            if orden["productos"]:

                st.markdown("### 🛒 Productos")

                for i, p in enumerate(orden["productos"]):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.write(f"{p['producto']} — {p['cantidad']} x ${p['precio']}")
                    with col2:
                        if st.button("❌", key=f"del_{i}"):
                            orden["productos"].pop(i)
                            orden = recalcular(orden)
                            actualizar_orden(orden)
                            st.rerun()

            # =========================
            # TOTALES
            # =========================
            orden = recalcular(orden)
            actualizar_orden(orden)

            if orden["productos"]:
                st.markdown("### 🧾 Vista previa")
                with st.container(border=True):
                    mostrar_ticket(orden)

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Confirmar orden"):
                    orden["estado_general"] = "confirmada"
                    actualizar_orden(orden)
                    st.session_state.orden_actual = None
                    st.success("Orden confirmada")
                    st.rerun()

            with col2:
                if st.button("🗑️ Cancelar"):
                    desactivar_orden(orden["id"])
                    st.session_state.orden_actual = None
                    st.rerun()
