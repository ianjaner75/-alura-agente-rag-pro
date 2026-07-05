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
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { font-size: 2.5rem; margin: 0; }
    .main-header p { font-size: 1.1rem; opacity: 0.85; margin: 0.5rem 0 0 0; }
    .metric-card {
        background: #1e2d3d;
        border: 1px solid #2d6a9f;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card .value { font-size: 1.8rem; font-weight: bold; color: #4fc3f7; }
    .metric-card .label { font-size: 0.8rem; color: #90a4ae; margin-top: 0.2rem; }
    .source-tag {
        background: #1e3a5f;
        border-left: 3px solid #2d6a9f;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        margin: 0.3rem 0;
        font-size: 0.85rem;
        color: #b0bec5;
    }
    .stChatMessage { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    modo = st.radio(
        "Selecciona el modo:",
        ["🏢 Santos Pegasus Soluciones", "📁 Mis propios documentos"],
        index=0
    )

    if modo == "📁 Mis propios documentos":
        st.markdown("### 📂 Sube tus documentos")
        archivos = st.file_uploader(
            "Selecciona uno o más PDFs",
            type=["pdf"],
            accept_multiple_files=True
        )
        boton_cargar = st.button("🚀 Cargar documentos", type="primary", use_container_width=True)
    else:
        archivos = None
        boton_cargar = False

    st.divider()

    # Documentos cargados
    if modo == "🏢 Santos Pegasus Soluciones":
        st.markdown("### 📑 Documentos base")
        docs = [
            "Manual de Onboarding",
            "Guía Backend",
            "Guía Frontend",
            "Protocolo de Incidentes",
            "Arquitectura de Microservicios"
        ]
        for doc in docs:
            st.markdown(f"✅ {doc}")

    st.divider()
    st.markdown("### 🛠️ Stack tecnológico")
    st.markdown("🦙 **Groq** — LLaMA 3.1 8B")
    st.markdown("🤗 **HuggingFace** — MiniLM Embeddings")
    st.markdown("🔍 **FAISS** — Vector Store")
    st.markdown("🦜 **LangChain** — Orquestación RAG")

    st.divider()
    if st.button("🗑️ Limpiar historial", use_container_width=True):
        st.session_state.historial = []
        st.rerun()

# Header principal
if modo == "🏢 Santos Pegasus Soluciones":
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agente Inteligente</h1>
        <p>Santos Pegasus Soluciones — Consulta la documentación interna de la empresa</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agente Inteligente</h1>
        <p>Modo Personal — Sube tus documentos y haz preguntas sobre ellos</p>
    </div>
    """, unsafe_allow_html=True)

# Métricas
col1, col2, col3 = st.columns(3)
with col1:
    preguntas = len([m for m in st.session_state.get("historial", []) if m["rol"] == "user"])
    st.markdown(f"""<div class="metric-card">
        <div class="value">{preguntas}</div>
        <div class="label">Preguntas realizadas</div>
    </div>""", unsafe_allow_html=True)
with col2:
    docs_num = 5 if modo == "🏢 Santos Pegasus Soluciones" else len(archivos) if archivos else 0
    st.markdown(f"""<div class="metric-card">
        <div class="value">{docs_num}</div>
        <div class="label">Documentos cargados</div>
    </div>""", unsafe_allow_html=True)
with col3:
    modelo = "LLaMA 3.1 8B"
    st.markdown(f"""<div class="metric-card">
        <div class="value">⚡</div>
        <div class="label">{modelo} via Groq</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# Inicializar estado
if "agente" not in st.session_state:
    st.session_state.agente = None
if "historial" not in st.session_state:
    st.session_state.historial = []
if "modo_actual" not in st.session_state:
    st.session_state.modo_actual = None

# Cargar agente
if modo == "🏢 Santos Pegasus Soluciones":
    if st.session_state.modo_actual != "pegasus":
        st.session_state.historial = []
        st.session_state.modo_actual = "pegasus"
        st.session_state.agente = None
    if st.session_state.agente is None:
        with st.spinner("⏳ Cargando documentos de Santos Pegasus..."):
            carpeta_docs = os.path.join(os.path.dirname(__file__), "..", "docs")
            st.session_state.agente = crear_agente(carpeta_docs)
        st.success("✅ Agente listo. Puedes hacer tus preguntas.")

elif modo == "📁 Mis propios documentos":
    if st.session_state.modo_actual != "personalizado":
        st.session_state.historial = []
        st.session_state.modo_actual = "personalizado"
        st.session_state.agente = None
    if boton_cargar and archivos:
        with st.spinner(f"⏳ Procesando {len(archivos)} documento(s)..."):
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

# Historial
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["contenido"])
        if mensaje["rol"] == "assistant" and "fuentes" in mensaje:
            if mensaje["fuentes"]:
                with st.expander("📄 Ver fuentes"):
                    for f in mensaje["fuentes"]:
                        st.markdown(f'<div class="source-tag">📄 {f}</div>', unsafe_allow_html=True)

# Input
if st.session_state.agente is not None:
    pregunta = st.chat_input("Escribe tu pregunta aquí...")
    if pregunta:
        with st.chat_message("user"):
            st.write(pregunta)
        st.session_state.historial.append({"rol": "user", "contenido": pregunta})

        with st.chat_message("assistant"):
            with st.spinner("🔍 Buscando en los documentos..."):
                resultado = st.session_state.agente.invoke({"query": pregunta})
                respuesta = resultado["result"]
                source_docs = resultado.get("source_documents", [])
                fuentes_texto = []
                for doc in source_docs:
                    archivo = os.path.basename(doc.metadata.get("source", "Desconocido"))
                    pagina = doc.metadata.get("page", "?")
                    fuentes_texto.append(f"{archivo} — Página {pagina + 1}")

            st.write(respuesta)
            if fuentes_texto:
                with st.expander("📄 Ver fuentes"):
                    for f in fuentes_texto:
                        st.markdown(f'<div class="source-tag">📄 {f}</div>', unsafe_allow_html=True)

        st.session_state.historial.append({
            "rol": "assistant",
            "contenido": respuesta,
            "fuentes": fuentes_texto
        })