## Electric Vehicle Charging Station Location using NSGA-II

Proyecto desarrollado para la asignatura **Inteligencia Computacional** de la carrera **Ingeniería en Informática** (FICH - Universidad Nacional del Litoral).

El objetivo del trabajo consiste en resolver el problema de ubicación óptima de estaciones de carga para vehículos eléctricos mediante un **Algoritmo Genético Multiobjetivo (NSGA-II)**, obteniendo un conjunto de soluciones de compromiso (Frente de Pareto) entre costo de instalación, cobertura territorial y prioridad de ubicación.

---

# Introducción

La creciente adopción de vehículos eléctricos plantea nuevos desafíos relacionados con la infraestructura de recarga.

Determinar dónde instalar estaciones de carga es un problema de optimización complejo, ya que intervienen múltiples objetivos que suelen entrar en conflicto entre sí:

- Reducir la cantidad de estaciones instaladas.
- Garantizar cobertura sobre toda la red vial.
- Priorizar zonas con mayor flujo vehicular y densidad poblacional.

Para resolver este problema se implementó un algoritmo **NSGA-II (Non-Dominated Sorting Genetic Algorithm II)** utilizando la librería **pymoo**, obteniendo un conjunto de soluciones no dominadas que permiten al planificador elegir el compromiso más conveniente entre los distintos objetivos.

---

# Relación con la asignatura

Este proyecto aplica conceptos desarrollados durante la materia **Inteligencia Computacional**, principalmente los relacionados con la **Computación Evolutiva** y la **Optimización Multiobjetivo**.

Se utilizan técnicas estudiadas en las unidades correspondientes a Inteligencia Colectiva, donde se desarrollan los fundamentos de los algoritmos evolutivos inspirados en procesos biológicos para resolver problemas de optimización complejos.

Entre los conceptos aplicados se encuentran:

- Inteligencia Computacional.
- Computación Evolutiva.
- Algoritmos Genéticos.
- Optimización Multiobjetivo.
- Frontera de Pareto.
- Funciones de Fitness.
- Representación genética.
- Selección por torneo.
- Cruza y mutación.
- Elitismo.

Especialmente corresponde a los contenidos de:

- **Unidad 5 – Inteligencia Colectiva I**
- **Unidad 6 – Inteligencia Colectiva II**

---

# Objetivos del proyecto

Implementar un algoritmo evolutivo capaz de optimizar simultáneamente:

- Cantidad de estaciones de carga.
- Distancia máxima desde cualquier nodo hacia su estación más cercana.
- Prioridad de ubicación basada en flujo vehicular y densidad geográfica.

El algoritmo no busca una única solución óptima sino un **conjunto de soluciones Pareto óptimas**, permitiendo diferentes compromisos entre los objetivos.

---

# ¿Qué es un Algoritmo Genético?

Los **Algoritmos Genéticos (AG)** son técnicas de optimización inspiradas en el proceso de evolución natural propuesto por Charles Darwin. En lugar de buscar una solución mediante reglas determinísticas, trabajan con una **población de soluciones candidatas** que evoluciona generación tras generación.

Cada solución, denominada **individuo**, representa una posible respuesta al problema y está codificada mediante un **cromosoma**, que almacena la información necesaria para describir dicha solución. En este proyecto, cada cromosoma es un vector binario donde cada gen indica si en un nodo del mapa existe o no una estación de carga.

Durante la evolución, cada individuo es evaluado mediante una o varias **funciones de fitness**, que determinan qué tan buena es la solución. Las soluciones con mejor desempeño tienen mayor probabilidad de reproducirse mediante operadores inspirados en la genética:

- **Selección:** elige los individuos con mejor fitness para reproducirse.
- **Cruza (Crossover):** combina la información genética de dos individuos para generar nuevas soluciones.
- **Mutación:** modifica aleatoriamente algunos genes para mantener diversidad en la población y evitar caer en óptimos locales.
- **Reemplazo:** la nueva generación sustituye parcial o totalmente a la anterior, manteniendo la evolución del algoritmo.

Este proceso se repite durante cientos o miles de generaciones, logrando que la población evolucione progresivamente hacia soluciones cada vez mejores.

Los algoritmos genéticos resultan especialmente útiles cuando el espacio de búsqueda es muy grande o cuando un problema posee múltiples variables y restricciones, haciendo inviable una búsqueda exhaustiva.

---

# ¿Por qué NSGA-II?

En este proyecto no existe un único criterio de optimización, sino **tres objetivos que compiten entre sí**:

- Minimizar la cantidad de estaciones de carga.
- Minimizar la distancia máxima desde cualquier nodo hasta su estación más cercana.
- Maximizar la prioridad de ubicación de las estaciones según el flujo vehicular y la densidad poblacional.

Mejorar uno de estos objetivos generalmente implica empeorar alguno de los otros. Por esta razón se utilizó **NSGA-II (Non-dominated Sorting Genetic Algorithm II)**, un algoritmo genético diseñado específicamente para problemas de **optimización multiobjetivo**.

En lugar de devolver una única solución, NSGA-II genera un conjunto de soluciones denominado **Frente de Pareto**, donde todas las alternativas representan distintos compromisos entre los objetivos y ninguna domina completamente a otra. Esto permite que el usuario seleccione posteriormente la solución más conveniente según las necesidades del problema.

---

# ¿Cómo funciona el algoritmo en este proyecto?

Cada individuo de la población representa una posible distribución de estaciones de carga.

El cromosoma está formado por un vector binario:

```text
[1,0,0,1,0,1,...]
```

donde:

- **1** → existe una estación de carga en ese nodo.
- **0** → no existe estación de carga.

Cada individuo es evaluado mediante tres funciones objetivo (fitness).

### Fitness 1 — Cantidad de estaciones

Minimiza la cantidad total de estaciones instaladas.

Busca reducir el costo de implementación penalizando aquellas soluciones que utilizan demasiadas estaciones.

---

### Fitness 2 — Cobertura

Minimiza la distancia máxima desde cualquier nodo hasta la estación de carga más cercana.

Si algún nodo queda a una distancia superior al límite establecido (`d_max`), la solución recibe una fuerte penalización.

---

### Fitness 3 — Prioridad

Maximiza la calidad de las ubicaciones elegidas.

La prioridad de cada nodo se calcula utilizando:

- flujo vehicular;
- cantidad de esquinas cercanas (como aproximación de la densidad poblacional).

El algoritmo intenta ubicar las estaciones en los puntos más relevantes del territorio.

---

# Algoritmo utilizado

La implementación utiliza **NSGA-II**, uno de los algoritmos evolutivos multiobjetivo más reconocidos y utilizados en la actualidad.

Las principales características del algoritmo son:

- Ordenamiento por dominancia (*Non-Dominated Sorting*).
- Frontera de Pareto.
- Crowding Distance (preservación de diversidad).
- Selección por torneo.
- Elitismo.
- Cruza binaria.
- Mutación polinomial.

Gracias a estas características, NSGA-II logra mantener diversidad entre las soluciones mientras converge hacia regiones óptimas del espacio de búsqueda.

---

# Dataset

El proyecto utiliza un conjunto de datos geográficos correspondiente al:

**Condado de San Joaquín, California (Estados Unidos).**

El dataset fue construido utilizando información proveniente de:

- OpenStreetMap.
- OSMNX.
- GeoPandas.
- Datos oficiales de tráfico del Estado de California.

Cada nodo contiene información sobre:

- Coordenadas geográficas.
- Flujo vehicular.
- Cantidad de esquinas cercanas.
- Conectividad dentro de la red vial.

El conjunto de datos final contiene:

**488 nodos candidatos** para instalar estaciones de carga.

---

# Parámetros utilizados

| Parámetro                  | Valor             |
| -------------------------- | ----------------- |
| Algoritmo                  | NSGA-II           |
| Población                  | 400 individuos    |
| Generaciones               | 1500              |
| Cantidad de nodos          | 488               |
| Distancia máxima (`d_max`) | 10 km / 20 km     |
| Peso flujo                 | 0.7               |
| Peso densidad              | 0.3               |
| Representación             | Cromosoma binario |

---

# Tecnologías utilizadas

| Herramienta      | Uso                          |
| ---------------- | ---------------------------- |
| Python           | Implementación general       |
| pymoo            | NSGA-II                      |
| NumPy            | Operaciones numéricas        |
| Pandas           | Procesamiento de datos       |
| GeoPandas        | Datos geográficos            |
| OSMNX            | Construcción del grafo vial  |
| Matplotlib       | Visualización de resultados  |
| Shapely          | Operaciones geométricas      |
| Jupyter Notebook | Desarrollo y experimentación |

---

# Resultados obtenidos

El algoritmo genera una **Frontera de Pareto** formada por soluciones no dominadas.

Entre los resultados obtenidos pueden encontrarse:

- soluciones con pocas estaciones y menor costo;
- soluciones con mejor cobertura territorial;
- soluciones que priorizan nodos con mayor flujo vehicular;
- distintos compromisos entre costo, cobertura y prioridad.

Esto permite que el planificador seleccione la alternativa que mejor se adapte a las necesidades del problema.

---

# Validación

Al no existir una solución óptima conocida para este problema, la validación se realizó mediante:

- un índice de eficiencia desarrollado para el proyecto;
- comparación entre soluciones dominadas y no dominadas;
- verificación automática de que todas las soluciones pertenecientes al Frente de Pareto fueran efectivamente no dominadas.

---

# Limitaciones

Entre las principales limitaciones del modelo se encuentran:

- utilización de distancia euclídea en lugar de distancia real sobre la red vial;
- no considerar costos reales de instalación;
- no modelar disponibilidad de energía eléctrica;
- no incluir restricciones urbanísticas;
- dependencia de la calidad del dataset utilizado.

Estas limitaciones representan posibles líneas de trabajo para futuras mejoras del proyecto.

---

# Estructura del proyecto

```text
.
├── datasets/
│   └── dataset_final.gpkg
│
├── notebooks/
│   └── resolucion.ipynb
│
├── resultados/
│   ├── pareto.png
│   ├── soluciones.png
│   └── mapas/
│
├── informe/
│   └── Informe.pdf
│
├── presentacion/
│   └── Presentacion.pdf
│
└── README.md
```

---

# Ejecución

Instalar las dependencias correspondientes

Abrir el notebook:

```bash
jupyter notebook resolucion.ipynb
```

Ejecutar todas las celdas.

El algoritmo generará automáticamente:

- la población inicial;
- la evolución del NSGA-II;
- el Frente de Pareto;
- mapas con la ubicación de estaciones;
- métricas de validación.

---

# Conceptos de Inteligencia Computacional aplicados

- Computación Evolutiva.
- Algoritmos Genéticos.
- Optimización Multiobjetivo.
- NSGA-II.
- Funciones de Fitness.
- Frontera de Pareto.
- Dominancia.
- Crowding Distance.
- Selección por Torneo.
- Cruza.
- Mutación.
- Elitismo.

---

# Autores

**Francisco Javier Agustín Maldonado**

**Hernán Correa**

Ingeniería en Informática

Facultad de Ingeniería y Ciencias Hídricas

Universidad Nacional del Litoral

---

# Referencias

- Deb, K. et al. *A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II*.
- Documentación oficial de **pymoo**.
- OpenStreetMap.
- OSMNX.
- Bai et al. *A Bi-objective Model for Location Planning of Electric Vehicle Charging Stations*.


