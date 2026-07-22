import os
import sys
import argparse
import geopandas as gpd
import pandas as pd

# --- CONFIGURACIÓN ---
RUTA_CALTRANS = 'Annual_Average_Daily_Traffic.geojson'
CODIGO_TULARE = 'TUL'
UMBRAL_ADT = 2500

COL_ADT_CALTRANS = 'BACK_AADT'
COL_CONDADO = 'COUNTY'
# ----------------------


def find_file(path, max_up=3):
    """Intentar resolver la ruta probando varias ubicaciones.

    Devuelve la ruta absoluta si se encuentra, o None si no.
    """
    # Ruta absoluta explícita
    if os.path.isabs(path) and os.path.exists(path):
        return os.path.abspath(path)

    # Ruta relativa desde cwd
    if os.path.exists(path):
        return os.path.abspath(path)

    # Ruta relativa al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, path)
    if os.path.exists(candidate):
        return os.path.abspath(candidate)

    # Buscar subiendo jerarquía desde el directorio del script
    p = script_dir
    for _ in range(max_up):
        candidate = os.path.join(p, path)
        if os.path.exists(candidate):
            return os.path.abspath(candidate)
        p = os.path.dirname(p)

    return None


def main():
    parser = argparse.ArgumentParser(description='Generar puntos y rutas filtradas desde un GeoJSON de Caltrans')
    parser.add_argument('-i', '--input', default=RUTA_CALTRANS, help='Ruta al archivo Annual_Average_Daily_Traffic.geojson (absoluta o relativa)')
    args = parser.parse_args()

    ruta = args.input
    encontrada = find_file(ruta)
    attempted = [
        os.path.abspath(ruta) if os.path.exists(ruta) else None,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta),
    ]

    if encontrada is None:
        print('❌ No se encontró el archivo de entrada.')
        print(f'Busqué en (ejemplos):')
        print(f'  - ruta tal como la pasaste: {os.path.abspath(ruta) if ruta else ruta}')
        print(f'  - en el directorio del script: {os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta)}')
        print('\nSoluciones:')
        print('  1) Coloca "Annual_Average_Daily_Traffic.geojson" en el mismo directorio que este script.')
        print('  2) Ejecuta el script pasando la ruta completa:')
        print('       python generador_puntos_rutas_estatales.py -i "C:\\ruta\\a\\Annual_Average_Daily_Traffic.geojson"')
        print('  3) Asegúrate de no tener errores tipográficos en la ruta o en el nombre de la carpeta (por ejemplo ".CURSANDO" vs ".CURSSANDO").')
        sys.exit(2)

    try:
        # 1️⃣ CARGA DEL DATASET CALTRANS
        gdf_caltrans = gpd.read_file(encontrada).to_crs(epsg=4326)

        # Filtrar solo Tulare County
        if COL_CONDADO in gdf_caltrans.columns:
            gdf_caltrans = gdf_caltrans[
                gdf_caltrans[COL_CONDADO].astype(str).str.strip() == CODIGO_TULARE
            ]

        # Filtrar por ADT mínimo
        gdf_caltrans['ADT'] = pd.to_numeric(gdf_caltrans[COL_ADT_CALTRANS], errors='coerce')
        gdf_caltrans = gdf_caltrans[gdf_caltrans['ADT'] >= UMBRAL_ADT].copy()
        print(f"Puntos/rutas Caltrans Tulare (ADT ≥ {UMBRAL_ADT}): {len(gdf_caltrans)}")

        # 2️⃣ PREPARAR PUNTOS
        gdf_puntos = gdf_caltrans[['ADT', 'geometry']].copy()
        gdf_puntos['Tipo_Candidato'] = 'Flujo_Caltrans'
        gdf_puntos['Longitud'] = gdf_puntos.geometry.x
        gdf_puntos['Latitud'] = gdf_puntos.geometry.y

        # 3️⃣ EXPORTAR GEOJSON
        out_rutas = 'rutas_finales_TUL_Caltrans.geojson'
        out_puntos = 'puntos_finales_TUL_Caltrans.geojson'
        gdf_caltrans[['ADT', 'geometry']].to_file(out_rutas, driver='GeoJSON')
        gdf_puntos.to_file(out_puntos, driver='GeoJSON')

        print(f"✅ Exportación completada: {len(gdf_caltrans)} rutas y {len(gdf_puntos)} puntos para Tulare.")

    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
