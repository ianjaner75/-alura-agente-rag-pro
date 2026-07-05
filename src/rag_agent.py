# rag_agent.py - Lógica del agente RAG con LangChain y Gemini
import os
import time
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from document_loader import cargar_documentos, dividir_documentos

load_dotenv()


PROMPT_TEMPLATE = """
Eres un asistente inteligente de Santos Pegasus Soluciones.
Usa únicamente la siguiente información para responder la pregunta.
Si no encuentras la respuesta en el contexto, di claramente que no tienes esa información.

Contexto:
{context}

Pregunta: {question}

Respuesta:"""

def crear_agente(carpeta_docs: str):
    """Crea el agente RAG cargando los documentos y construyendo el vector store"""

    ruta_faiss = os.path.join(os.path.dirname(__file__), "..", "vector_store")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if os.path.exists(ruta_faiss):
        print("Cargando vector store desde disco...")
        vector_store = FAISS.load_local(
            ruta_faiss,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("Cargando documentos...")
        documentos = cargar_documentos(carpeta_docs)
        chunks = dividir_documentos(documentos)
        print(f"Creando embeddings para {len(chunks)} chunks (solo la primera vez)...")

        textos = [chunk.page_content for chunk in chunks]
        metadatos = [chunk.metadata for chunk in chunks]

        todos_embeddings = []
        batch_size = 10
        
        
        for i in range(0, len(textos), batch_size):
            batch = textos[i:i+batch_size]
            batch_emb = embeddings.embed_documents(batch)
            todos_embeddings.extend(batch_emb)
            print(f"Procesados {min(i+batch_size, len(textos))}/{len(textos)} chunks...")

        vector_store = FAISS.from_embeddings(
            list(zip(textos, todos_embeddings)),
            embeddings,
            metadatas=metadatos
        )
        vector_store.save_local(ruta_faiss)
        print("Vector store guardado en disco.")

    print("Configurando el agente...")
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    # Reducimos k de 4 a 2 para enviar menos texto y consumir menos tokens por consulta
    agente = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    print("Agente listo.")
    return agente

def hacer_pregunta(agente, pregunta: str) -> str:
    """Hace una pregunta al agente"""
    try:
        resultado = agente.invoke({"query": pregunta})
        return resultado["result"]
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise e

def crear_agente_personalizado(carpeta_docs: str):
    """Crea un agente RAG temporal con documentos del usuario"""
    
    print("Cargando documentos personalizados...")
    documentos = cargar_documentos(carpeta_docs)
    chunks = dividir_documentos(documentos)
    print(f"Creando embeddings para {len(chunks)} chunks...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    textos = [chunk.page_content for chunk in chunks]
    metadatos = [chunk.metadata for chunk in chunks]

    todos_embeddings = []
    batch_size = 10

    for i in range(0, len(textos), batch_size):
        batch = textos[i:i+batch_size]
        batch_emb = embeddings.embed_documents(batch)
        todos_embeddings.extend(batch_emb)
        print(f"Procesados {min(i+batch_size, len(textos))}/{len(textos)} chunks...")

    vector_store = FAISS.from_embeddings(
        list(zip(textos, todos_embeddings)),
        embeddings,
        metadatas=metadatos
    )

    print("Configurando agente personalizado...")
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )

    prompt_personalizado = PromptTemplate(
        template="""Eres un asistente inteligente.
Usa únicamente la siguiente información para responder la pregunta.
Si no encuentras la respuesta en el contexto, di claramente que no tienes esa información.

Contexto:
{context}

Pregunta: {question}

Respuesta:""",
        input_variables=["context", "question"]
    )

    agente = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        chain_type_kwargs={"prompt": prompt_personalizado},
        return_source_documents=True
    )

    print("Agente personalizado listo.")
    return agente