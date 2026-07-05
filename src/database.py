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