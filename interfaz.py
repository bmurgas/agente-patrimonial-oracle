import streamlit as st
import procesamiento
import logica_ia 

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
                with st.spinner("Procesando y vectorizando documentos..."):
                    rutas = procesamiento.guardar_archivos_localmente(archivos_subidos)
                    exito = procesamiento.procesar_y_vectorizar(rutas)
                    
                    if exito:
                        st.success(f"¡Se procesaron y guardaron {len(archivos_subidos)} archivos en la memoria del Agente!")
                    else:
                        st.error("No se pudo procesar el texto de los documentos.")
            else:
                st.warning("Por favor, sube un archivo primero.")
                
        st.divider()
        
        # NUEVO: Botón para reiniciar el chat
        if st.button("🗑️ Limpiar Conversación"):
            st.session_state.mensajes = []
            st.rerun() # Fuerza a recargar la página para limpiar la pantalla
            
        st.info("Proyecto Final - Infraestructura Oracle Cloud")

def renderizar_chat():
    """Dibuja la zona principal de interacción con el agente."""
    st.title("🏛️ Agente Patrimonial e Inteligencia Territorial")
    st.write("Bienvenido. Este agente te ayudará a analizar normativas y generar información.")

    # 1. INICIALIZAR MEMORIA: Si es la primera vez que entra, creamos la lista vacía
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # 2. DIBUJAR HISTORIAL: Mostramos los mensajes guardados en pantalla
    for mensaje in st.session_state.mensajes:
        st.chat_message(mensaje["role"]).write(mensaje["content"])

    st.markdown("### Chat de Análisis")
    mensaje_usuario = st.chat_input("Ej: ¿Qué dice la ley 17.288 sobre los hallazgos no previstos?")

    if mensaje_usuario:
        # Mostramos lo que escribió el usuario ahora
        st.chat_message("user").write(mensaje_usuario)
        
        # Animación de "pensando"
        with st.chat_message("assistant"):
            with st.spinner("Buscando en documentos y analizando consulta..."):
                # Enviamos el mensaje Y el historial a nuestra lógica
                respuesta_ia = logica_ia.procesar_consulta(mensaje_usuario, st.session_state.mensajes)
                st.write(respuesta_ia)
        
        # 3. GUARDAR EN MEMORIA: Registramos esta interacción para el futuro
        st.session_state.mensajes.append({"role": "user", "content": mensaje_usuario})
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})