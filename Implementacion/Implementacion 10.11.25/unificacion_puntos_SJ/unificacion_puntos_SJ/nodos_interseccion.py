import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt

# ============================================================
# 1. Descargar la red vial de San Joaquin County
# ============================================================
print("📥 Descargando red vial de San Joaquin County...")
G = ox.graph_from_place("San Joaquin County, California, USA", network_type="drive")

# ============================================================
# 2. Calcular el grado de cada nodo
# ============================================================
grados = dict(G.degree())

# Convertir a GeoDataFrame
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
gdf_nodes["grado"] = gdf_nodes.index.map(grados)

# ============================================================
# 3. Filtrar intersecciones reales
# ============================================================
# Solo nodos con 3 o más conexiones
gdf_intersecciones = gdf_nodes[gdf_nodes["grado"] >= 3].copy()

print(f"📊 Total de nodos: {len(gdf_nodes)}")
print(f"📍 Nodos de intersección (grado >= 3): {len(gdf_intersecciones)}")

# ============================================================
# 4. Guardar y visualizar
# ============================================================
output_file = "nodos_interseccion.gpkg"
gdf_intersecciones.to_file(output_file, layer="intersecciones", driver="GPKG")
print(f"💾 Guardado en: {output_file}")

fig, ax = plt.subplots(figsize=(10, 10))
ox.plot_graph(G, ax=ax, node_size=0, edge_color="gray", edge_alpha=0.3, show=False, close=False)
gdf_intersecciones.plot(ax=ax, color="red", markersize=10)
plt.title("Intersecciones (grado ≥ 3) - San Joaquin County")
plt.axis("off")
plt.show()
