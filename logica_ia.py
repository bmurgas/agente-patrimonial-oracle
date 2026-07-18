import os
from dotenv import load_dotenv
from langchain_cohere import ChatCohere, CohereEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
import geo_analisis

load_dotenv()
DIRECTORIO_VECTOR = "base_vectorial"

@tool
def herramienta_buscar_monumentos(lat: float, lon: float, radio_km: float = 5.0, tipo_filtro: str = "ambos") -> dict:
    """
    Busca sitios patrimoniales cerca de una coordenada.
    - Usa tipo_filtro="ambos" si el usuario solo dice "monumentos" o no especifica.
    - Usa tipo_filtro="nacional" si el usuario pide explícitamente "monumentos nacionales".
    - Usa tipo_filtro="arqueologico" si el usuario pide explícitamente "monumentos arqueológicos" o "sitios arqueológicos".
    """
    ruta_excel, ruta_mapa, ruta_kmz, mensaje = geo_analisis.analizar_entorno(lat, lon, radio_km, tipo_filtro)
    return {"excel": ruta_excel, "mapa": ruta_mapa, "kmz": ruta_kmz, "mensaje": mensaje}

def buscar_contexto(consulta):
    if not os.path.exists(DIRECTORIO_VECTOR):
        return ""
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma(persist_directory=DIRECTORIO_VECTOR, embedding_function=embeddings)
    
    # 1. Detectar si la pregunta es teórica/conceptual para Andrea
    palabras_teoricas = ["qué es", "que es", "qué se entiende", "que se entiende", "define", "definicion", "ley", "normativa", "articulo", "hallazgo"]
    es_pregunta_teorica = any(palabra in consulta.lower() for palabra in palabras_teoricas)
    
    # 2. Búsqueda inteligente: si es teórica, traemos MENOS fragmentos (k=15) pero más precisos. 
    # Si quisieras filtrar solo PDFs, aquí usarías filter={"source": "ruta_al_pdf"}, 
    # pero como no sabemos el nombre exacto de tu PDF, usaremos una técnica de "densidad".
    # Al pedir menos fragmentos (k=15), obligamos al modelo a buscar las coincidencias más densas
    # de significado (las definiciones) en lugar de repetir 50 filas de Excel vacías.
    
    # Aumentamos a 80 para atrapar coincidencias parciales que queden más abajo en el ranking vectorial
    k_busqueda = 15 if es_pregunta_teorica else 80
    
    resultados = vectorstore.similarity_search(consulta, k=k_busqueda) 
    
    contexto = ""
    for res in resultados:
        # Limpieza brutal de basura visual (esto detiene los bucles <co>)
        texto_limpio = res.page_content.replace("<co>", "").replace("</co>", "").replace("[", "").replace("]", "")
        contexto += texto_limpio + "\n\n"
        
    return contexto

def procesar_consulta(mensaje, historial=[]):
    try:
        # Usamos el modelo ideal para agentes y RAG
        llm = ChatCohere(model="command-a-03-2025") 
        llm_con_herramientas = llm.bind_tools([herramienta_buscar_monumentos])
        
        contexto_documentos = buscar_contexto(mensaje)
        
        # Seguro contra vacíos
        texto_contexto = contexto_documentos if len(contexto_documentos.strip()) > 10 else "No hay información en los documentos cargados."
        
        instruccion_sistema = f"""
        Eres un asistente académico avanzado y experto patrimonial. Tienes plena capacidad para leer textos legales y buscar registros en bases de datos.

        CONTEXTO DISPONIBLE (DOCUMENTOS Y TABLAS DEL USUARIO):
        {texto_contexto}

        REGLAS DE COMPORTAMIENTO (CUMPLE ESTRICTAMENTE):

        1. BÚSQUEDA DE DATOS Y CONCEPTOS:
        - Tu deber principal es responder a la consulta basándote EXCLUSIVAMENTE en el CONTEXTO DISPONIBLE proporcionado arriba.
        - Si la pregunta es sobre registros (ej: "¿Existe la iglesia X?"), busca en el contexto y entrega los datos tal como aparecen.
        - Si la pregunta es conceptual, redacta una explicación basada solo en el contexto, coloca la cita inmediatamente después del párrafo y asegúrate de incluirla en la bibliografía final.
        
        2. MANEJO DE NOMBRES INCOMPLETOS O SIMILARES:
        - Si el usuario busca un nombre (ej: "Casa cuna Arturo Prat") y no encuentras una coincidencia exacta, BUSCA en el contexto si existe algún registro que contenga parte de esas palabras (ej: "Casa cuna de Arturo Prat y terrenos adyacentes").
        - Si encuentras algo similar, entrégale la información al usuario pero adviértele primero: "No encontré el registro exacto, pero encontré este muy similar que podría ser lo que buscas: [Nombre del registro]".
        
        3. CUANDO NO HAY NADA:
        - Si la respuesta NO está en el contexto y tampoco hay nada parecido, TIENES PROHIBIDO usar conocimiento externo. En su lugar, DEBES responder exactamente: "No encontré información sobre esta solicitud en los documentos cargados." (Nunca devuelvas una respuesta vacía).

        4. PREGUNTAS GEOGRÁFICAS Y MAPAS:
        - SOLO si el usuario escribe coordenadas numéricas exactas (ej: -33.45, -70.66), ejecuta la 'herramienta_buscar_monumentos'.
        - Si el mensaje del usuario NO contiene coordenadas, IGNORA tu herramienta de mapas.
        """
        
        mensajes_langchain = [SystemMessage(content=instruccion_sistema)]
        
        for msg in historial:
            if msg["role"] == "user":
                mensajes_langchain.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant" and msg["tipo"] == "texto":
                mensajes_langchain.append(AIMessage(content=msg["content"]))
                
        mensajes_langchain.append(HumanMessage(content=mensaje))
        respuesta = llm_con_herramientas.invoke(mensajes_langchain)
        
        if respuesta.tool_calls:
            for tool_call in respuesta.tool_calls:
                if tool_call["name"] == "herramienta_buscar_monumentos":
                    args = tool_call["args"]
                    resultado = herramienta_buscar_monumentos.invoke(args)
                    
                    return {
                        "tipo": "mapa",
                        "texto": resultado["mensaje"],
                        "excel": resultado["excel"],
                        "mapa": resultado["mapa"],
                        "kmz": resultado["kmz"]
                    }
                    
        return {"tipo": "texto", "texto": respuesta.content}
        
    except Exception as e:
        return {"tipo": "texto", "texto": f"Error al conectar con la IA: {str(e)}"}