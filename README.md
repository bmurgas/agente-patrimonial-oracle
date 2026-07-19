# 🏛️ Agente Patrimonial e Inteligencia Territorial

¡Bienvenido al repositorio del **Agente Patrimonial AI**! Este proyecto es un asistente conversacional avanzado, diseñado específicamente para facilitar la labor de revisión, edición y consulta de informes patrimoniales y arqueológicos.

A través del uso de Inteligencia Artificial (LLMs) y análisis espacial (GIS), esta herramienta permite "conversar" con normativas legales (PDFs) y bases de datos de monumentos (Excel), garantizando respuestas con rigor académico y visualizaciones geográficas precisas.

---

## ✨ Características Principales

* **📖 Búsqueda Teórica y Conceptual (RAG):** Sube leyes, normativas o artículos en PDF. La IA responderá a tus preguntas conceptuales basándose *exclusivamente* en esos documentos, parafraseando la información e incluyendo la cita bibliográfica exacta al final de cada respuesta.
* **📊 Exploración de Bases de Datos:** Transforma filas de Excel en conocimiento consultable. Si buscas un monumento con el nombre incompleto, el sistema utilizará búsqueda difusa (vectores) para sugerirte el registro más similar y entregarte toda su ficha técnica.
* **🌍 Análisis Espacial Inteligente:** Si le proporcionas una coordenada exacta (ej: `-33.45, -70.66`), la IA activará sus herramientas cartográficas para buscar monumentos en un radio determinado, generando al instante:
* Un mapa interactivo (`.html`).
* Un archivo para Google Earth (`.kmz`).
* Una tabla consolidada con los resultados (`.xlsx`).


* **⚙️ Optimizado para Servidores Pequeños:** La arquitectura está diseñada para ejecutarse en entornos con recursos limitados (como la capa gratuita de Oracle Cloud), procesando datos de forma local por lotes para evitar desbordes de memoria.

---

## 🧩 Arquitectura del Proyecto

El sistema está dividido en módulos especializados para mantener el código limpio y escalable:

* **`app.py` & `interfaz.py`:** La cara visible de la aplicación. Utilizan *Streamlit* para renderizar el panel lateral de subida de archivos, el chat interactivo y los botones de descarga del historial cartográfico.
* **`procesamiento.py`:** El bibliotecario. Se encarga de leer los PDFs y los archivos Excel (indexando estos últimos fila por fila). Utiliza *HuggingFaceEmbeddings* (modelo `paraphrase-multilingual-MiniLM-L12-v2`) configurado con `batch_size=4` para generar vectores matemáticos sin saturar la RAM del servidor, guardándolos en *ChromaDB*.
* **`logica_ia.py`:** El cerebro académico. Conecta el modelo de lenguaje de *Cohere* (`command-a-03-2025`) con Langchain. Contiene las "Reglas de Comportamiento" estrictas que evitan que la IA invente datos (alucinaciones) y gestionan cuándo activar las herramientas de mapas.
* **`geo_analisis.py`:** El cartógrafo. Utiliza *Geopandas* y *Folium* para transformar las coordenadas UTM/LatLon, medir distancias, cruzar información con las bases de datos maestras y dibujar los mapas interactivos y archivos KMZ.

---

## 🚀 Guía de Instalación y Despliegue

Sigue estos pasos para levantar el proyecto desde cero, especialmente si utilizas un servidor Linux en la nube (como Ubuntu).

### 1. Preparar el Entorno

Clona este repositorio y navega hasta la carpeta del proyecto. Luego, instala las herramientas básicas de Python y entornos virtuales:

```bash
sudo apt-get update
sudo apt-get install python3-venv python3-pip tmux -y

```

### 2. Crear y Activar el Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Instalar Dependencias

Instala todas las librerías necesarias especificadas en el archivo `requirements.txt`:

```bash
pip install -r requirements.txt

```

### 4. Configurar Variables de Entorno

Crea un archivo llamado `.env` en la raíz del proyecto y agrega tu clave de API de Cohere:

```text
COHERE_API_KEY=tu_clave_secreta_aqui

```

### 5. Despliegue Seguro (Evitando Caídas)

Para servidores en la nube, es vital usar `tmux`. Esto crea una sesión a prueba de cortes de internet, asegurando que si la conexión SSH se cae mientras la IA procesa un Excel gigante, el servidor siga trabajando en segundo plano sin arrojar errores (como *Connection reset* o *Segmentation fault*).

```bash
# 1. Abre una terminal blindada
tmux

# 2. Activa el entorno
source venv/bin/activate

# 3. Limita la saturación del procesador para procesos locales
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false

# 4. Inicia la aplicación
python -m streamlit run app.py

```

*Tip: Puedes salir de `tmux` cerrando tu terminal tranquilamente. Para volver a ver la aplicación corriendo en tu servidor, conéctate por SSH y escribe `tmux attach`.*

---

## 💡 Cómo Utilizar el Agente

Una vez que la aplicación esté corriendo (usualmente en `http://localhost:8501`), el flujo de trabajo es el siguiente:

1. **Cargar Conocimiento:** En el panel lateral, sube tus normativas (PDF) y tu base de datos de monumentos (Excel). Haz clic en "Procesar Archivos".
2. **Consultas Teóricas:** Pregunta directamente.
* *Ejemplo:* *"¿Qué se entiende por monumento arqueológico según la normativa?"*
* *Ejemplo:* *"¿Qué información tenemos del Torreón Los Canelos?"*


3. **Análisis Territorial:** Para que la IA genere mapas, **debes incluir coordenadas numéricas**.
* *Ejemplo:* *"Busca monumentos arqueológicos a 5km de la coordenada -33.45, -70.66"*



### Notas sobre los Datos Maestros

El módulo espacial (`geo_analisis.py`) asume la existencia de dos bases de datos locales en la raíz del proyecto para funcionar correctamente:

* `Monumentos_arqueológicos.xls`
* `Puntos_Monumentos_Nacionales.xlsx`