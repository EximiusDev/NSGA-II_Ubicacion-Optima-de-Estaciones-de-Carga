import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import matplotlib.pyplot as plt

# ============================================================
# 1. Cargar los archivos (rutas relativas a este script)
# ============================================================
BASE_DIR = Path(__file__).parent
gdf_unificados = gpd.read_file(str(BASE_DIR / "nodos_unificados.gpkg"))
gdf_esquinas = gpd.read_file(str(BASE_DIR / "nodos_interseccion.gpkg"))

# ============================================================
# 2. Asegurar proyección métrica (para usar radios en metros)
# ============================================================
if gdf_unificados.crs != "EPSG:3857":
    gdf_unificados = gdf_unificados.to_crs(3857)
if gdf_esquinas.crs != "EPSG:3857":
    gdf_esquinas = gdf_esquinas.to_crs(3857)

# ============================================================
# 3. Definir el radio (en metros)
# ============================================================
R = 1000

# ============================================================
# 4. Crear buffers y hacer conteo espacial
# ============================================================
gdf_unificados["esquinas_en_radio"] = 0
gdf_buffers = gdf_unificados.copy()
gdf_buffers["geometry"] = gdf_buffers.geometry.buffer(R)

join = gpd.sjoin(gdf_buffers, gdf_esquinas, how="left", predicate="contains")
conteo = join.groupby(join.index).size()
gdf_unificados.loc[conteo.index, "esquinas_en_radio"] = conteo.values

# ============================================================
# 5. Filtrar columnas deseadas
# ============================================================
columnas_deseadas = ['osmid', 'y', 'x', 'street_count', 'highway', 'flujo_total', 'esquinas_en_radio', 'geometry']
gdf_unificados = gdf_unificados[columnas_deseadas]

# ============================================================
# 6. Guardar resultado
# ============================================================
output_file = str(BASE_DIR / "dataset_final.gpkg")
gdf_unificados.to_file(output_file, layer="nodos_unificados", driver="GPKG")

print(f"✅ Archivo actualizado guardado en: {output_file}")
print(gdf_unificados.head())



# ============================================================
# 6. Plot: nodos coloreados por cantidad de esquinas en radio
# ============================================================
fig, ax = plt.subplots(figsize=(12, 12))

# Buffers como referencia
gdf_buffers.plot(
    ax=ax,
    facecolor="none",
    edgecolor="green",
    alpha=0.3,
    linewidth=1,
    label=f"Buffer R={R} m"
)

# Nodos unificados coloreados por cantidad de esquinas
gdf_unificados.plot(
    ax=ax,
    column="esquinas_en_radio",
    cmap="viridis",
    markersize=50,
    legend=True,
    legend_kwds={"label": "Cantidad de esquinas en radio R", "shrink": 0.7},
    alpha=0.9
)

# Esquinas
gdf_esquinas.plot(
    ax=ax,
    color="red",
    markersize=5,
    label="Esquinas",
    alpha=0.7
)

plt.title(f"Nodos unificados coloreados por cantidad de esquinas en R={R} m", fontsize=16)
plt.axis("off")
plt.legend()
plt.show()
