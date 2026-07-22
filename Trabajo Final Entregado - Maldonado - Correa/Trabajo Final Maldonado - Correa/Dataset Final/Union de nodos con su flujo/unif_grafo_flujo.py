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

# ============================================================
# 2. Proyectar la red
# ============================================================
try:
    gdf_nodes = ox.project_gdf(gdf_nodes)
    gdf_edges = ox.project_gdf(gdf_edges)
except AttributeError:
    from osmnx import projection
    gdf_nodes = projection.project_gdf(gdf_nodes)
    gdf_edges = projection.project_gdf(gdf_edges)

PROJECTED_CRS = gdf_nodes.crs
print("✅ Red vial proyectada:", PROJECTED_CRS)

# ============================================================
# 3. Filtrar rutas principales
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
# 4. Cargar datos de tráfico
# ============================================================
print("📥 Cargando puntos de tráfico...")
gdf_trafico = gpd.read_file("puntos_unificados_SJ.geojson")
if gdf_trafico.crs != PROJECTED_CRS:
    gdf_trafico = gdf_trafico.to_crs(PROJECTED_CRS)
print("✅ Puntos de tráfico:", len(gdf_trafico))

# ============================================================
# 5. Asignación 1:1 (punto de tráfico → nodo más cercano)
# ============================================================
r = 150   # radio en metros
p = 1.0   # potencia para IDW
eps = 1e-6

print("🔗 Emparejando punto de tráfico con su nodo más cercano...")

gdf_nodes_ruta = gdf_nodes_ruta.copy()
gdf_nodes_ruta["osmid_nodo"] = gdf_nodes_ruta.index

# Unión espacial 1:1 (más cercano)
asignacion_1a1 = gpd.sjoin_nearest(
    gdf_trafico,
    gdf_nodes_ruta[["geometry", "osmid_nodo"]],
    how="left",
    distance_col="dist_min",
    max_distance=r
)

if "osmid_nodo" not in asignacion_1a1.columns:
    raise RuntimeError(
        f"❌ No se encontró la columna 'osmid_nodo' tras el sjoin_nearest. "
        f"Columnas disponibles: {asignacion_1a1.columns.tolist()}"
    )

asignacion_1a1 = asignacion_1a1.dropna(subset=["osmid_nodo"])
asignacion_1a1["osmid_nodo"] = asignacion_1a1["osmid_nodo"].astype(int)
print(f"✅ Puntos asignados (1:1): {len(asignacion_1a1)} de {len(gdf_trafico)} puntos totales")

# ============================================================
# 6. Cálculo de flujo total ponderado dentro del radio r
# ============================================================
print("🔍 Calculando influencia ponderada de puntos cercanos (todos los puntos incluidos)...")

# 🔸 Todos los puntos aportan influencia, incluso si ya fueron emparejados
buffers = gdf_nodes_ruta.loc[asignacion_1a1["osmid_nodo"].unique()].copy()
buffers["osmid_nodo"] = buffers.index
buffers["geometry"] = buffers.geometry.buffer(r)

# Unión espacial: todos los puntos dentro del radio de cada nodo
points_in_buffer = gpd.sjoin(
    gdf_trafico,
    buffers[["geometry", "osmid_nodo"]],
    how="inner",
    predicate="intersects"
)

if len(points_in_buffer) == 0:
    print("⚠️ Ningún punto cayó dentro del radio de los nodos emparejados.")
    grouped = pd.DataFrame(columns=["osmid_nodo", "flujo_sum", "puntos_vecinos", "dist_media"])
else:
    nodes_geom = gdf_nodes_ruta.geometry.rename("geom_nodo").to_frame()
    points_in_buffer = points_in_buffer.merge(nodes_geom, left_on="osmid_nodo", right_index=True, how="left")
    points_in_buffer["dist_m"] = points_in_buffer.geometry.distance(points_in_buffer["geom_nodo"])

    # Peso IDW inverso a la distancia
    points_in_buffer["weight"] = 1.0 / (points_in_buffer["dist_m"] + eps) ** p
    points_in_buffer["ADT_w"] = points_in_buffer["ADT"] * points_in_buffer["weight"]

    # Promedio ponderado del flujo dentro del radio
    grouped = points_in_buffer.groupby("osmid_nodo").apply(
        lambda df: pd.Series({
            "flujo_sum": (df["ADT_w"].sum() / df["weight"].sum()) if df["weight"].sum() > 0 else 0,
            "puntos_vecinos": len(df),
            "dist_media": df["dist_m"].mean()
        })
    ).reset_index()

# ============================================================
# 7. Integrar asignación 1:1 con flujos ponderados
# ============================================================
# Flujo directo → promedio de los puntos 1:1
flujo_directo = asignacion_1a1.groupby("osmid_nodo")["ADT"].mean().rename("flujo_directo")

# Merge de ambos
result = buffers.merge(grouped.set_index("osmid_nodo"), left_index=True, right_index=True, how="left")
result = result.merge(flujo_directo, left_index=True, right_index=True, how="left")

# Flujo total
result["flujo_total"] = result["flujo_directo"].fillna(0) + result["flujo_sum"].fillna(0)

print(f"✅ Nodos emparejados con flujo total calculado: {len(result)}")

# ============================================================
# 8. Guardar y visualizar
# ============================================================
output_file = "nodos_unificados.gpkg"
#result.to_file(output_file, layer="nodos_emparejados_flujo", driver="GPKG")
print(f"💾 Guardado en: {output_file}")

# Grafico
fig, ax = plt.subplots(figsize=(10, 10))
gdf_edges_ruta.plot(ax=ax, linewidth=0.4, color="gray", alpha=0.4)
result.plot(ax=ax, color="black", markersize=250)
plt.title("Nodos emparejados")
plt.axis("off")
plt.show()

