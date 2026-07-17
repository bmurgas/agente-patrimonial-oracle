import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
import os
import zipfile
import fiona
from pyproj import CRS, Transformer
import html

fiona.drvsupport.supported_drivers['KML'] = 'rw'

def convertir_utm_a_latlon(x, y, huso):
    crs_utm = CRS.from_string(f"+proj=utm +zone={huso} +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    crs_latlon = CRS.from_epsg(4326)
    transformer = Transformer.from_crs(crs_utm, crs_latlon, always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lat, lon

def cargar_datos_monumentos():
    try:
        df_arq = pd.read_excel("Monumentos_arqueológicos.xls")
        df_arq = df_arq.dropna(subset=['COORD_GEO_LATITUD', 'COORD_GEO_LONGITUD'])
        df_arq['tipo_monumento'] = 'Arqueológico'
        df_arq = df_arq.rename(columns={'NOMBRE': 'nombre', 'COORD_GEO_LATITUD': 'lat', 'COORD_GEO_LONGITUD': 'lon', 'CATEGORIA_MONUM_ARQUEOLOGICO': 'categoria'})
        
        df_nac = pd.read_excel("Puntos_Monumentos_Nacionales.xlsx")
        df_nac = df_nac.dropna(subset=['lat', 'long'])
        df_nac['tipo_monumento'] = 'Nacional'
        df_nac = df_nac.rename(columns={'long': 'lon'}) 
        
        columnas = ['nombre', 'tipo_monumento', 'categoria', 'lat', 'lon']
        df_completo = pd.concat([df_arq[[c for c in columnas if c in df_arq.columns]], df_nac[[c for c in columnas if c in df_nac.columns]]], ignore_index=True)
        
        geometria = [Point(xy) for xy in zip(df_completo.lon, df_completo.lat)]
        gdf = gpd.GeoDataFrame(df_completo, geometry=geometria, crs="EPSG:4326")
        return gdf
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        return None

def analizar_entorno(lat, lon, radio_km, tipo_filtro="ambos"):
    gdf_monumentos = cargar_datos_monumentos()
    if gdf_monumentos is None:
        return None, None, None, "Error leyendo las bases de datos de monumentos."

    # APLICAR EL FILTRO SOLICITADO POR LA IA
    if tipo_filtro == 'nacional':
        gdf_monumentos = gdf_monumentos[gdf_monumentos['tipo_monumento'] == 'Nacional']
    elif tipo_filtro == 'arqueologico':
        gdf_monumentos = gdf_monumentos[gdf_monumentos['tipo_monumento'] == 'Arqueológico']

    if gdf_monumentos.empty:
        return None, None, None, f"No hay monumentos de ese tipo registrados en la base de datos."

    punto_centro = Point(lon, lat)
    gdf_centro = gpd.GeoDataFrame({'geometry': [punto_centro]}, crs="EPSG:4326")
    utm_crs = gdf_centro.estimate_utm_crs() 
    gdf_centro_utm = gdf_centro.to_crs(utm_crs)
    gdf_monumentos_utm = gdf_monumentos.to_crs(utm_crs)
    
    radio_metros = radio_km * 1000
    buffer = gdf_centro_utm.geometry.buffer(radio_metros).iloc[0]
    monumentos_cercanos = gdf_monumentos_utm[gdf_monumentos_utm.geometry.within(buffer)].copy()
    
    if monumentos_cercanos.empty:
        return None, None, None, f"No se encontraron resultados para tu solicitud en un radio de {radio_km}km."
        
    # --- 1. EXCEL ---
    monumentos_cercanos['UTM_Este (X)'] = monumentos_cercanos.geometry.x.round(2)
    monumentos_cercanos['UTM_Norte (Y)'] = monumentos_cercanos.geometry.y.round(2)
    monumentos_cercanos['Huso_UTM'] = utm_crs.name
    monumentos_cercanos['Latitud'] = monumentos_cercanos['lat']
    monumentos_cercanos['Longitud'] = monumentos_cercanos['lon']
    
    columnas_exportar = ['nombre', 'tipo_monumento', 'categoria', 'Latitud', 'Longitud', 'UTM_Este (X)', 'UTM_Norte (Y)', 'Huso_UTM']
    ruta_excel = "resultados_espaciales.xlsx"
    monumentos_cercanos[columnas_exportar].to_excel(ruta_excel, index=False)
    
    monumentos_mapa = monumentos_cercanos.to_crs("EPSG:4326")

    # --- 2. KMZ CON ICONOS OFICIALES DE GOOGLE EARTH Y PUNTO CENTRAL ---
    ruta_kml = "temp_resultados.kml"
    ruta_kmz = "resultados_espaciales.kmz"
    
    kml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n<name>Resultados Patrimoniales</name>\n'
    
    # Añadimos un tercer estilo: una estrella amarilla para el punto central
    kml_content += '''
    <Style id="estilo_centro"><IconStyle><scale>1.5</scale><Icon><href>https://maps.google.com/mapfiles/kml/paddle/ylw-stars.png</href></Icon></IconStyle></Style>
    <Style id="estilo_nacional"><IconStyle><scale>1.2</scale><Icon><href>https://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png</href></Icon></IconStyle></Style>
    <Style id="estilo_arqueologico"><IconStyle><scale>1.2</scale><Icon><href>https://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href></Icon></IconStyle></Style>
    '''
    
    # 1. Dibujamos primero el Punto Central
    kml_content += f'<Placemark>\n  <name>Punto de Búsqueda (Origen)</name>\n  <styleUrl>#estilo_centro</styleUrl>\n'
    kml_content += f'  <Point><coordinates>{lon},{lat},0</coordinates></Point>\n</Placemark>\n'
    
    # 2. Dibujamos los monumentos encontrados
    for idx, row in monumentos_mapa.iterrows():
        estilo = "estilo_nacional" if row['tipo_monumento'] == 'Nacional' else "estilo_arqueologico"
        nombre_limpio = html.escape(str(row['nombre']))
        kml_content += f'<Placemark>\n  <name>{nombre_limpio}</name>\n  <styleUrl>#{estilo}</styleUrl>\n'
        kml_content += '  <ExtendedData>\n'
        for col in columnas_exportar:
            val_limpio = html.escape(str(row[col]))
            kml_content += f'    <Data name="{col}"><value>{val_limpio}</value></Data>\n'
        kml_content += f'  </ExtendedData>\n  <Point><coordinates>{row["lon"]},{row["lat"]},0</coordinates></Point>\n</Placemark>\n'
        
    kml_content += '</Document>\n</kml>'
    
    with open(ruta_kml, 'w', encoding='utf-8') as f: f.write(kml_content)
    with zipfile.ZipFile(ruta_kmz, 'w', zipfile.ZIP_DEFLATED) as zipf: zipf.write(ruta_kml, os.path.basename(ruta_kml))
    os.remove(ruta_kml)
    
    # --- 3. MAPA SATELITAL (FOLIUM) ---
    mapa = folium.Map(location=[lat, lon], zoom_start=13, tiles=None)
    folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satélite Esri').add_to(mapa)
    folium.Marker([lat, lon], popup="<b>PUNTO CENTRAL</b>", icon=folium.Icon(color='red', icon='star')).add_to(mapa)
    folium.Circle(location=[lat, lon], radius=radio_metros, color='white', weight=2, fill=True, fill_opacity=0.1).add_to(mapa)
    
    for idx, row in monumentos_mapa.iterrows():
        color_icono = 'blue' if row['tipo_monumento'] == 'Nacional' else 'orange'
        folium.Marker([row['lat'], row['lon']], popup=f"<b>{row['nombre']}</b><br>{row['tipo_monumento']}", icon=folium.Icon(color=color_icono, icon='info-sign')).add_to(mapa)
        
    ruta_mapa = "mapa_entorno.html"
    mapa.save(ruta_mapa)
    
    return ruta_excel, ruta_mapa, ruta_kmz, f"Filtro '{tipo_filtro}': Se encontraron {len(monumentos_cercanos)} resultados en {radio_km}km."