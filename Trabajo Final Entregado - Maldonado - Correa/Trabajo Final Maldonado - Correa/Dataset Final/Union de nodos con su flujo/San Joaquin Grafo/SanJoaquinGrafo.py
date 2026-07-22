import osmnx as ox
import pandas as pd
import numpy as np

# ----------------------------
# 1. Descargar la red vial
# ----------------------------
G = ox.graph_from_place("San Joaquin County, California, USA", network_type="drive")

gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

# ----------------------------
# 2. Configuración de consumo
# ----------------------------
consumo_kwh_km = 0.2  # Consumo promedio EV: 0.2 kWh/km

# ----------------------------
# 3. Convertir grafo a GeoDataFrames
# ----------------------------
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

# ----------------------------
# 4. Filtrar solo aristas que son "ruta"
# ----------------------------
def es_ruta(highway):
    if isinstance(highway, list):
        highway = highway[0]
    return highway in ['primary','secondary','tertiary','trunk','motorway']

gdf_edges_ruta = gdf_edges[gdf_edges['highway'].apply(es_ruta)]

# ----------------------------
# 5. Extraer solo nodos que pertenecen a estas aristas
# En OSMnx moderno, los nodos están en el MultiIndex del GeoDataFrame de aristas
# ----------------------------
nodos_en_ruta = pd.unique(np.concatenate([
    gdf_edges_ruta.index.get_level_values(0).values,
    gdf_edges_ruta.index.get_level_values(1).values
]))
gdf_nodes_ruta = gdf_nodes.loc[nodos_en_ruta]

# ----------------------------
# 6. Reconstruir subgrafo solo con rutas y nodos involucrados
# ----------------------------
G_ruta = ox.graph_from_gdfs(gdf_nodes_ruta, gdf_edges_ruta)

# ----------------------------
# 7. Graficar subgrafo de rutas
# ----------------------------
ox.plot_graph(G_ruta, node_size=10, edge_color='red')

# ----------------------------
# 8. Crear lista de nodos de subgrafo
# ----------------------------
nodos = list(G_ruta.nodes)
n = len(nodos)
indice_nodo = {nodo: i for i, nodo in enumerate(nodos)}

# ----------------------------
# 9. Inicializar matriz de distancia solo para rutas
# ----------------------------
matriz_distancia_ruta = np.full((n, n), np.inf)

for u, v, attr in G_ruta.edges(data=True):
    i = indice_nodo[u]
    j = indice_nodo[v]
    length_m = attr.get('length', 0)
    matriz_distancia_ruta[i, j] = round(length_m, 1)

# ----------------------------
# 10. Guardar matriz de distancia filtrada
# ----------------------------
df_distancia_ruta = pd.DataFrame(matriz_distancia_ruta, index=nodos, columns=nodos)
df_distancia_ruta.to_csv("matriz_distancia_ruta.csv")

print("Matriz de distancia solo rutas generada:")
print(f"- matriz_distancia_ruta.csv ({df_distancia_ruta.shape})")
