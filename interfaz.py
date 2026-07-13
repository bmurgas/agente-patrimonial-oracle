import streamlit as st

def configurar_pagina():
    """Configura los parámetros básicos de la página web."""
    st.set_page_config(page_title="Agente Patrimonial AI", page_icon="🏛️", layout="wide")

def renderizar_sidebar():
    """Dibuja el panel lateral para la carga de archivos."""
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/8200/8200839.png", width=100)
        st.title("Gestión de Datos")
        st.markdown("Sube aquí las normativas y shapefiles de la línea base.")
        
        archivos_subidos = st.file_uploader(
            "Subir Archivos (.pdf, .shp, .zip)", 
            type=["pdf", "shp", "shx", "dbf", "prj", "zip"],
            accept_multiple_files=True
        )
        
        if st.button("Procesar Archivos"):
            if archivos_subidos:
                st.success(f"{len(archivos_subidos)} archivo(s) listo(s) para procesar.")
                # Aquí conectaremos con procesamiento.py más adelante
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
        # Aquí conectaremos con logica_ia.py más adelante
        st.info("🤖 **Agente:** Conexión con IA pendiente...")