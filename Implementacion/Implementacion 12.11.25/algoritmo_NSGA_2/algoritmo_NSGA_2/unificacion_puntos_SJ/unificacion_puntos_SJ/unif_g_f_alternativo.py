import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. Descargar la red vial
# ============================================================
print("📥 Descargando red vial de San Joaquin County...")
G = ox.graph_from_place("San Joaquin County, California, USA", network_type="drive")
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

print("CRS de nodos original:", gdf_nodes.crs)

# ============================================================
# 2. Proyectar la red (según versión de OSMnx)
# ============================================================
try:
    # OSMnx ≥ 2.0
    gdf_nodes = ox.project_gdf(gdf_nodes)
    gdf_edges = ox.project_gdf(gdf_edges)
except AttributeError:
    # OSMnx < 2.0
    print("⚙️  Usando método antiguo de proyección...")
    from osmnx import projection
    gdf_nodes = projection.project_gdf(gdf_nodes)
    gdf_edges = projection.project_gdf(gdf_edges)

print("✅ Red vial proyectada a CRS métrico:", gdf_nodes.crs)
PROJECTED_CRS = gdf_nodes.crs

# ============================================================
# 3. Filtrar solo aristas que son rutas principales
# ============================================================
tipos_ruta = ["primary", "secondary", "tertiary", "trunk", "motorway"]

def es_ruta(hw):
    if isinstance(hw, list):
        return any(h in tipos_ruta for h in hw)
    return hw in tipos_ruta

gdf_edges_ruta = gdf_edges[gdf_edges["highway"].apply(es_ruta)]

nodos_en_ruta = pd.unique(
    np.concatenate([
        gdf_edges_ruta.index.get_level_values(0).values,
        gdf_edges_ruta.index.get_level_values(1).values
    ])
)
gdf_nodes_ruta = gdf_nodes.loc[nodos_en_ruta]

print(f"📊 Nodos totales: {len(gdf_nodes)}, nodos en rutas principales: {len(gdf_nodes_ruta)}")

# ============================================================
# 4. Cargar datos de tráfico y reproyectar
# ============================================================
print("📥 Cargando datos de tráfico...")
gdf_trafico = gpd.read_file("puntos_unificados_SJ.geojson")
print("CRS de tráfico original:", gdf_trafico.crs)

if gdf_trafico.crs != PROJECTED_CRS:
    gdf_trafico = gdf_trafico.to_crs(PROJECTED_CRS)
    print("✅ Datos de tráfico reproyectados a:", PROJECTED_CRS)

print(f"Puntos de tráfico cargados: {len(gdf_trafico)}")

# ============================================================
# 5. Asignar flujo de tráfico a los nodos más cercanos
# ============================================================
print("🔍 Calculando correspondencia tráfico → nodos...")

# Agregar una columna explícita con el ID del nodo antes del join
gdf_nodes_ruta = gdf_nodes_ruta.copy()
gdf_nodes_ruta["osmid_nodo"] = gdf_nodes_ruta.index

# Realizar la unión espacial
gdf_trafico_con_nodo = gpd.sjoin_nearest(
    left_df=gdf_trafico,
    right_df=gdf_nodes_ruta,
    how="left",
    max_distance=100,  # metros
    distance_col="dist_m"
)

# Verificar que haya una columna osmid_nodo
if "osmid_nodo" not in gdf_trafico_con_nodo.columns:
    raise RuntimeError("❌ Error: no se encontró la columna 'osmid_nodo' tras el sjoin_nearest.")

print("✅ Unión espacial completada.")
print(f"Matches válidos: {gdf_trafico_con_nodo['osmid_nodo'].notna().sum()} de {len(gdf_trafico)}")

# ============================================================
# 6. Consolidar flujo (ADT) por nodo
# ============================================================
print("📈 Consolidando flujo (ADT) en los nodos...")

flujo_por_nodo = (
    gdf_trafico_con_nodo.groupby("osmid_nodo")["ADT"]
    .sum()
    .reset_index()
    .rename(columns={"osmid_nodo": "osmid"})
)

# Convertir tipo de índice
flujo_por_nodo["osmid"] = flujo_por_nodo["osmid"].astype(gdf_nodes_ruta.index.dtype)

# Unir con los nodos originales
gdf_nodes_ruta_con_flujo = gdf_nodes_ruta.merge(
    flujo_por_nodo, left_index=True, right_on="osmid", how="inner"
)

# Mantener consistencia CRS e índice
gdf_nodes_ruta_con_flujo = gdf_nodes_ruta_con_flujo.set_index("osmid").set_crs(PROJECTED_CRS)

print(f"✅ Nodos finales con flujo asignado: {len(gdf_nodes_ruta_con_flujo)}")

# ============================================================
# 7. Guardar resultados
# ============================================================
output_file = "nodos_ruta_con_flujo_CONSOLIDADO.gpkg"
gdf_nodes_ruta_con_flujo.to_file(output_file, layer="nodos_ruta_flujo_consol", driver="GPKG")
print(f"💾 Archivo guardado en: {output_file}")

# ============================================================
# 8. Visualización
# ============================================================
fig, ax = plt.subplots(figsize=(10, 10))
gdf_edges_ruta.plot(ax=ax, linewidth=0.4, color='gray', alpha=0.4)
gdf_nodes_ruta_con_flujo.plot(
    ax=ax, column="ADT", cmap="YlOrRd", markersize=8, legend=True
)
plt.title("Nodos de rutas principales con flujo de tráfico asignado", fontsize=12)
plt.axis("off")
plt.show()
