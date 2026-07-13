import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage

load_dotenv()
DIRECTORIO_VECTOR = "base_vectorial"

def buscar_contexto(consulta):
    """Busca fragmentos relevantes en la base vectorial."""
    if not os.path.exists(DIRECTORIO_VECTOR):
        return ""
        
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    vectorstore = Chroma(persist_directory=DIRECTORIO_VECTOR, embedding_function=embeddings)
    
    # Busca los 3 fragmentos más relevantes
    resultados = vectorstore.similarity_search(consulta, k=3)
    
    contexto = ""
    for res in resultados:
        contexto += res.page_content + "\n\n"
        
    return contexto

def procesar_consulta(mensaje):
    """Genera una respuesta usando el contexto de los documentos."""
    try:
        llm = ChatCohere(model="command-a-03-2025") 
        
        # Primero buscamos en los documentos
        contexto_documentos = buscar_contexto(mensaje)
        
        # Armamos el "Prompt" (Instrucción) para la IA
        instruccion = f"""
        Eres un experto patrimonial y territorial. Responde la consulta del usuario basándote en la siguiente información de los documentos proporcionados.
        Si la información no está en el contexto, indícalo claramente.
        Debes incluir la cita inmediatamente después del párrafo donde se haya utilizado la información extraída, y luego añadirla en una bibliografía final. 
        
        CONTEXTO DE DOCUMENTOS:
        {contexto_documentos}
        
        CONSULTA DEL USUARIO: {mensaje}
        """
        
        mensajes = [HumanMessage(content=instruccion)]
        respuesta = llm.invoke(mensajes)
        
        return respuesta.content
    except Exception as e:
        return f"Error al conectar con la IA: {str(e)}"