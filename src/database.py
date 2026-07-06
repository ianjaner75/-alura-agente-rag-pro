# database.py - Gestión de chats con Supabase
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def crear_chat(titulo: str, modo: str) -> str:
    client = get_client()
    result = client.table("chats").insert({
        "titulo": titulo,
        "modo": modo
    }).execute()
    return result.data[0]["id"]

def obtener_chats() -> list:
    client = get_client()
    result = client.table("chats").select("*").order("actualizado_at", desc=True).execute()
    return result.data

def obtener_mensajes(chat_id: str) -> list:
    client = get_client()
    result = client.table("mensajes").select("*").eq("chat_id", chat_id).order("creado_at").execute()
    return result.data

def guardar_mensaje(chat_id: str, rol: str, contenido: str, fuentes: list = []):
    client = get_client()
    client.table("mensajes").insert({
        "chat_id": chat_id,
        "rol": rol,
        "contenido": contenido,
        "fuentes": fuentes
    }).execute()
    client.table("chats").update({
        "actualizado_at": "now()"
    }).eq("id", chat_id).execute()

def eliminar_chat(chat_id: str):
    client = get_client()
    client.table("chats").delete().eq("id", chat_id).execute()

def renombrar_chat(chat_id: str, nuevo_titulo: str):
    client = get_client()
    client.table("chats").update({
        "titulo": nuevo_titulo
    }).eq("id", chat_id).execute()
    
import uuid

def subir_pdf_supabase(nombre_archivo: str, contenido_bytes: bytes) -> str:
    """Sube un PDF a Supabase Storage y retorna la URL pública"""
    import re
    client = get_client()
    # Limpiar nombre: quitar tildes, espacios y caracteres especiales
    nombre_limpio = nombre_archivo.encode('ascii', 'ignore').decode('ascii')
    nombre_limpio = re.sub(r'[^a-zA-Z0-9._-]', '_', nombre_limpio)
    nombre_unico = f"{uuid.uuid4()}_{nombre_limpio}"
    client.storage.from_("documentos").upload(
        path=nombre_unico,
        file=contenido_bytes,
        file_options={"content-type": "application/pdf"}
    )
    url = client.storage.from_("documentos").get_public_url(nombre_unico)
    return url, nombre_unico

def listar_pdfs_chat(chat_id: str) -> list:
    """Lista los PDFs asociados a un chat"""
    client = get_client()
    result = client.table("chats").select("archivos").eq("id", chat_id).execute()
    if result.data and result.data[0].get("archivos"):
        return result.data[0]["archivos"]
    return []

def asociar_archivos_chat(chat_id: str, archivos: list):
    """Guarda la lista de archivos asociados al chat"""
    client = get_client()
    client.table("chats").update({"archivos": archivos}).eq("id", chat_id).execute()