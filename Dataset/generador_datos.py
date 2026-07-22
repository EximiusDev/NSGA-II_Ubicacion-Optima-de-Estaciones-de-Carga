import osmnx as ox
import pandas as pd
import numpy as np

# ----------------------------
# 1. Descargar la red vial
# ----------------------------
G = ox.graph_from_place("Paraná, Entre Ríos, Argentina", network_type="drive")

ox.plot_graph(G)
# ----------------------------
# 2. Configuración de consumo
# ----------------------------
consumo_kwh_km = 0.2  # Consumo promedio EV: 0.2 kWh/km

# ----------------------------
# 3. Crear lista de nodos
# ----------------------------
nodos = list(G.nodes)
n = len(nodos)

# Crear diccionario para acceder al índice del nodo
indice_nodo = {nodo: i for i, nodo in enumerate(nodos)}

# ----------------------------
# 4. Inicializar matrices
# ----------------------------
# Distancia en metros
matriz_distancia = np.full((n, n), np.inf)
# Consumo en kWh
matriz_consumo = np.full((n, n), np.inf)
# Indicador es_ruta
matriz_es_ruta = np.zeros((n, n), dtype=int)

# ----------------------------
# 5. Rellenar matrices con aristas
# ----------------------------
for u, v, attr in G.edges(data=True):
    i = indice_nodo[u]
    j = indice_nodo[v]
    
    length_m = attr.get('length', 0)
    
    highway_type = attr.get('highway', 'unknown')
    if isinstance(highway_type, list):
        highway_type = highway_type[0]
    es_ruta = 1 if highway_type in ['primary', 'secondary', 'tertiary', 'trunk', 'motorway'] else 0
    
    consumo = (length_m / 1000) * consumo_kwh_km
    
    matriz_distancia[i, j] = round(length_m, 1)
    matriz_consumo[i, j] = round(consumo, 3)
    matriz_es_ruta[i, j] = es_ruta

# ----------------------------
# 6. Guardar matrices como CSV
# ----------------------------
df_distancia = pd.DataFrame(matriz_distancia, index=nodos, columns=nodos)
df_consumo = pd.DataFrame(matriz_consumo, index=nodos, columns=nodos)
df_es_ruta = pd.DataFrame(matriz_es_ruta, index=nodos, columns=nodos)

df_distancia.to_csv("matriz_distancia.csv")
df_consumo.to_csv("matriz_consumo.csv")
df_es_ruta.to_csv("matriz_es_ruta.csv")

# ----------------------------
# 7. Mensaje final
# ----------------------------
print("Matrices generadas:")
print(f"- matriz_distancia.csv ({df_distancia.shape})")
print(f"- matriz_consumo.csv ({df_consumo.shape})")
print(f"- matriz_es_ruta.csv ({df_es_ruta.shape})")
