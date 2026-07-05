# rag_agent.py - Lógica del agente RAG con LangChain y Groq
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from document_loader import cargar_documentos, dividir_documentos

load_dotenv()

def crear_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def crear_vector_store(chunks, embeddings):
    textos = [chunk.page_content for chunk in chunks]
    metadatos = [chunk.metadata for chunk in chunks]
    todos_embeddings = []
    batch_size = 10
    for i in range(0, len(textos), batch_size):
        batch = textos[i:i+batch_size]
        batch_emb = embeddings.embed_documents(batch)
        todos_embeddings.extend(batch_emb)
        print(f"Procesados {min(i+batch_size, len(textos))}/{len(textos)} chunks...")
    return FAISS.from_embeddings(
        list(zip(textos, todos_embeddings)),
        embeddings,
        metadatas=metadatos
    )

def crear_cadena(vector_store, memoria):
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        memory=memoria,
        return_source_documents=True,
        verbose=False
    )

def crear_agente(carpeta_docs: str):
    ruta_faiss = os.path.join(os.path.dirname(__file__), "..", "vector_store")
    embeddings = crear_embeddings()
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
        vector_store = crear_vector_store(chunks, embeddings)
        vector_store.save_local(ruta_faiss)
        print("Vector store guardado en disco.")
    
    memoria = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
        k=5
    )
    print("Agente listo.")
    return crear_cadena(vector_store, memoria)

def crear_agente_personalizado(carpeta_docs: str):
    print("Cargando documentos personalizados...")
    embeddings = crear_embeddings()
    documentos = cargar_documentos(carpeta_docs)
    chunks = dividir_documentos(documentos)
    vector_store = crear_vector_store(chunks, embeddings)
    memoria = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
        k=5
    )
    print("Agente personalizado listo.")
    return crear_cadena(vector_store, memoria)

def hacer_pregunta(agente, pregunta: str) -> dict:
    try:
        resultado = agente.invoke({"question": pregunta})
        return {
            "result": resultado["answer"],
            "source_documents": resultado.get("source_documents", [])
        }
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise e