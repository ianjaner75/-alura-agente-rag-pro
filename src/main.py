# main.py - Interfaz web con Streamlit - Modo Dual + Chats persistentes
import streamlit as st
import sys
import os
import tempfile

sys.path.append(os.path.dirname(__file__))
from rag_agent import crear_agente, crear_agente_personalizado, hacer_pregunta
from database import (crear_chat, obtener_chats, obtener_mensajes, guardar_mensaje,
                      eliminar_chat, renombrar_chat, subir_pdf_supabase,
                      listar_pdfs_chat, asociar_archivos_chat)

st.set_page_config(
    page_title="RAG Agent · Santos Pegasus",
    page_icon="⬡",
    layout="wide"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

/* ══ FORZAR MODO OSCURO EN TODO EL APP ══ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main, .block-container,
section[data-testid="stSidebar"] > div,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
    background-color: #080C14 !important;
    color: #E2EAF4 !important;
}

/* sidebar fondo propio */
[data-testid="stSidebar"] {
    background: #0A0F1C !important;
    border-right: 1px solid #1E2D45 !important;
}
[data-testid="stSidebar"] * { color: #A8B8CC !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong { color: #E2EAF4 !important; }

/* barra superior de Streamlit */
[data-testid="stHeader"],
header[data-testid="stHeader"] { background: #080C14 !important; border-bottom: 1px solid #1E2D45 !important; }

/* input de chat */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] > div {
    background: #0F1520 !important;
    color: #E2EAF4 !important;
    border: 1px solid #1E2D45 !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"]:focus-within > div {
    border-color: #00C2FF !important;
    box-shadow: 0 0 0 2px rgba(0,194,255,.08) !important;
}

/* mensajes del chat */
[data-testid="stChatMessage"] {
    background: #0F1520 !important;
    border: 1px solid #1E2D45 !important;
    border-radius: 12px !important;
    color: #C8D8E8 !important;
}
[data-testid="stChatMessage"] * { color: #C8D8E8 !important; }

/* expander */
[data-testid="stExpander"],
[data-testid="stExpander"] > div {
    background: #0A0F1C !important;
    border: 1px solid #1E2D45 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] * { color: #5A7A9A !important; }

/* alerts / success */
[data-testid="stAlert"],
[data-testid="stSuccess"] {
    background: #061A10 !important;
    border: 1px solid #0D3A20 !important;
    color: #00C2A0 !important;
    border-radius: 8px !important;
}
[data-testid="stAlert"] * { color: #00C2A0 !important; }

/* info box */
[data-testid="stInfo"] {
    background: #080C14 !important;
    border: 1px solid #1E2D45 !important;
    color: #5A7A9A !important;
}

/* spinner */
[data-testid="stSpinner"] * { color: #00C2FF !important; }

/* file uploader */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"] {
    background: #0F1520 !important;
    border: 1px dashed #1E3A5A !important;
    border-radius: 10px !important;
    color: #5A7A9A !important;
}
[data-testid="stFileUploader"] * { color: #7A9AB8 !important; }

/* radio buttons */
[data-testid="stRadio"] label { color: #A8B8CC !important; font-size: 0.88rem !important; }
[data-testid="stRadio"] { color: #A8B8CC !important; }

/* divider */
hr { border-color: #1E2D45 !important; }

/* scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080C14; }
::-webkit-scrollbar-thumb { background: #1E2D45; border-radius: 2px; }

/* botones */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    border: 1px solid #1E2D45 !important;
    background: #0F1520 !important;
    color: #A8B8CC !important;
}
.stButton > button:hover {
    border-color: #00C2FF !important;
    color: #00C2FF !important;
    box-shadow: 0 0 12px rgba(0,194,255,0.12) !important;
    background: #0A1525 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0066AA, #6366F1) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 500 !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 18px rgba(99,102,241,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ══ HEADER CENTRADO ══ */
.sys-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 2.5rem 0 1.5rem;
    border-bottom: 1px solid #1E2D45;
    margin-bottom: 1.5rem;
    position: relative;
}
.sys-logo-svg {
    margin-bottom: 12px;
}
.sys-header h1 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #E2EAF4;
    margin: 0 0 6px;
    letter-spacing: -0.02em;
}
.sys-header p {
    font-size: 0.75rem;
    color: #3A5A7A;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.sys-status {
    position: absolute;
    top: 2.5rem;
    right: 0;
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.7rem;
    color: #00C2FF;
    font-family: 'JetBrains Mono', monospace;
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00C2FF;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,194,255,.4); }
    50% { opacity: .5; box-shadow: 0 0 0 5px rgba(0,194,255,0); }
}

/* ══ MÉTRICAS ══ */
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.5rem; }
.metric-card {
    background: #0F1520;
    border: 1px solid #1E2D45;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    animation: fadein .4s ease forwards;
}
.metric-card:nth-child(2) { animation-delay: .08s; }
.metric-card:nth-child(3) { animation-delay: .16s; }
@keyframes fadein { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:none; } }
.metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00C2FF, #6366F1);
}
.metric-card .m-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem; font-weight: 600;
    color: #00C2FF; line-height: 1; margin-bottom: 6px;
}
.metric-card .m-label {
    font-size: 0.68rem; color: #3A5A7A;
    text-transform: uppercase; letter-spacing: 0.1em;
}

/* fuentes */
.source-tag {
    display: inline-flex; align-items: center; gap: 5px;
    background: #0F1520; border: 1px solid #1E2D45; border-radius: 6px;
    padding: 3px 10px; font-size: 0.75rem; color: #5A7A9A;
    margin: 3px 3px 0 0; font-family: 'JetBrains Mono', monospace;
}

/* estado vacío */
.empty-state {
    text-align: center; padding: 4rem 1rem; color: #1E2D45;
}
.empty-state .es-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: .4; }
.empty-state p { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #2A4060; }

/* stack items sidebar */
.stack-item {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 0; font-size: 0.82rem; color: #5A7A9A;
    border-bottom: 1px solid #1A2535;
}
.stack-item span { color: #7A9AB8 !important; }

/* doc list sidebar */
.doc-item {
    font-size: .82rem; padding: 5px 0;
    color: #5A7A9A; border-bottom: 1px solid #1A2535;
    display: flex; align-items: center; gap: 6px;
}
.doc-item::before { content: '✦'; color: #1E3A5A; font-size: .7rem; }
</style>
""", unsafe_allow_html=True)

# ── Estado inicial ─────────────────────────────────────────────────────────────
for key, val in {
    "agente": None, "historial": [], "modo_actual": None,
    "chat_id": None, "modo_cargado": "🏢 Santos Pegasus Soluciones", "archivos_info": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    modo_index = 0 if st.session_state.modo_cargado == "🏢 Santos Pegasus Soluciones" else 1
    modo = st.radio("Selecciona el modo:",
                    ["🏢 Santos Pegasus Soluciones", "📁 Mis propios documentos"],
                    index=modo_index)

    if modo == "📁 Mis propios documentos":
        st.markdown("### 📂 Sube tus documentos")
        archivos = st.file_uploader("PDF o CSV", type=["pdf", "csv"], accept_multiple_files=True)
        boton_cargar = st.button("🚀 Cargar documentos", type="primary", use_container_width=True)
    else:
        archivos = None
        boton_cargar = False

    st.divider()

    if modo == "🏢 Santos Pegasus Soluciones":
        st.markdown("### 📑 Documentos base")
        for doc in ["Manual de Onboarding", "Guía Backend", "Guía Frontend",
                    "Protocolo de Incidentes", "Arquitectura de Microservicios"]:
            st.markdown(f"<div class='doc-item'>{doc}</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🛠️ Stack")
    for icon, label in [("🦙","Groq — LLaMA 3.1 8B"), ("🤗","HuggingFace — MiniLM"),
                        ("🔍","FAISS — Vector Store"), ("🦜","LangChain — RAG"),
                        ("🗄️","Supabase — DB")]:
        st.markdown(f"<div class='stack-item'>{icon} <span>{label}</span></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 💬 Chats")
    if st.button("＋ Nuevo chat", use_container_width=True, type="primary"):
        st.session_state.chat_id = None
        st.session_state.historial = []
        st.session_state.agente = None
        st.session_state.modo_actual = None
        st.session_state.modo_cargado = "🏢 Santos Pegasus Soluciones"
        st.rerun()

    chats = obtener_chats()
    for chat in chats:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            titulo = chat["titulo"][:22] + "..." if len(chat["titulo"]) > 22 else chat["titulo"]
            activo = "🔵 " if st.session_state.chat_id == chat["id"] else ""
            if st.button(f"{activo}💬 {titulo}", key=f"chat_{chat['id']}", use_container_width=True):
                st.session_state.chat_id = chat["id"]
                mensajes = obtener_mensajes(chat["id"])
                st.session_state.historial = [
                    {"rol": m["rol"], "contenido": m["contenido"], "fuentes": m["fuentes"] or []}
                    for m in mensajes
                ]
                if chat["modo"] == "personalizado":
                    st.session_state.modo_cargado = "📁 Mis propios documentos"
                    st.session_state.modo_actual = "personalizado"
                    archivos_guardados = listar_pdfs_chat(chat["id"])
                    if archivos_guardados:
                        with st.spinner("⏳ Recuperando documentos..."):
                            import requests
                            tmp_dir = tempfile.mkdtemp()
                            for archivo_info in archivos_guardados:
                                response = requests.get(archivo_info["url"])
                                ruta = os.path.join(tmp_dir, archivo_info["nombre"])
                                with open(ruta, "wb") as f:
                                    f.write(response.content)
                            st.session_state.agente = crear_agente_personalizado(tmp_dir)
                    else:
                        st.session_state.agente = None
                else:
                    st.session_state.modo_cargado = "🏢 Santos Pegasus Soluciones"
                    st.session_state.modo_actual = None
                    st.session_state.agente = None
                st.rerun()
        with col_b:
            if st.button("✕", key=f"del_{chat['id']}"):
                eliminar_chat(chat["id"])
                if st.session_state.chat_id == chat["id"]:
                    st.session_state.chat_id = None
                    st.session_state.historial = []
                    st.session_state.agente = None
                st.rerun()

# ── Logo SVG centrado ──────────────────────────────────────────────────────────
logo_svg = """
<svg width="52" height="52" viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg">
  <polygon points="26,3 48,15 48,37 26,49 4,37 4,15"
           fill="none" stroke="#00C2FF" stroke-width="1.5" opacity="0.4"/>
  <polygon points="26,10 41,19 41,33 26,42 11,33 11,19"
           fill="none" stroke="#00C2FF" stroke-width="1" opacity="0.7"/>
  <circle cx="26" cy="26" r="6" fill="#00C2FF" opacity="0.9"/>
  <circle cx="26" cy="26" r="3" fill="#080C14"/>
  <line x1="26" y1="10" x2="26" y2="20" stroke="#6366F1" stroke-width="1" opacity="0.5"/>
  <line x1="26" y1="32" x2="26" y2="42" stroke="#6366F1" stroke-width="1" opacity="0.5"/>
  <line x1="11" y1="19" x2="20" y2="23" stroke="#6366F1" stroke-width="1" opacity="0.5"/>
  <line x1="32" y1="29" x2="41" y2="33" stroke="#6366F1" stroke-width="1" opacity="0.5"/>
  <line x1="41" y1="19" x2="32" y2="23" stroke="#6366F1" stroke-width="1" opacity="0.5"/>
  <line x1="20" y1="29" x2="11" y2="33" stroke="#6366F1" stroke-width="1" opacity="0.5"/>
</svg>
"""

modo_label = "PEGASUS MODE" if modo == "🏢 Santos Pegasus Soluciones" else "PERSONAL MODE"
subtitulo  = "Documentación interna · Santos Pegasus Soluciones" if modo == "🏢 Santos Pegasus Soluciones" else "Documentos propios · RAG personalizado"

st.markdown(f"""
<div class="sys-header">
  <div class="sys-logo-svg">{logo_svg}</div>
  <h1>RAG Agent</h1>
  <p>{subtitulo}</p>
  <div class="sys-status">
    <div class="status-dot"></div>
    SISTEMA ACTIVO · {modo_label}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Métricas ───────────────────────────────────────────────────────────────────
preguntas_count = len([m for m in st.session_state.historial if m["rol"] == "user"])
docs_count = 5 if modo == "🏢 Santos Pegasus Soluciones" else (len(archivos) if archivos else 0)
chats_count = len(chats)

st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="m-value">{preguntas_count}</div>
    <div class="m-label">Preguntas realizadas</div>
  </div>
  <div class="metric-card">
    <div class="m-value">{docs_count}</div>
    <div class="m-label">Documentos cargados</div>
  </div>
  <div class="metric-card">
    <div class="m-value">{chats_count}</div>
    <div class="m-label">Chats guardados</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Cargar agente ──────────────────────────────────────────────────────────────
if modo == "🏢 Santos Pegasus Soluciones":
    if st.session_state.modo_actual != "pegasus":
        st.session_state.modo_actual = "pegasus"
        st.session_state.agente = None
    if st.session_state.agente is None:
        with st.spinner("⏳ Inicializando base vectorial Pegasus..."):
            carpeta_docs = os.path.join(os.path.dirname(__file__), "..", "docs")
            st.session_state.agente = crear_agente(carpeta_docs)
        st.success("✅ Agente listo.")

elif modo == "📁 Mis propios documentos":
    if st.session_state.modo_actual not in ("personalizado", None):
        st.session_state.modo_actual = "personalizado"
        st.session_state.agente = None

    if boton_cargar and archivos:
        with st.spinner(f"⏳ Procesando {len(archivos)} archivo(s)..."):
            tmp_dir = tempfile.mkdtemp()
            archivos_info = []
            for archivo in archivos:
                contenido = archivo.getbuffer()
                url, nombre_unico = subir_pdf_supabase(archivo.name, bytes(contenido))
                ruta = os.path.join(tmp_dir, archivo.name)
                with open(ruta, "wb") as f:
                    f.write(contenido)
                archivos_info.append({"nombre": archivo.name, "url": url, "path": nombre_unico})
            st.session_state.agente = crear_agente_personalizado(tmp_dir)
            st.session_state.historial = []
            st.session_state.archivos_info = archivos_info
            st.session_state.modo_actual = "personalizado"
        st.success(f"✅ {len(archivos)} archivo(s) indexados.")

    elif st.session_state.agente is None and not archivos:
        if st.session_state.get("chat_id") is not None and st.session_state.modo_actual == "personalizado":
            with st.spinner("⏳ Reconstruyendo índice vectorial desde Supabase..."):
                archivos_guardados = listar_pdfs_chat(st.session_state.chat_id)
                if archivos_guardados:
                    import requests
                    tmp_dir = tempfile.mkdtemp()
                    for archivo_info in archivos_guardados:
                        response = requests.get(archivo_info["url"])
                        ruta = os.path.join(tmp_dir, archivo_info["nombre"])
                        with open(ruta, "wb") as f:
                            f.write(response.content)
                    st.session_state.agente = crear_agente_personalizado(tmp_dir)
                    st.rerun()
                else:
                    st.info("👈 Sube tus documentos PDF o CSV para comenzar.")
        else:
            st.markdown("""
            <div class="empty-state">
              <div class="es-icon">⬡</div>
              <p>Sube un PDF o CSV en el panel izquierdo para comenzar</p>
            </div>
            """, unsafe_allow_html=True)

# ── Historial ──────────────────────────────────────────────────────────────────
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["contenido"])
        if mensaje["rol"] == "assistant" and mensaje.get("fuentes"):
            with st.expander("📄 Ver fuentes"):
                for f in mensaje["fuentes"]:
                    st.markdown(f'<span class="source-tag">📄 {f}</span>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
if st.session_state.agente is not None:
    pregunta = st.chat_input("Consulta la base de conocimiento...")
    if pregunta:
        if st.session_state.chat_id is None:
            titulo = pregunta[:50]
            modo_str = "pegasus" if modo == "🏢 Santos Pegasus Soluciones" else "personalizado"
            st.session_state.chat_id = crear_chat(titulo, modo_str)
            if modo_str == "personalizado" and st.session_state.archivos_info:
                asociar_archivos_chat(st.session_state.chat_id, st.session_state.archivos_info)

        with st.chat_message("user"):
            st.write(pregunta)
        st.session_state.historial.append({"rol": "user", "contenido": pregunta, "fuentes": []})
        guardar_mensaje(st.session_state.chat_id, "user", pregunta)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Buscando en la base vectorial..."):
                resultado = hacer_pregunta(st.session_state.agente, pregunta, st.session_state.historial)
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
                        st.markdown(f'<span class="source-tag">📄 {f}</span>', unsafe_allow_html=True)

        st.session_state.historial.append({
            "rol": "assistant", "contenido": respuesta, "fuentes": fuentes_texto
        })
        guardar_mensaje(st.session_state.chat_id, "assistant", respuesta, fuentes_texto)
        st.rerun()