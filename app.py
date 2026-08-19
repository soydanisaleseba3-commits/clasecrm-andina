import streamlit as st
import random
import csv
import os

st.set_page_config(page_title="Juega y Gana un Descuento", page_icon="🎮")

# Inicialización de variables de estado
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "registro"
if "tablero" not in st.session_state:
    st.session_state.tablero = [""] * 9
if "email" not in st.session_state:
    st.session_state.email = ""
if "ganador" not in st.session_state:
    st.session_state.ganador = None

def guardar_correo(email):
    # Guarda el correo capturado en un archivo CSV local
    archivo = "clientes.csv"
    existe = os.path.isfile(archivo)
    with open(archivo, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["Email"])
        writer.writerow([email])

def verificar_victoria(tablero, jugador):
    combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Filas
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columnas
        [0, 4, 8], [2, 4, 6]             # Diagonales
    ]
    return any(all(tablero[i] == jugador for i in c) for c in combos)

def turno_cpu():
    # La CPU elige una casilla vacía al azar (jugador "O")
    vacios = [i for i, x in enumerate(st.session_state.tablero) if x == ""]
    if vacios and not st.session_state.ganador:
        i = random.choice(vacios)
        st.session_state.tablero[i] = "O"

def marcar_casilla(indice):
    if st.session_state.tablero[indice] == "" and not st.session_state.ganador:
        st.session_state.tablero[indice] = "X"
        if verificar_victoria(st.session_state.tablero, "X"):
            st.session_state.ganador = "Usuario"
            st.session_state.pantalla = "premio"
        else:
            turno_cpu()
            if verificar_victoria(st.session_state.tablero, "O"):
                st.session_state.ganador = "CPU"

# PANTALLA 1: Captura de Correo
if st.session_state.pantalla == "registro":
    st.title("🎯 ¡Juega y Gana un Descuento!")
    st.write("Ingresa tu correo electrónico para comenzar a jugar al Triqui.")
    
    email_input = st.text_input("Correo electrónico:")
    if st.button("Comenzar Juego"):
        if "@" in email_input and "." in email_input:
            st.session_state.email = email_input
            guardar_correo(email_input)
            st.session_state.pantalla = "juego"
            st.rerun()
        else:
            st.warning("Por favor, ingresa un correo válido.")

# PANTALLA 2: Tablero del Triqui
elif st.session_state.pantalla == "juego":
    st.title("❌ Triqui ⭕")
    st.write(f"Jugando como: **{st.session_state.email}**")
    
    # Renderizar grilla de 3x3
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
                args=(idx,),
                use_container_width=True
            )

    if st.session_state.ganador == "CPU":
        st.error("¡Casi! La máquina completó la línea primero.")
        if st.button("Intentar de nuevo"):
            st.session_state.tablero = [""] * 9
            st.session_state.ganador = None
            st.rerun()

# PANTALLA 3: Cupón de Descuento
elif st.session_state.pantalla == "premio":
    st.balloons()
    st.title("🎉 ¡Felicidades, ganaste!")
    st.success("Hiciste las 3 en raya con éxito.")
    st.markdown("### Tu código de descuento es:")
    st.code("DESCUENTO10OFF", language="text")
    st.info("Utiliza este código al realizar tu compra en nuestra tienda.")
