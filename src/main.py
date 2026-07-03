# main.py - Interfaz web con Streamlit
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))
from rag_agent import crear_agente, hacer_pregunta

# Configuración de la página
st.set_page_config(
    page_title="Agente RAG - Santos Pegasus Soluciones",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Agente Inteligente")
st.subheader("Santos Pegasus Soluciones")
st.markdown("Haz preguntas sobre la documentación interna de la empresa.")
st.divider()

# Inicializar el agente una sola vez
@st.cache_resource
def inicializar_agente():
    carpeta_docs = os.path.join(os.path.dirname(__file__), "..", "docs")
    return crear_agente(carpeta_docs)

with st.spinner("Cargando documentos y preparando el agente..."):
    agente = inicializar_agente()

st.success("Agente listo. Puedes hacer tus preguntas.")

# Historial de conversación
if "historial" not in st.session_state:
    st.session_state.historial = []

# Mostrar historial
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["contenido"])

# Input del usuario
pregunta = st.chat_input("Escribe tu pregunta aquí...")

if pregunta:
    with st.chat_message("user"):
        st.write(pregunta)
    st.session_state.historial.append({
        "rol": "user",
        "contenido": pregunta
    })

    with st.chat_message("assistant"):
        with st.spinner("Buscando respuesta..."):
            respuesta = hacer_pregunta(agente, pregunta)
        st.write(respuesta)
    st.session_state.historial.append({
        "rol": "assistant",
        "contenido": respuesta
    })
