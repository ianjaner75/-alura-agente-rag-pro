# main.py - Interfaz web con Streamlit - Modo Dual
import streamlit as st
import sys
import os
import tempfile

sys.path.append(os.path.dirname(__file__))
from rag_agent import crear_agente, crear_agente_personalizado, hacer_pregunta

st.set_page_config(
    page_title="Agente RAG Inteligente",
    page_icon="🤖",
    layout="centered"
)

# Sidebar para seleccionar modo
with st.sidebar:
    st.title("⚙️ Configuración")
    modo = st.radio(
        "Selecciona el modo:",
        ["🏢 Santos Pegasus Soluciones", "📁 Mis propios documentos"],
        index=0
    )

    if modo == "📁 Mis propios documentos":
        st.markdown("### Sube tus documentos PDF")
        archivos = st.file_uploader(
            "Selecciona uno o más PDFs",
            type=["pdf"],
            accept_multiple_files=True
        )
        boton_cargar = st.button("🚀 Cargar documentos", type="primary")
    else:
        archivos = None
        boton_cargar = False

    st.divider()
    st.markdown("**Stack tecnológico:**")
    st.markdown("- 🦙 Groq (LLaMA 3.1)")
    st.markdown("- 🤗 HuggingFace Embeddings")
    st.markdown("- 🔍 FAISS Vector Store")
    st.markdown("- 🦜 LangChain")

# Título principal
if modo == "🏢 Santos Pegasus Soluciones":
    st.title("🤖 Agente Inteligente")
    st.subheader("Santos Pegasus Soluciones")
    st.markdown("Haz preguntas sobre la documentación interna de la empresa.")
else:
    st.title("🤖 Agente Inteligente")
    st.subheader("Modo: Documentos Personalizados")
    st.markdown("Sube tus PDFs en el panel izquierdo y haz preguntas sobre ellos.")

st.divider()

# Inicializar estado
if "agente" not in st.session_state:
    st.session_state.agente = None
if "historial" not in st.session_state:
    st.session_state.historial = []
if "modo_actual" not in st.session_state:
    st.session_state.modo_actual = None

# Cargar agente según modo
if modo == "🏢 Santos Pegasus Soluciones":
    if st.session_state.modo_actual != "pegasus":
        st.session_state.historial = []
        st.session_state.modo_actual = "pegasus"
        st.session_state.agente = None

    if st.session_state.agente is None:
        with st.spinner("Cargando documentos de Santos Pegasus..."):
            carpeta_docs = os.path.join(os.path.dirname(__file__), "..", "docs")
            st.session_state.agente = crear_agente(carpeta_docs)
        st.success("Agente listo. Puedes hacer tus preguntas.")

elif modo == "📁 Mis propios documentos":
    if st.session_state.modo_actual != "personalizado":
        st.session_state.historial = []
        st.session_state.modo_actual = "personalizado"
        st.session_state.agente = None

    if boton_cargar and archivos:
        with st.spinner(f"Procesando {len(archivos)} documento(s)..."):
            tmp_dir = tempfile.mkdtemp()
            for archivo in archivos:
                ruta = os.path.join(tmp_dir, archivo.name)
                with open(ruta, "wb") as f:
                    f.write(archivo.getbuffer())
            st.session_state.agente = crear_agente_personalizado(tmp_dir)
            st.session_state.historial = []
        st.success(f"✅ {len(archivos)} documento(s) cargado(s). Puedes hacer tus preguntas.")
    elif st.session_state.agente is None:
        st.info("👈 Sube tus documentos PDF en el panel izquierdo para comenzar.")

# Mostrar historial
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["contenido"])

# Input del usuario
if st.session_state.agente is not None:
    pregunta = st.chat_input("Escribe tu pregunta aquí...")
    if pregunta:
        with st.chat_message("user"):
            st.write(pregunta)
        st.session_state.historial.append({"rol": "user", "contenido": pregunta})

        with st.chat_message("assistant"):
            with st.spinner("Buscando respuesta..."):
                respuesta = hacer_pregunta(st.session_state.agente, pregunta)
            st.write(respuesta)
        st.session_state.historial.append({"rol": "assistant", "contenido": respuesta})