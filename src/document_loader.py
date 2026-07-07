# document_loader.py - Carga y procesamiento de documentos PDF
import os
import pandas as pd
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import glob

def cargar_documentos(carpeta_docs: str) -> list:
    """Carga todos los PDFs de la carpeta docs/"""
    documentos = []
    for archivo in os.listdir(carpeta_docs):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(carpeta_docs, archivo)
            print(f"Cargando: {archivo}")
            loader = PyPDFLoader(ruta)
            documentos.extend(loader.load())
    for csv_path in glob.glob(os.path.join(carpeta_docs, "*.csv")):
        documentos.extend(cargar_csv(csv_path))
    print(f"Total de páginas cargadas: {len(documentos)}")
    return documentos

def dividir_documentos(documentos: list) -> list:
    """Divide los documentos en chunks para el vector store"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = splitter.split_documents(documentos)
    print(f"Total de chunks generados: {len(chunks)}")
    return chunks

def cargar_csv(ruta: str) -> list:
    # 🌟 sep=None y engine='python' detectan automáticamente si usa , o ;
    df = pd.read_csv(ruta, sep=None, engine='python')
    documentos = []
    for i, row in df.iterrows():
        contenido = " | ".join([f"{col}: {val}" for col, val in row.items()])
        documentos.append(Document(
            page_content=contenido,
            metadata={"source": ruta, "page": i}
        ))
    return documentos
