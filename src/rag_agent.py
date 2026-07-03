# rag_agent.py - Lógica del agente RAG con LangChain y Gemini
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from document_loader import cargar_documentos, dividir_documentos

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

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
    print("Cargando documentos...")
    documentos = cargar_documentos(carpeta_docs)
    chunks = dividir_documentos(documentos)

    print("Creando embeddings y vector store...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    vector_store = FAISS.from_documents(chunks, embeddings)

    print("Configurando el agente...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

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
    """Hace una pregunta al agente y retorna la respuesta"""
    resultado = agente.invoke({"query": pregunta})
    return resultado["result"]
