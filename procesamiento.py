import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

DIRECTORIO_DATOS = "datos_agente"
DIRECTORIO_VECTOR = "base_vectorial"

def guardar_archivos_localmente(archivos_subidos):
    if not os.path.exists(DIRECTORIO_DATOS):
        os.makedirs(DIRECTORIO_DATOS)
    
    rutas_guardadas = []
    for archivo in archivos_subidos:
        ruta_completa = os.path.join(DIRECTORIO_DATOS, archivo.name)
        with open(ruta_completa, "wb") as f:
            f.write(archivo.getbuffer())
        rutas_guardadas.append(ruta_completa)
        
    return rutas_guardadas

def procesar_y_vectorizar(rutas_archivos):
    """Extrae texto, lo divide y lo guarda en ChromaDB."""
    texto_completo = ""
    
    # 1. Extraer texto
    for ruta in rutas_archivos:
        if ruta.endswith('.pdf'):
            try:
                lector = PdfReader(ruta)
                for pagina in lector.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
            except Exception as e:
                print(f"Error leyendo {ruta}: {e}")
                
    if not texto_completo:
        return False

    # 2. Dividir el texto en "chunks" (pedazos manejables)
    divisor = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    fragmentos = divisor.split_text(texto_completo)

    # 3. Crear embeddings y guardar en ChromaDB
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    vectorstore = Chroma.from_texts(
        texts=fragmentos,
        embedding=embeddings,
        persist_directory=DIRECTORIO_VECTOR
    )
    
    return True