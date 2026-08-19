import streamlit as st
import random
import csv
import os

# Configuración de página
st.set_page_config(
    page_title="Triqui: Juega y Gana",
    page_icon="🎮",
    layout="centered"
)

# --- ESTILOS CSS PERSONALIZADOS (Diseño Neón & Glassmorphism) ---
st.markdown("""
<style>
    /* Fondo principal oscuro con gradiente */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a0b2e 0%, #090314 100%);
        color: #ffffff;
    }

    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Encabezado Neón */
    .neon-title {
        text-align: center;
        font-family: 'sans-serif';
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #f7797d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
        margin-bottom: 20px;
    }

    /* Tarjetas estilo Glassmorphism para los formularios */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    /* Estilo de las casillas del juego (Botones nativos transformados) */
    div.stButton > button {
        height: 110px !important;
        width: 100% !important;
        font-size: 3rem !important;
        font-weight: bold !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.02) !important;
    }

    /* Hover sobre las casillas */
    div.stButton > button:hover {
        border-color: #00f2fe !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.5), inset 0 0 10px rgba(0, 242, 254, 0.3) !important;
        transform: translateY(-3px);
    }

    /* Estilo para los inputs de texto */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #fff !important;
    }

    /* Modales de alerta/éxito estilizados */
    .stSuccess, .stInfo, .stWarning, .stError {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADO DE LA SESIÓN ---
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "registro"
if "tablero" not in st.session_state:
    st.session_state.tablero = [""] * 9
if "email" not in st.session_state:
    st.session_state.email = ""
if "ganador" not in st.session_state:
    st.session_state.ganador = None

# --- FUNCIONES DE LÓGICA ---
def guardar_correo(email):
    archivo = "clientes.csv"
    existe = os.path.isfile(archivo)
    with open(archivo, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["Email"])
        writer.writerow([email])

def verificar_victoria(tablero, jugador):
    combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    return any(all(tablero[i] == jugador for i in c) for c in combos)

def turno_cpu():
    vacios = [i for i, x in enumerate(st.session_state.tablero) if x == ""]
    if vacios and not st.session_state.ganador:
        i = random.choice(vacios)
        st.session_state.tablero[i] = "⭕"

def marcar_casilla(indice):
    if st.session_state.tablero[indice] == "" and not st.session_state.ganador:
        st.session_state.tablero[indice] = "❌"
        if verificar_victoria(st.session_state.tablero, "❌"):
            st.session_state.ganador = "Usuario"
            st.session_state.pantalla = "premio"
        else:
            turno_cpu()
            if verificar_victoria(st.session_state.tablero, "⭕"):
                st.session_state.ganador = "CPU"

# --- PANTALLA 1: REGISTRO ---
if st.session_state.pantalla == "registro":
    st.markdown('<h1 class="neon-title">TRIQUI: JUEGA Y GANA</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <h3 style="text-align: center; margin-bottom: 10px;">¡Consigue tu Cupón de Descuento!</h3>
            <p style="text-align: center; color: #a0a0a0;">Ingresa tu correo para habilitar el tablero y competir por un 10% OFF.</p>
        </div>
    """, unsafe_allow_html=True)
    
    email_input = st.text_input("Correo electrónico:", placeholder="ejemplo@correo.com")
    
    if st.button("🚀 INICIAR JUEGO"):
        if "@" in email_input and "." in email_input:
            st.session_state.email = email_input
            guardar_correo(email_input)
            st.session_state.pantalla = "juego"
            st.rerun()
        else:
            st.warning("⚠️ Ingresa un correo electrónico válido.")

# --- PANTALLA 2: JUEGO DE TRIQUI ---
elif st.session_state.pantalla == "juego":
    st.markdown('<h1 class="neon-title">TRIQUI: JUEGA Y GANA</h1>', unsafe_allow_html=True)
    
    # Barra de estado superior
    st.markdown(f"""
        <div class="glass-card" style="padding: 15px; display: flex; justify-content: space-between; align-items: center;">
            <span>👤 <b>{st.session_state.email}</b></span>
            <span style="color: #00f2fe; font-weight: bold;">TU TURNO: ❌</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Renderizado del tablero 3x3
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            val = st.session_state.tablero[idx]
            label = val if val != "" else " "
            cols[col].button(
                label, 
                key=f"btn_{idx}", 
                on_click=marcar_casilla, 
                args=(idx,)
            )

    if st.session_state.ganador == "CPU":
        st.error("🤖 ¡La máquina ha completado la línea!")
        if st.button("🔄 Intentar de nuevo"):
            st.session_state.tablero = [""] * 9
            st.session_state.ganador = None
            st.rerun()

# --- PANTALLA 3: PREMIO ---
elif st.session_state.pantalla == "premio":
    st.balloons()
    st.markdown('<h1 class="neon-title">¡VICTORIA!</h1>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h2>🎉 ¡Completaste las 3 en raya!</h2>
            <p>Aquí tienes tu cupón exclusivo:</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.code("DESCUENTO10OFF", language="text")
    st.info("Copia este código y úsalo al momento del pago.")
