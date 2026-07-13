import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()
DIRECTORIO_VECTOR = "base_vectorial"

def buscar_contexto(consulta):
    """Busca fragmentos relevantes en la base vectorial."""
    if not os.path.exists(DIRECTORIO_VECTOR):
        return ""
        
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    vectorstore = Chroma(persist_directory=DIRECTORIO_VECTOR, embedding_function=embeddings)
    resultados = vectorstore.similarity_search(consulta, k=3)
    
    contexto = ""
    for res in resultados:
        contexto += res.page_content + "\n\n"
        
    return contexto

def procesar_consulta(mensaje, historial=[]):
    """Genera una respuesta considerando el historial y los documentos."""
    try:
        llm = ChatCohere(model="command-a-03-2025") 
        contexto_documentos = buscar_contexto(mensaje)
        
        # 1. Creamos la instrucción de sistema base (Instrucciones estrictas y Contexto)
        instruccion_sistema = f"""
        Eres un experto patrimonial y territorial. Responde la consulta basándote en la siguiente información de los documentos proporcionados.
        Si la información no está en el contexto, indícalo claramente.
        Debes incluir la cita inmediatamente después del párrafo donde se haya utilizado la información extraída, y luego añadirla en una bibliografía final.
        
        CONTEXTO DE DOCUMENTOS:
        {contexto_documentos}
        """
        
        # 2. Armamos la lista de mensajes empezando por la instrucción de sistema
        mensajes_langchain = [SystemMessage(content=instruccion_sistema)]
        
        # 3. Agregamos el historial previo a la memoria del modelo
        for msg in historial:
            if msg["role"] == "user":
                mensajes_langchain.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                mensajes_langchain.append(AIMessage(content=msg["content"]))
                
        # 4. Finalmente, agregamos el mensaje actual del usuario
        mensajes_langchain.append(HumanMessage(content=mensaje))
        
        # Generamos la respuesta
        respuesta = llm.invoke(mensajes_langchain)
        return respuesta.content
    except Exception as e:
        return f"Error al conectar con la IA: {str(e)}"