import sys
import os

# -------------------------------------------------
# RUTA DEL PROYECTO
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# -------------------------------------------------
# LIBRERÍAS
# -------------------------------------------------
import streamlit as st

# -------------------------------------------------
# IMPORTS DE UI
# -------------------------------------------------
from ui.dashboard import mostrar_dashboard
from ui.clientes_ui import clientes_ui
from ui.productos_ui import productos_ui
from ui.ordenes_ui import ordenes_ui
from ui.entregas_ui import entregas_ui

# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Gestor de ventas 🌿",
    page_icon="🌿",
    layout="wide"
)

# -------------------------------------------------
# TEMA VISUAL — CSS VERDE/NATURAL
# -------------------------------------------------
st.markdown("""
<style>

/* ══════════════════════════════════════
   FONDO GENERAL
══════════════════════════════════════ */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
.main {
    background-color: #f4faf7 !important;
}

/* ══════════════════════════════════════
   SIDEBAR
══════════════════════════════════════ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div:first-child {
    background-color: #1b4332 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #d8f3dc !important;
}

[data-testid="stSidebar"] h1 {
    color: #ffffff !important;
    font-size: 1.4rem !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: #d8f3dc !important;
    padding: 4px 8px;
    border-radius: 8px;
    display: block;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #2d6a4f !important;
}

[data-testid="stSidebar"] hr {
    border-color: #2d6a4f !important;
}

/* ══════════════════════════════════════
   BOTONES
══════════════════════════════════════ */
.stButton button {
    background-color: #40916c !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.45rem 1.1rem !important;
    font-weight: 600 !important;
    transition: background-color 0.2s ease !important;
}

.stButton button:hover {
    background-color: #2d6a4f !important;
    border: none !important;
}

.stButton button:focus {
    box-shadow: 0 0 0 2px rgba(64, 145, 108, 0.4) !important;
    border: none !important;
}

/* ══════════════════════════════════════
   TÍTULOS
══════════════════════════════════════ */
h1 {
    color: #1b4332 !important;
    border-bottom: 3px solid #74c69d !important;
    padding-bottom: 0.4rem !important;
    margin-bottom: 1.2rem !important;
}

h2, h3 {
    color: #2d6a4f !important;
}

/* ══════════════════════════════════════
   MÉTRICAS
══════════════════════════════════════ */
[data-testid="metric-container"],
[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1px solid #b7e4c7 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    box-shadow: 0 2px 6px rgba(64, 145, 108, 0.10) !important;
}

[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] {
    color: #40916c !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #1b4332 !important;
}

/* ══════════════════════════════════════
   TABS
══════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background-color: #d8f3dc !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #2d6a4f !important;
    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    background-color: #40916c !important;
    color: #ffffff !important;
}

/* ══════════════════════════════════════
   INPUTS
══════════════════════════════════════ */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    border: 1.5px solid #74c69d !important;
    border-radius: 8px !important;
    background-color: #ffffff !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: #40916c !important;
    box-shadow: 0 0 0 2px rgba(64, 145, 108, 0.2) !important;
}

/* ══════════════════════════════════════
   DATAFRAME
══════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid #b7e4c7 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ══════════════════════════════════════
   DIVIDER
══════════════════════════════════════ */
hr {
    border-color: #b7e4c7 !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("🌿 Gestor CBD")
st.sidebar.caption("Hola 👋 ¿Qué quieres hacer hoy?")
st.sidebar.divider()

opcion = st.sidebar.radio(
    "Navegación",
    [
        "📊 Dashboard",
        "📦 Productos",
        "👥 Clientes",
        "🧾 Órdenes",
        "🚚 Entregas"
    ]
)

# -------------------------------------------------
# PÁGINAS
# -------------------------------------------------
if opcion == "📊 Dashboard":
    mostrar_dashboard()

elif opcion == "👥 Clientes":
    clientes_ui()

elif opcion == "📦 Productos":
    productos_ui()

elif opcion == "🧾 Órdenes":
    ordenes_ui()

elif opcion == "🚚 Entregas":
    entregas_ui()