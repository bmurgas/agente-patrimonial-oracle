import interfaz

def main():
    # 1. Configuramos la ventana
    interfaz.configurar_pagina()
    
    # 2. Dibujamos el panel lateral
    interfaz.renderizar_sidebar()
    
    # 3. Dibujamos la pantalla principal
    interfaz.renderizar_chat()

if __name__ == "__main__":
    main()
