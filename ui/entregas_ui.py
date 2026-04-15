import streamlit as st
from models.ordenes import obtener_ordenes, actualizar_orden
from models.clientes import obtener_clientes


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _badge_pago(estado_pago: str) -> str:
    return "🟢 Pagado" if estado_pago == "pagado" else "🔴 No pagado"


def _render_editor(o: dict):
    """Expander para editar productos y total de una orden."""
    with st.expander("✏️ Editar orden", expanded=False):
        productos = o.get("productos", [])
        productos_editados = []
        cambios = False

        st.markdown("**Productos:**")
        for i, p in enumerate(productos):
            col_prod, col_cant, col_del = st.columns([3, 1, 0.5])
            nombre = col_prod.text_input(
                "Producto",
                value=p.get("producto", ""),
                key=f"edit_prod_{o['id']}_{i}",
                label_visibility="collapsed",
            )
            cantidad = col_cant.number_input(
                "Cant.",
                min_value=1,
                value=int(p.get("cantidad", 1)),
                key=f"edit_cant_{o['id']}_{i}",
                label_visibility="collapsed",
            )
            eliminar = col_del.button("🗑️", key=f"del_{o['id']}_{i}", help="Eliminar producto")

            if not eliminar:
                productos_editados.append({"producto": nombre, "cantidad": cantidad})
                if nombre != p.get("producto") or cantidad != int(p.get("cantidad", 1)):
                    cambios = True

        # Agregar producto nuevo
        if st.button("➕ Agregar producto", key=f"add_prod_{o['id']}"):
            productos_editados.append({"producto": "", "cantidad": 1})
            cambios = True

        # Editar total
        nuevo_total = st.number_input(
            "💵 Total ($)",
            min_value=0.0,
            value=float(o.get("total", 0)),
            step=10.0,
            format="%.2f",
            key=f"edit_total_{o['id']}",
        )
        if nuevo_total != float(o.get("total", 0)):
            cambios = True

        # Estado de pago editable
        opciones_pago = ["pendiente", "pagado"]
        idx_pago = opciones_pago.index(o.get("estado_pago", "pendiente"))
        nuevo_estado_pago = st.selectbox(
            "💳 Estado de pago",
            opciones_pago,
            index=idx_pago,
            key=f"edit_pago_{o['id']}",
            format_func=lambda x: "🔴 No pagado" if x == "pendiente" else "🟢 Pagado",
        )
        if nuevo_estado_pago != o.get("estado_pago"):
            cambios = True

        # Guardar cambios
        if st.button("💾 Guardar cambios", key=f"save_{o['id']}", type="primary"):
            o["productos"] = productos_editados
            o["total"] = nuevo_total
            o["estado_pago"] = nuevo_estado_pago
            actualizar_orden(o)
            st.success("✅ Orden actualizada correctamente.")
            st.rerun()

        if cambios:
            st.caption("⚠️ Tienes cambios sin guardar.")


def _render_tarjeta(o: dict, estado: str, clientes_dict: dict, etiquetas_boton: dict):
    """Renderiza una tarjeta completa de orden."""
    cliente_nombre = o.get("cliente", "")
    cliente_info   = clientes_dict.get(cliente_nombre, {})
    direccion      = cliente_info.get("direccion") or "Sin dirección registrada"
    telefono       = cliente_info.get("telefono", "")
    estado_pago    = o.get("estado_pago", "pendiente")

    with st.container(border=True):
        # ── Encabezado ──────────────────────────────
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        col1.markdown(f"**📦 Orden #{o['id']}** · 👤 **{cliente_nombre}**")
        col2.markdown(f"💵 **${o.get('total', 0):,.2f}**")
        col3.markdown(_badge_pago(estado_pago))

        # ── Contacto y dirección ─────────────────────
        if telefono:
            st.caption(f"📞 {telefono}")
        st.caption(f"📍 {direccion}")

        # ── Productos ────────────────────────────────
        productos_texto = "  \n".join(
            f"• {p.get('producto', '')} x {int(p.get('cantidad', 1))}"
            for p in o.get("productos", [])
        )
        if productos_texto:
            st.markdown(productos_texto)

        # ── Alerta de cobro ──────────────────────────
        if estado_pago == "pendiente":
            st.warning(
                f"💳 **No pagado** — recuerda cobrar **${o.get('total', 0):,.2f}** al entregar."
            )

        # ── Nota de entrega ──────────────────────────
        nota = st.text_input(
            "📝 Nota de entrega (opcional)",
            value=o.get("nota_entrega", ""),
            placeholder="Ej: Dejar con el vecino, tocar el timbre...",
            key=f"nota_{o['id']}",
        )
        if nota != o.get("nota_entrega", ""):
            o["nota_entrega"] = nota
            actualizar_orden(o)

        # ── Acciones ─────────────────────────────────
        col_btn1, col_btn2 = st.columns([2, 1])

        # Avanzar estado de entrega
        if estado in etiquetas_boton:
            if col_btn1.button(etiquetas_boton[estado], key=f"next_{o['id']}"):
                o["estado_entrega"] = "en_ruta" if estado == "pendiente" else "entregado"
                actualizar_orden(o)
                st.rerun()

        # Marcar como pagado (acceso rápido sin abrir editor)
        if estado_pago == "pendiente":
            if col_btn2.button("💳 Cobrar", key=f"cobrar_{o['id']}", help="Marcar como pagado"):
                o["estado_pago"] = "pagado"
                actualizar_orden(o)
                st.rerun()

        # Editor completo
        _render_editor(o)


# ─────────────────────────────────────────────
# VISTA PRINCIPAL
# ─────────────────────────────────────────────

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
        "en_ruta":   "✅ Marcar como entregado",
    }

    for tab, estado in zip(tabs, estados):
        with tab:
            lista = [o for o in ordenes if o.get("estado_entrega") == estado]

            if not lista:
                st.info("Sin órdenes en este estado.")
                continue

            # Resumen rápido del tab
            no_pagadas = sum(1 for o in lista if o.get("estado_pago") == "pendiente")
            total_tab  = sum(o.get("total", 0) for o in lista)
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Órdenes", len(lista))
            mc2.metric("Total", f"${total_tab:,.2f}")
            mc3.metric("🔴 Sin cobrar", no_pagadas)

            st.divider()

            for o in lista:
                _render_tarjeta(o, estado, clientes_dict, etiquetas_boton)
