import streamlit as st
from models.ordenes import obtener_ordenes, actualizar_orden
from models.clientes import obtener_clientes


def entregas_ui():

    st.title("🚚 Entregas")

    clientes_lista = obtener_clientes()
    clientes_dict  = {c["nombre"]: c for c in clientes_lista}

    ordenes = [
        o for o in obtener_ordenes()
        if o.get("estado_general") == "confirmada" and o.get("activo", True)
    ]

    tabs    = st.tabs(["🟡 Pendientes", "🔵 En ruta", "🟢 Entregadas"])
    estados = ["pendiente", "en_ruta", "entregado"]

    etiquetas_boton = {
        "pendiente": "🚗 Marcar en ruta",
        "en_ruta":   "✅ Marcar como entregado"
    }

    for tab, estado in zip(tabs, estados):

        with tab:

            lista = [o for o in ordenes if o.get("estado_entrega") == estado]

            if not lista:
                st.info("Sin órdenes en este estado.")
                continue

            for o in lista:

                cliente_nombre = o.get("cliente", "")
                cliente_info   = clientes_dict.get(cliente_nombre, {})
                direccion      = cliente_info.get("direccion") or "Sin dirección registrada"
                telefono       = cliente_info.get("telefono", "")

                with st.container(border=True):

                    # Encabezado de la orden
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"**📦 Orden #{o['id']}** · 👤 **{cliente_nombre}**")
                    col2.markdown(f"💵 **${o.get('total', 0):,.2f}**")

                    # Datos de contacto y dirección
                    if telefono:
                        st.caption(f"📞 {telefono}")
                    st.caption(f"📍 {direccion}")

                    # Lista de productos
                    productos_texto = "  \n".join(
                        f"• {p.get('producto', '')} x {int(p.get('cantidad', 1))}"
                        for p in o.get("productos", [])
                    )
                    if productos_texto:
                        st.markdown(productos_texto)

                    # Alerta si no está pagado y está en ruta
                    if estado == "en_ruta" and o.get("estado_pago") == "pendiente":
                        st.warning(
                            f"💳 Orden **no pagada** — recuerda cobrar "
                            f"**${o.get('total', 0):,.2f}** al entregar."
                        )

                    # Nota de entrega
                    nota = st.text_input(
                        "📝 Nota de entrega (opcional)",
                        value=o.get("nota_entrega", ""),
                        placeholder="Ej: Dejar con el vecino, tocar el timbre...",
                        key=f"nota_{o['id']}"
                    )

                    if nota != o.get("nota_entrega", ""):
                        o["nota_entrega"] = nota
                        actualizar_orden(o)

                    # Botón de avance de estado
                    if estado in etiquetas_boton:
                        if st.button(
                            etiquetas_boton[estado],
                            key=f"next_{o['id']}"
                        ):
                            if estado == "pendiente":
                                o["estado_entrega"] = "en_ruta"
                            elif estado == "en_ruta":
                                o["estado_entrega"] = "entregado"

                            actualizar_orden(o)
                            st.rerun()