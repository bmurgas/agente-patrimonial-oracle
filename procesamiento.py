import os
from pypdf import PdfReader

# Carpeta local temporal para guardar los documentos
DIRECTORIO_DATOS = "datos_agente"

def guardar_archivos_localmente(archivos_subidos):
    """Guarda los archivos subidos desde la interfaz en el servidor local."""
    # Si no existe la carpeta, la creamos
    if not os.path.exists(DIRECTORIO_DATOS):
        os.makedirs(DIRECTORIO_DATOS)
    
    rutas_guardadas = []
    for archivo in archivos_subidos:
        ruta_completa = os.path.join(DIRECTORIO_DATOS, archivo.name)
        # Escribimos el archivo en el disco duro
        with open(ruta_completa, "wb") as f:
            f.write(archivo.getbuffer())
        rutas_guardadas.append(ruta_completa)
        
    return rutas_guardadas

def extraer_texto_pdf(ruta_archivo):
    """Lee un PDF y extrae su texto."""
    texto_completo = ""
    try:
        lector = PdfReader(ruta_archivo)
        for pagina in lector.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto_completo += texto_pagina + "\n"
        return texto_completo
    except Exception as e:
        return f"Error al leer {ruta_archivo}: {str(e)}"