import geopandas as gpd
import fiona

archivo = "dataset_final.gpkg"

# Listar capas
capas = fiona.listlayers(archivo)
print("Capas disponibles:")
print(capas)

# Cargar una capa y mostrar columnas
gdf = gpd.read_file(archivo, layer=capas[0])
print("Columnas de la capa:", gdf.columns.tolist())
print("Primeras filas:")
print(gdf.head())
