# document_loader.py - Carga y procesamiento de documentos PDF
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def cargar_documentos(carpeta_docs: str) -> list:
    """Carga todos los PDFs de la carpeta docs/"""
    documentos = []
    for archivo in os.listdir(carpeta_docs):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(carpeta_docs, archivo)
            print(f"Cargando: {archivo}")
            loader = PyPDFLoader(ruta)
            documentos.extend(loader.load())
    print(f"Total de páginas cargadas: {len(documentos)}")
    return documentos

def dividir_documentos(documentos: list) -> list:
    """Divide los documentos en chunks para el vector store"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = splitter.split_documents(documentos)
    print(f"Total de chunks generados: {len(chunks)}")
    return chunks
