import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from database.mongo_db import obtener_todos
from models.gastos import obtener_gastos
from models.ordenes import actualizar_orden
from services.finanzas_service import calcular_finanzas


# =========================
# HELPERS
# =========================
def safe_fecha(f):
    try:
        return datetime.strptime(f, "%Y-%m-%d")
    except Exception:
        return None


def filtrar_por_periodo(registros, periodo, campo_fecha="fecha"):
    hoy = datetime.now().date()
    if periodo == "todo":
        return registros
    resultado = []
    for r in registros:
        fecha = safe_fecha(r.get(campo_fecha, ""))
        if fecha is None:
            continue
        f = fecha.date()
        if periodo == "hoy" and f == hoy:
            resultado.append(r)
        elif periodo == "esta_semana":
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            if inicio_semana <= f <= hoy:
                resultado.append(r)
        elif periodo == "este_mes" and f.month == hoy.month and f.year == hoy.year:
            resultado.append(r)
    return resultado


def mostrar_dashboard():

    st.title("📊 Resumen del negocio")

    # =========================
    # FILTRO DE PERÍODO
    # =========================
    periodo = st.radio(
        "Ver datos de:",
        options=["hoy", "esta_semana", "este_mes", "todo"],
        format_func=lambda x: {
            "hoy": "📅 Hoy",
            "esta_semana": "🗓️ Esta semana",
            "este_mes": "📆 Este mes",
            "todo": "📂 Todo"
        }[x],
        index=2,
        horizontal=True,
        key="filtro_periodo"
    )

    # =========================
    # CARGAR DATOS
    # =========================
    todas_las_ordenes = obtener_todos("ordenes") or []
    todos_los_gastos  = obtener_gastos() or []

    todas_las_ventas = [
        o for o in todas_las_ordenes
        if o.get("estado_general") == "confirmada"
        and o.get("activo", True)  # 👈 también filtra activo aquí
    ]

    ventas  = filtrar_por_periodo(todas_las_ventas, periodo)
    gastos  = filtrar_por_periodo(todos_los_gastos, periodo)

    # 👇 CAMBIO: solo órdenes activas, confirmadas y no entregadas
    ordenes = [
        o for o in todas_las_ordenes
        if o.get("activo", True)
        and o.get("estado_general") == "confirmada"
        and o.get("estado_entrega") != "entregado"
    ]

    # =========================
    # MÉTRICAS PRINCIPALES
    # =========================
    ingresos, gastos_total, ganancia = calcular_finanzas(ventas, gastos)

    st.markdown("### 💰 Finanzas")

    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos", f"${ingresos:,.2f}")
    col2.metric("Gastos",   f"${gastos_total:,.2f}")
    col3.metric(
        "Ganancia",
        f"${ganancia:,.2f}",
        delta=f"${ganancia - gastos_total:,.2f}" if gastos_total > 0 else None
    )

    st.divider()

    # =========================
    # COBROS PENDIENTES
    # =========================
    st.markdown("### 🔔 Cobros pendientes")

    pendientes = [
        o for o in ordenes
        if o.get("estado_pago") == "pendiente"
    ]

    if not pendientes:
        st.success("✅ No hay cobros pendientes. ¡Todo al día!")
    else:
        st.warning(f"Tienes **{len(pendientes)}** orden(es) sin cobrar:")

        for o in pendientes:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                col1.write(f"👤 **{o.get('cliente', 'Sin nombre')}**")
                col2.write(f"💵 ${o.get('total', 0):,.2f}")
                col3.write(f"📦 Orden #{o.get('id', '—')}")

                # 👇 CAMBIO: botón para marcar como pagado directo desde el dashboard
                if col4.button("💳 Cobrar", key=f"cobrar_dash_{o['id']}"):
                    o["estado_pago"] = "pagado"
                    actualizar_orden(o)
                    st.rerun()

    st.divider()

    # =========================
    # GRÁFICA DE VENTAS
    # =========================
    st.markdown("### 📈 Ventas por día")

    if not ventas:
        st.info("Sin ventas registradas en este período.")
    else:
        df = pd.DataFrame(ventas)
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha"])
        chart = df.groupby("fecha")["total"].sum().reset_index()
        chart = chart.rename(columns={"fecha": "Fecha", "total": "Total ($)"})
        st.bar_chart(chart.set_index("Fecha"))

    st.divider()

    # =========================
    # ÓRDENES EN PROCESO
    # =========================
    st.markdown("### 🚚 Órdenes en proceso")

    en_proceso = [
        o for o in ordenes
        if o.get("estado_entrega") != "entregado"
    ]

    if not en_proceso:
        st.info("No hay órdenes en proceso en este momento.")
    else:
        for o in en_proceso:
            estado_entrega = o.get("estado_entrega", "pendiente")
            emoji = {"pendiente": "🟡", "en_ruta": "🔵", "entregado": "🟢"}.get(estado_entrega, "⚪")

            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            col1.write(f"👤 **{o.get('cliente', '—')}**")
            col2.write(f"{emoji} {estado_entrega.replace('_', ' ').capitalize()}")
            col3.write(f"💵 ${o.get('total', 0):,.2f}")
            col4.write(f"📦 #{o.get('id', '—')}")
