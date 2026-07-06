# main.py - Interfaz web con Streamlit - Modo Dual + Chats persistentes
import streamlit as st
import sys
import os
import tempfile

sys.path.append(os.path.dirname(__file__))
from rag_agent import crear_agente, crear_agente_personalizado, hacer_pregunta
from database import crear_chat, obtener_chats, obtener_mensajes, guardar_mensaje, eliminar_chat, renombrar_chat, subir_pdf_supabase, listar_pdfs_chat, asociar_archivos_chat

st.set_page_config(
    page_title="Agente RAG Inteligente",
    page_icon="🤖",
    layout="wide"
)

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
    .chat-item {
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.2rem 0;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado
if "agente" not in st.session_state:
    st.session_state.agente = None
if "historial" not in st.session_state:
    st.session_state.historial = []
if "modo_actual" not in st.session_state:
    st.session_state.modo_actual = None
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    modo_default = st.session_state.get("modo_cargado", "🏢 Santos Pegasus Soluciones")
    modo_index = 0 if modo_default == "🏢 Santos Pegasus Soluciones" else 1
    modo = st.radio(
        "Selecciona el modo:",
        ["🏢 Santos Pegasus Soluciones", "📁 Mis propios documentos"],
        index=modo_index
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

    if modo == "🏢 Santos Pegasus Soluciones":
        st.markdown("### 📑 Documentos base")
        for doc in ["Manual de Onboarding", "Guía Backend", "Guía Frontend", "Protocolo de Incidentes", "Arquitectura de Microservicios"]:
            st.markdown(f"✅ {doc}")

    st.divider()
    st.markdown("### 🛠️ Stack tecnológico")
    st.markdown("🦙 **Groq** — LLaMA 3.1 8B")
    st.markdown("🤗 **HuggingFace** — MiniLM Embeddings")
    st.markdown("🔍 **FAISS** — Vector Store")
    st.markdown("🦜 **LangChain** — Orquestación RAG")

    st.divider()

    # Panel de chats guardados
    st.markdown("### 💬 Chats guardados")

    if st.button("➕ Nuevo chat", use_container_width=True, type="primary"):
        st.session_state.chat_id = None
        st.session_state.historial = []
        st.session_state.agente = None
        st.session_state.modo_actual = None
        st.rerun()

    chats = obtener_chats()
    for chat in chats:
        col1, col2 = st.columns([4, 1])
        with col1:
            titulo = chat["titulo"][:25] + "..." if len(chat["titulo"]) > 25 else chat["titulo"]
            if st.button(f"💬 {titulo}", key=f"chat_{chat['id']}", use_container_width=True):
                st.session_state.chat_id = chat["id"]
                mensajes = obtener_mensajes(chat["id"])
                st.session_state.historial = [
                    {"rol": m["rol"], "contenido": m["contenido"], "fuentes": m["fuentes"] or []}
                    for m in mensajes
                ]
                if chat["modo"] == "personalizado":
                    archivos_guardados = listar_pdfs_chat(chat["id"])
                    if archivos_guardados:
                        with st.spinner("⏳ Recuperando documentos del chat..."):
                            import requests
                            tmp_dir = tempfile.mkdtemp()
                            for archivo_info in archivos_guardados:
                                response = requests.get(archivo_info["url"])
                                ruta = os.path.join(tmp_dir, archivo_info["nombre"])
                                with open(ruta, "wb") as f:
                                    f.write(response.content)
                            st.session_state.agente = crear_agente_personalizado(tmp_dir)
                            st.session_state.modo_actual = "personalizado"
                            st.session_state.modo_cargado = "📁 Mis propios documentos"
                    else:
                        st.session_state.agente = None
                        st.session_state.modo_actual = "personalizado"
                        st.session_state.modo_cargado = "📁 Mis propios documentos"
                else:
                    st.session_state.agente = None
                    st.session_state.modo_actual = None
                    st.session_state.modo_cargado = "🏢 Santos Pegasus Soluciones"
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat['id']}"):
                eliminar_chat(chat["id"])
                if st.session_state.chat_id == chat["id"]:
                    st.session_state.chat_id = None
                    st.session_state.historial = []
                st.rerun()

# Header
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
    preguntas = len([m for m in st.session_state.historial if m["rol"] == "user"])
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
    total_chats = len(chats)
    st.markdown(f"""<div class="metric-card">
        <div class="value">{total_chats}</div>
        <div class="label">Chats guardados</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# Cargar agente
if modo == "🏢 Santos Pegasus Soluciones":
    if st.session_state.modo_actual != "pegasus":
        st.session_state.modo_actual = "pegasus"
        st.session_state.agente = None
    if st.session_state.agente is None:
        with st.spinner("⏳ Cargando documentos de Santos Pegasus..."):
            carpeta_docs = os.path.join(os.path.dirname(__file__), "..", "docs")
            st.session_state.agente = crear_agente(carpeta_docs)
        st.success("✅ Agente listo. Puedes hacer tus preguntas.")

#  CÓDIGO MODIFICADO:
elif modo == "📁 Mis propios documentos":
    if st.session_state.modo_actual != "personalizado":
        st.session_state.modo_actual = "personalizado"
        st.session_state.agente = None
        
    if boton_cargar and archivos:
        with st.spinner(f"⏳ Procesando {len(archivos)} documento(s)..."):
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
        st.success(f"✅ {len(archivos)} documento(s) cargado(s). Puedes hacer tus preguntas.")
        
    elif st.session_state.agente is None and not archivos:
        # Si no hay agente en memoria pero hay un chat activo, reconstruimos el índice FAISS al vuelo
        if st.session_state.get("chat_id") is not None:
            with st.spinner("⏳ Reconstruyendo base de datos vectorial desde Supabase..."):
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
                    st.info("👈 Sube tus documentos PDF en el panel izquierdo para comenzar.")
        else:
            st.info("👈 Sube tus documentos PDF en el panel izquierdo para comenzar.")

# Historial
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["contenido"])
        if mensaje["rol"] == "assistant" and mensaje.get("fuentes"):
            with st.expander("📄 Ver fuentes"):
                for f in mensaje["fuentes"]:
                    st.markdown(f'<div class="source-tag">📄 {f}</div>', unsafe_allow_html=True)

# Input
if st.session_state.agente is not None:
    pregunta = st.chat_input("Escribe tu pregunta aquí...")
    if pregunta:
        # Crear chat nuevo si no existe
        if st.session_state.chat_id is None:
            titulo = pregunta[:50]
            modo_str = "pegasus" if modo == "🏢 Santos Pegasus Soluciones" else "personalizado"
            st.session_state.chat_id = crear_chat(titulo, modo_str)
            if modo_str == "personalizado" and "archivos_info" in st.session_state:
                asociar_archivos_chat(st.session_state.chat_id, st.session_state.archivos_info)

        with st.chat_message("user"):
            st.write(pregunta)
        st.session_state.historial.append({"rol": "user", "contenido": pregunta, "fuentes": []})
        guardar_mensaje(st.session_state.chat_id, "user", pregunta)

        #  CÓDIGO MODIFICADO:
        with st.chat_message("assistant"):
            with st.spinner("🔍 Buscando en los documentos..."):
                # Le enviamos el historial completo para que LLaMA 3.1 tenga contexto de la conversación
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
                        st.markdown(f'<div class="source-tag">📄 {f}</div>', unsafe_allow_html=True)

        st.session_state.historial.append({
            "rol": "assistant",
            "contenido": respuesta,
            "fuentes": fuentes_texto
        })
        guardar_mensaje(st.session_state.chat_id, "assistant", respuesta, fuentes_texto)
        st.rerun()