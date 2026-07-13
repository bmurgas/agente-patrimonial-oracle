import streamlit as st
import procesamiento # Conectamos con el motor de datos

def configurar_pagina():
    """Configura los parámetros básicos de la página web."""
    st.set_page_config(page_title="Agente Patrimonial AI", page_icon="🏛️", layout="wide")

def renderizar_sidebar():
    """Dibuja el panel lateral para la carga de archivos."""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/8200/8200839.png", width=100)
        st.title("Gestión de Datos")
        st.markdown("Sube aquí las leyes, normativas,etc.")
        
        archivos_subidos = st.file_uploader(
            "Subir Archivos (.pdf, .shp, .zip)", 
            type=["pdf", "shp", "shx", "dbf", "prj", "zip"],
            accept_multiple_files=True
        )
        
        if st.button("Procesar Archivos"):
            if archivos_subidos:
                # Animación de carga mientras procesa
                with st.spinner("Procesando documentos..."):
                    # 1. Guardar archivos físicamente
                    rutas = procesamiento.guardar_archivos_localmente(archivos_subidos)
                    
                    # 2. Prueba rápida: Extraer texto del primer archivo (si es PDF)
                    primer_archivo = rutas[0]
                    if primer_archivo.endswith('.pdf'):
                        texto_extraido = procesamiento.extraer_texto_pdf(primer_archivo)
                        st.success(f"¡Se guardaron {len(archivos_subidos)} archivos con éxito!")
                        st.text_area("Vista previa del texto extraído:", texto_extraido[:800] + "...", height=200)
                    else:
                        st.success(f"¡Se guardaron {len(archivos_subidos)} archivos!")
                        st.info("Sube un documento PDF para probar la extracción de texto.")
            else:
                st.warning("Por favor, sube un archivo primero.")
                
        st.divider()
        st.info("Proyecto Final - Infraestructura Oracle Cloud")

def renderizar_chat():
    """Dibuja la zona principal de interacción con el agente."""
    st.title("🏛️ Agente Patrimonial e Inteligencia Territorial")
    st.write("Bienvenido. Este agente te ayudará a analizar normativas y generar información.")

    st.markdown("### Chat de Análisis")
    mensaje_usuario = st.chat_input("Ej: ¿Qué dice la ley 17.288 sobre los hallazgos no previstos?")

    if mensaje_usuario:
        st.write(f"**Tú:** {mensaje_usuario}")
        st.info("🤖 **Agente:** Conexión con IA pendiente...")