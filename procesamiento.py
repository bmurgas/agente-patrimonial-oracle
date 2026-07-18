import os
import tempfile
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

DIRECTORIO_VECTOR = "base_vectorial"

def guardar_archivos_localmente(archivos_subidos):
    rutas = []
    for archivo in archivos_subidos:
        ruta = os.path.join(tempfile.gettempdir(), archivo.name)
        with open(ruta, "wb") as f:
            f.write(archivo.getbuffer())
        rutas.append(ruta)
    return rutas

def procesar_y_vectorizar(rutas):
    try:
        documentos = []
        
        for ruta in rutas:
            ext = os.path.splitext(ruta)[1].lower()
            nombre_archivo = os.path.basename(ruta)
            
            # 1. PROCESAR PDF
            if ext == '.pdf':
                loader = PyPDFLoader(ruta)
                documentos.extend(loader.load())
                
            # 2. PROCESAR EXCEL (Optimizado para precisión vectorial - 1 fila = 1 documento)
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(ruta)
                
                for index, row in df.iterrows():
                    # Transformamos cada fila en una ficha descriptiva individual
                    fila_str = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                    
                    # Evitamos agregar filas completamente vacías
                    if fila_str.strip():
                        doc = Document(page_content=fila_str, metadata={"source": nombre_archivo})
                        documentos.append(doc)

        if not documentos:
            return False

        # Dividimos los textos largos (los del PDF, ya que las filas de Excel rara vez superan los 1000 caracteres)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        textos_divididos = text_splitter.split_documents(documentos)

        # LA MAGIA: Usamos un modelo local multi-idioma (Cero costo de API)
        embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        
        Chroma.from_documents(
            documents=textos_divididos,
            embedding=embeddings,
            persist_directory=DIRECTORIO_VECTOR
        )

        return True
        
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        return False