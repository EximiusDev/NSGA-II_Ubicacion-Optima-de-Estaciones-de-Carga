# Ubicación de Estaciones de Carga de Autos Eléctricos mediante Algoritmos Genéticos Multiobjetivo

F.J.A. Maldonado y H. Correa  
Facultad de Ingeniería y Ciencias Hídricas, Universidad Nacional del Litoral  
Instituto de Investigación en Señales, Sistemas e Inteligencia Computacional, UNL-CONICET

---

**Resumen (≈200 palabras)**

La creciente adopción de vehículos eléctricos (VE) exige diseñar redes de recarga eficientes y sostenibles. Este trabajo propone un marco de optimización multiobjetivo para ubicar estaciones de recarga usando un algoritmo evolutivo de ordenamiento no-dominado (NSGA-II). El problema se formula sobre un conjunto de nodos geoespaciales extraídos del fichero `dataset_final.gpkg`. Los objetivos considerados son: minimizar la proporción de estaciones instaladas, minimizar la máxima distancia de cobertura y maximizar la prioridad de servicio basada en flujo y entorno urbano. Para abordar estos objetivos se define una representación binaria por nodo, funciones de fitness modulares y una configuración reproducible en un notebook basado en `pymoo` y `geopandas`.

Se realizaron experimentos variando parámetros clave como `d_max`, penalizaciones y tamaño de población. Los resultados se almacenan en `resultado_nsga2_final.npz` y se presentan en forma de frontera de Pareto. La frontera pone en evidencia los trade-offs entre coste (nº de estaciones) y beneficio (cobertura y prioridad). Se discuten limitaciones del enfoque, como la suposición de distancia euclídea y la falta de modelado de costes reales. Se proponen extensiones prácticas: incorporar red vial, costes económicos y demanda temporal. El marco entregado es reproducible y sirve como herramienta de apoyo para la planificación de infraestructura de recarga en distintos entornos (urbano y rural).

---

## 1. Introducción

La transición hacia la movilidad eléctrica es una prioridad global por sus beneficios ambientales y de salud. Implementar una red de estaciones de recarga eficiente es clave para facilitar dicha transición. El desafío técnico es diseñar ubicaciones que equilibren costo, cobertura y prioridad de servicio. Los vehículos eléctricos presentan limitaciones de autonomía que hacen crucial la planificación espacial de puntos de recarga. Además, zonas rurales y rutas interurbanas agregan complejidad por las grandes distancias entre nodos.

Este trabajo investiga una solución basada en algoritmos evolutivos multiobjetivo. Los Algoritmos Genéticos, y en particular NSGA-II, son adecuados para problemas con objetivos conflictivos porque entregan una aproximación de la frontera de Pareto y preservan diversidad en la población. En contraste con estudios previos, aquí se presta atención tanto a entornos urbanos como a entornos de mayor escala espacial, donde las distancias y la dispersión de la demanda son notables.

El objetivo práctico es proveer un procedimiento reproducible para generar alternativas de diseño (soluciones no dominadas) que faciliten la toma de decisiones de planificadores y operadores. El enfoque se apoya en datos espaciales (archivo `dataset_final.gpkg`) y en una implementación modular en `resolucion_final_modificable.ipynb`.

Breve organización del documento: en la Sección 2 se revisan trabajos relacionados; la Sección 3 describe la formulación y el método; la Sección 4 presenta los experimentos y resultados; la Sección 5 discute limitaciones y aplicaciones; la Sección 6 concluye con recomendaciones.

---

## 2. Revisión bibliográfica (selección representativa)

- Lam, Leung & Chu: presentaron formulaciones del problema de ubicación y discutieron complejidad y soluciones alternativas, incluyendo enfoques exactos y heurísticos. Sus conclusiones muestran que heurísticas mixtas son necesarias en instancias de tamaño real.

- Liu et al.: aplicaron optimización basada en Particle Swarm Optimization para planificación de estaciones y demuestran mejoras en cobertura bajo restricciones eléctricas.

- Awasthi et al.: propusieron híbridos GA–PSO para la planificación en sistemas de distribución, mostrando que combinaciones híbridas pueden superar métodos individuales en precisión de solución.

- Bai et al.: emplearon una variante de NSGA-II con datos de GPS para capturar trayectorias reales y obtener posicionamientos que favorecen patrones reales de desplazamiento.

Estos trabajos muestran la eficacia de métodos evolutivos y heurísticos para problemas de ubicación. La presente contribución reutiliza el paradigma NSGA-II y lo aplica a datos y restricciones específicas del repositorio del proyecto, con foco en reproducibilidad y análisis de sensibilidad.

---

## 3. Método (Formulación y Algoritmo)

### 3.1 Formulación del problema

- Conjunto de nodos: sea $N$ el número total de nodos representados en `dataset_final.gpkg`. Cada nodo $i$ tiene coordenadas $(x_i, y_i)$ y atributos de prioridad $f_i$ derivados de `flujo_total` y `esquinas_en_radio`.

- Variables de decisión: para cada nodo $i$ se define $z_i \in \{0,1\}$ donde $z_i=1$ indica la instalación de estación en el nodo $i$.

- Objetivos: se definen tres objetivos a minimizar (note que la prioridad se invierte para convertirla a minimización):

  1) Número relativo de estaciones (coste):
  $$f_1(\mathbf{z}) = \alpha \frac{\sum_{i} z_i}{N} + \text{penalización	extunderscore exceso}$$

  2) Cobertura máxima (distancia máxima de cualquier nodo a su estación más cercana):
  $$f_2(\mathbf{z}) = \max_{j \in \mathcal{N}} \min_{i: z_i=1} d(j,i)$$
  donde $d(j,i)$ es la distancia euclídea entre nodos $j$ e $i$. En la implementación se normaliza por $d_{max}$.

  3) Prioridad invertida (se busca seleccionar estaciones en nodos de alta prioridad):
  $$f_3(\mathbf{z}) = 1 - \frac{1}{|S|} \sum_{i\in S} p_i, \quad S=\{i: z_i=1\}$$
  con $p_i$ la prioridad normalizada del nodo $i$.

- Restricciones suaves: se penaliza el exceso de estaciones sobre una proporción máxima permitida $\rho_{max}$. Las penalizaciones se incorporan a $f_1$ o a $f_2$ según diseño experimental.

### 3.2 Cálculo de prioridades

La prioridad $p_i$ se computa como combinación lineal de atributos normalizados:

$$p_i = w_f \cdot \frac{flujo\_total_i}{\max flujo\_total} + w_e \cdot \frac{esquinas\_en\_radio_i}{\max esquinas\_en\_radio}$$

Con pesos $w_f$ y $w_e$ (en la implementación por defecto $w_f=0.7, w_e=0.3$).

### 3.3 Algoritmo de solución: NSGA-II

Se usa la implementación `NSGA2` de `pymoo` con variables binarias. El flujo general es:

1. Inicializar población aleatoria $P_0$ de vectores $\mathbf{z}$.  
2. Evaluar objetivos $f_1, f_2, f_3$ para cada individuo usando las funciones definidas.  
3. Ordenar por dominancia (frentes de Pareto).  
4. Calcular crowding distance en cada frente.  
5. Selección por torneo binario, crossover y mutación.  
6. Generar nueva población y repetir $n_{gen}$ generaciones.  
7. Conservar historial y exportar resultados en `resultado_nsga2_final.npz`.

Se usan operadores de cruzamiento y mutación estándar. La evaluación de cobertura se acelera mediante estructuras espaciales (se recomienda `scipy.spatial.cKDTree` para consultas eficientes de distancia mínima en implementaciones a gran escala).

### 3.4 Implementación y reproducibilidad

- Lenguajes y librerías: Python 3.x, `pandas`, `geopandas`, `numpy`, `scikit-learn` (`pairwise_distances` para prototipo), `pymoo` para NSGA-II, `matplotlib` y `plotly` para visualización.

- Notebook principal: `resolucion_final_modificable.ipynb` contiene la implementación, funciones de fitness, clase problema `EVChargingProblem3F`, ejecución del algoritmo y rutinas de validación.

- Resultados guardados: `resultado_nsga2_final.npz` contiene matrices `X` (soluciones) y `F` (valores objetivo) para reproducibilidad y análisis posterior.

---

## 4. Experimentos y Resultados

### 4.1 Datos y preprocesamiento

Los datos se cargan desde `dataset_final.gpkg` con `geopandas.read_file`. Se garantiza un CRS métrico (`EPSG:3857`) para cálculos en metros. Las variables de prioridad (`flujo_total` y `esquinas_en_radio`) se normalizan dividiendo por su máximo observado y se combinan con pesos prefijados. Cuando las geometrías no son puntos, se usan centroides para representar la posición del nodo.

### 4.2 Configuración experimental

Parámetros representativos usados en los experimentos de referencia:

- `d_max` = 10,000 m (umbral de cobertura),  
- `pop_size` = 200,  
- `n_gen` = 500,  
- `factor_estaciones` = 50 (peso relativo en f1),  
- `max_ratio` = 0.15 (proporción máxima de nodos con estaciones permitida),  
- semilla (`seed`) = 23 para reproducibilidad.

Estas elecciones permiten equilibrar capacidad computacional y exploración del espacio de soluciones.

### 4.3 Principales resultados

- Frontera de Pareto: la ejecución de NSGA-II produjo una frontera con soluciones que trade-offeaban entre pocas estaciones y mejor cobertura. Las soluciones con baja cantidad de estaciones muestran un aumento notable en la distancia máxima cubierta, mientras que soluciones con más estaciones reducen fuertemente la distancia máxima.

- Prioridad: entre las soluciones con similar cobertura, algunas se distinguen por seleccionar nodos con mayor prioridad (mayor `flujo_total` y número de esquinas), lo que es deseable desde el punto de vista del servicio.

- Métricas de validación: la rutina `validar_soluciones` calcula por solución la distancia máxima real, cobertura promedio, % nodos cubiertos y eficiencia por estación. Estas métricas facilitan ordenar soluciones por criterios operativos.

(Nota: los resultados numéricos concretos están guardados en `resultado_nsga2_final.npz`. Para reproducir y visualizar las gráficas interactivas, ejecutar la celda de visualización en `resolucion_final_modificable.ipynb`. Si VS Code muestra advertencias de renderers para `plotly`, se recomienda usar `pio.renderers.default='browser'` o abrir el resultado en navegador.)

### 4.4 Interpretación

- Existe una curva de compromiso estable entre coste y cobertura. La elección operativa depende de recursos disponibles y objetivos de servicio.  
- Las soluciones que maximizan prioridad tienden a concentrar estaciones en nodos con alto flujo, lo que mejora la utilidad por estación pero puede dejar áreas periféricas con peor cobertura.  
- Sensibilidad: la frontera se desplaza notablemente al variar `d_max` y el factor de penalización; por tanto, se recomienda realizar análisis de sensibilidad antes de adoptar un diseño final.

---

## 5. Discusión y Limitaciones

- Distancia euclídea: la implementación usa distancia euclídea en un CRS métrico. Esto es una aproximación que puede ser insuficiente en redes viales complejas. Incorporar distancias por red (ruta real) mejora realismo.

- Costes y restricciones: no se modelaron costes reales de instalación, capacidad eléctrica ni restricciones urbanas. Estos factores son críticos para la implementación práctica.

- Escalabilidad: el cálculo de distancias puede ser costoso para grandes instancias. Se recomienda `cKDTree` para consultas de distancia mínima y paralelización o evaluación solo de soluciones promisorias.

- Datos: la calidad de `dataset_final.gpkg` (atributos y geometrías) condiciona fuertemente la validez de las recomendaciones. Se aconseja validar y enriquecer datos con tráfico, demanda temporal y límites regulatorios.

---

## 6. Conclusiones y recomendaciones (≈150–200 palabras)

Se desarrolló e implementó un marco basado en NSGA-II para ubicar estaciones de recarga de vehículos eléctricos sobre un conjunto de nodos geoespaciales. La formulación multiobjetivo permite explorar el conjunto de soluciones no dominadas, mostrando explícitamente los compromisos entre número de estaciones, cobertura y prioridad de servicio. Los resultados obtenidos, almacenados en `resultado_nsga2_final.npz` y producidos por `resolucion_final_modificable.ipynb`, evidencian que es posible reducir considerablemente la distancia máxima de cobertura aumentando moderadamente el número de estaciones, o priorizar nodos de alto flujo manteniendo un coste controlado. Sin embargo, para aplicar estas soluciones en entornos reales es necesario incorporar costes económicos, restricciones urbanas y distancias basadas en la red vial. Recomendamos usar el presente marco como herramienta de apoyo a la decisión, complementando la salida de NSGA-II con análisis de sensibilidad y validación con expertos locales. Futuras extensiones incluyen modelado de demanda temporal, integración de costes y optimización con rutas reales.

---

## Agradecimientos

Agradecemos a las autoridades y colegas que compartieron ideas y revisiones durante el desarrollo. El proyecto recoge contribuciones de recursos y datos incluidos en la carpeta del repositorio.

---

## Referencias (selección)

- Lam, A. Y. S., Leung, Y.-W., & Chu, X. Electric vehicle charging station placement: Formulation, complexity, and solutions.  
- Liu, Z.-f., Zhang, W., Ji, X., & Li, K. Optimal planning of charging station for electric vehicle based on particle swarm optimization.  
- Awasthi, A., Venkitusamy, K., Padmanaban, S., Selvamuthukumaran, R., Blaabjerg, F., & Singh, A. K. Optimal planning of electric vehicle charging station at the distribution system using hybrid optimization algorithm.  
- Bai, X., Chin, K.-S., & Zhou, Z. A bi-objective model for location planning of electric vehicle charging stations with GPS trajectory data.  
- Okabe, A., Sugihara, K., & Saeki, E. Kernel Density Estimation of Traffic Accidents in a Network Space.

---

## Apéndice A — Archivos relevantes en el repositorio

- `dataset_final.gpkg` — datos espaciales con nodos y atributos.  
- `resolucion_final_modificable.ipynb` — notebook con la implementación y experimentos.  
- `resultado_nsga2_final.npz` — resultados guardados (`X` y `F`).  
- `informe_nsga2.md`, `informe_nsga2.txt`, `informe_nsga2.rtf` — archivos auxiliares generados en el proyecto.

---

## Apéndice B — Sugerencias para reproducir y convertir a DOCX

Para generar un `docx` (Word) desde este Markdown usando Pandoc en PowerShell:

```powershell
cd "c:\Users\Franc\Desktop\Informatica\.CURSANDO\Int Comp - Inteligencia Computacional - 2025\TP Final\Implementacion\Implementacion 13.11.25\algoritmo_NSGA_2\algoritmo_NSGA_2"
# instalar pandoc si no está disponible
pandoc informe_cientifico.md -o informe_cientifico.docx
```

Si prefieres, puedo generar el `requirements.txt` y/o crear el `.docx` aquí (si me indicas que Pandoc está disponible en tu equipo o deseas que lo prepare como archivo RTF/`docx` alternativo).
