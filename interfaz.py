import streamlit as st
import streamlit.components.v1 as components
import procesamiento
import logica_ia 

def configurar_pagina():
    st.set_page_config(page_title="Agente Patrimonial AI", page_icon="🏛️", layout="wide")

def renderizar_sidebar():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/8200/8200839.png", width=100)
        st.title("Gestión de Datos")
        st.markdown("Sube normativas (.pdf) o bases de datos (.xls, .xlsx).")
        
        archivos_subidos = st.file_uploader(
            "Subir Archivos", 
            type=["pdf", "xls", "xlsx"], 
            accept_multiple_files=True
        )
        
        if st.button("Procesar Archivos"):
            if archivos_subidos:
                with st.spinner("Procesando documentos..."):
                    rutas = procesamiento.guardar_archivos_localmente(archivos_subidos)
                    exito = procesamiento.procesar_y_vectorizar(rutas)
                    if exito:
                        st.success("Archivos procesados y vectorizados.")
                    else:
                        st.error("Error al procesar.")
                        
        st.divider()
        if st.button("🗑️ Limpiar Conversación"):
            st.session_state.mensajes = []
            st.rerun()

def dibujar_mensaje(mensaje, idx):
    """ESTO DIBUJA LOS MENSAJES ANTIGUOS (EL HISTORIAL)"""
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])
        
        if mensaje.get("tipo") == "mapa" and mensaje.get("mapa") is not None:
            try:
                # Dibujar mapa HTML
                with open(mensaje["mapa"], 'r', encoding='utf-8') as f:
                    components.html(f.read(), height=400)
                
                # Dibujar botones usando idx para evitar llaves duplicadas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    with open(mensaje["mapa"], "rb") as file:
                        st.download_button(
                            label="🗺️ Mapa HTML", 
                            data=file, 
                            file_name=f"mapa_historial_{idx}.html", 
                            mime="text/html",
                            key=f"hist_mapa_{idx}"
                        )
                with col2:
                    # Buscamos la ruta del Excel de forma robusta
                    ruta_excel = mensaje.get("excel") or mensaje.get("archivo")
                    if ruta_excel:
                        with open(ruta_excel, 'rb') as f:
                            st.download_button(
                                label="📊 Descargar Excel", 
                                data=f, 
                                file_name="resultados.xlsx", 
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                                key=f"hist_excel_{idx}"
                            )
                with col3:
                    if mensaje.get("kmz"):
                        with open(mensaje["kmz"], 'rb') as f:
                            st.download_button(
                                label="🌍 Descargar KMZ", 
                                data=f, 
                                file_name="resultados.kmz", 
                                mime="application/vnd.google-earth.kmz", 
                                key=f"hist_kmz_{idx}"
                            )
            except Exception as e:
                st.error(f"Error cargando archivos del historial: {str(e)}")

def renderizar_chat():
    st.title("🏛️ Agente Patrimonial e Inteligencia Territorial")
    
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Dibuja el historial enviando el índice (enumerate)
    for idx, mensaje in enumerate(st.session_state.mensajes):
        dibujar_mensaje(mensaje, idx)

    mensaje_usuario = st.chat_input("Ej: Busca monumentos a 5km de la coordenada -33.45, -70.66")

    if mensaje_usuario:
        msg_user = {"role": "user", "content": mensaje_usuario, "tipo": "texto"}
        st.session_state.mensajes.append(msg_user)
        st.chat_message("user").write(mensaje_usuario)
        
        with st.chat_message("assistant"):
            with st.spinner("Analizando requerimiento..."):
                respuesta_dict = logica_ia.procesar_consulta(mensaje_usuario, st.session_state.mensajes)
                
                msg_assistant = {
                    "role": "assistant", 
                    "content": respuesta_dict["texto"], 
                    "tipo": respuesta_dict["tipo"]
                }
                
                # GUARDADO EN HISTORIAL CORREGIDO:
                if respuesta_dict["tipo"] == "mapa":
                    msg_assistant["excel"] = respuesta_dict.get("excel") or respuesta_dict.get("archivo")
                    msg_assistant["mapa"] = respuesta_dict.get("mapa")
                    msg_assistant["kmz"] = respuesta_dict.get("kmz")
                    
                st.session_state.mensajes.append(msg_assistant)
                
                st.write(respuesta_dict["texto"])
                
                # ESTO DIBUJA EL MENSAJE "EN VIVO"
                if respuesta_dict["tipo"] == "mapa":
                    if respuesta_dict.get("mapa") is not None:
                        
                        with open(respuesta_dict["mapa"], 'r', encoding='utf-8') as f:
                            components.html(f.read(), height=400)
                            
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with open(respuesta_dict["mapa"], "rb") as file:
                                st.download_button(
                                    label="🗺️ Mapa HTML",
                                    data=file,
                                    file_name="map_resultado.html",
                                    mime="text/html"
                                )
                                
                        with col2:
                            ruta_excel = respuesta_dict.get("excel") or respuesta_dict.get("archivo")
                            if ruta_excel:
                                with open(ruta_excel, "rb") as file:
                                    st.download_button(
                                        label="📊 Datos Excel",
                                        data=file,
                                        file_name="datos_resultado.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                    
                        with col3:
                            if respuesta_dict.get("kmz"):
                                with open(respuesta_dict["kmz"], "rb") as file:
                                    st.download_button(
                                        label="🌍 Archivo KMZ",
                                        data=file,
                                        file_name="google_earth_resultado.kmz",
                                        mime="application/vnd.google-earth.kmz"
                                    )
                    else:
                        st.warning("⚠️ No se pudo generar el mapa. Verifica la ortografía y datos de búsqueda.")