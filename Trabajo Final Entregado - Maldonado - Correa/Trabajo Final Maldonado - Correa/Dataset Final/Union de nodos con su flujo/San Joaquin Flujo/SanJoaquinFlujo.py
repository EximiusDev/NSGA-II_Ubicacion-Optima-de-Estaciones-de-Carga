import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, MultiLineString

# --- CONFIGURACIÓN ---
RUTA_LOCAL = 'SJ_flujo.geojson'                     # Rutas locales (San Joaquin)
RUTA_CALTRANS = 'California_flujo.geojson'  # Puntos Caltrans

CODIGO_SJ = 'SJ'        # Filtrar Caltrans por SAN JOAQUIN
UMBRAL_ADT = 5000

COL_ADT_LOCAL = 'ADT'
COL_ADT_CALTRANS = 'BACK_AADT'
COL_CONDADO = 'COUNTY'
# ----------------------

def rutas_a_puntos_simplificado(gdf_rutas):
    """
    Convierte cada LineString o MultiLineString a puntos
    usando solo el inicio y fin de cada línea para reducir cantidad de puntos.
    """
    puntos = []

    for idx, row in gdf_rutas.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue

        if isinstance(geom, LineString):
            coords = [geom.coords[0], geom.coords[-1]]  # solo inicio y fin
        elif isinstance(geom, MultiLineString):
            coords = []
            for line in geom.geoms:
                coords.append(line.coords[0])
                coords.append(line.coords[-1])
        else:
            continue  # ignorar geometrías que no sean líneas

        for c in coords:
            puntos.append({
                'ADT': row.get(COL_ADT_LOCAL, None),
                'geometry': Point(c)
            })

    gdf_puntos = gpd.GeoDataFrame(puntos, geometry='geometry', crs=gdf_rutas.crs)
    return gdf_puntos

try:
    # 1️⃣ CARGA Y FILTRADO DE RUTAS LOCALES
    gdf_local = gpd.read_file(RUTA_LOCAL)
    gdf_local[COL_ADT_LOCAL] = pd.to_numeric(gdf_local[COL_ADT_LOCAL], errors='coerce')
    gdf_local = gdf_local.dropna(subset=[COL_ADT_LOCAL])
    gdf_local = gdf_local[gdf_local[COL_ADT_LOCAL] >= UMBRAL_ADT]

    # Convertir rutas a puntos simplificados
    gdf_puntos_local = rutas_a_puntos_simplificado(gdf_local)
    gdf_puntos_local['Tipo_Candidato'] = 'Flujo_Local'

    print(f"Puntos convertidos de rutas locales: {len(gdf_puntos_local)}")

    # 2️⃣ CARGA Y FILTRADO DE PUNTOS CALTRANS
    gdf_caltrans = gpd.read_file(RUTA_CALTRANS).to_crs(epsg=4326)
    if COL_CONDADO in gdf_caltrans.columns:
        gdf_caltrans = gdf_caltrans[gdf_caltrans[COL_CONDADO].astype(str).str.strip() == CODIGO_SJ]

    gdf_caltrans[COL_ADT_CALTRANS] = pd.to_numeric(gdf_caltrans[COL_ADT_CALTRANS], errors='coerce')
    gdf_caltrans = gdf_caltrans.dropna(subset=[COL_ADT_CALTRANS])
    gdf_caltrans['Tipo_Candidato'] = 'Flujo_Caltrans'

    print(f"Puntos Caltrans (SJ): {len(gdf_caltrans)}")

    # 3️⃣ UNIFICAR PUNTOS
    gdf_unificado = pd.concat([
        gdf_puntos_local[['geometry','ADT','Tipo_Candidato']],
        gdf_caltrans[['geometry', COL_ADT_CALTRANS, 'Tipo_Candidato']].rename(columns={COL_ADT_CALTRANS:'ADT'})
    ]).reset_index(drop=True)

    # Eliminar duplicados exactos de geometría
    gdf_unificado = gdf_unificado.drop_duplicates(subset=['geometry'])
    gdf_unificado['Longitud'] = gdf_unificado.geometry.x
    gdf_unificado['Latitud'] = gdf_unificado.geometry.y

    # 4️⃣ EXPORTAR GEOJSON UNIFICADO
    gdf_unificado.to_file('puntos_unificados_SJ.geojson', driver='GeoJSON')
    print(f"✅ Exportación completada: {len(gdf_unificado)} puntos unificados de San Joaquin.")

except Exception as e:
    print(f"❌ Error durante el procesamiento: {e}")
