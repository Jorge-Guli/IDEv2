# 2026-10-30 · Fase 12: el mundo del texto con Asimov (prerregistro)

## Pregunta
¿La evolución, desde LUCA, aprovecha la estructura de un texto real para predecir qué comida nutre ahora?

- **Textos:** "La última pregunta" y "La última respuesta" de Isaac Asimov, elegidas por el autor por su simbolismo. Copia propia del autor en `datos/textos/` (ignorada por Git; aquí solo van sus huellas).
  - `la_ultima_pregunta.txt`: sha256 `5a985d7c…`, 22 197 letras.
  - `la_ultima_respuesta.txt`: sha256 `d6548766…`, 12 110 letras.
- **Techos (solo conteos de vocales y consonantes):**
  - seguir la pista: 0,242;
  - base: 0,542;
  - invertir la pista: 0,758.

## Lo que llevó hasta acá (`2026-10-29-fase12-mundo-texto.md`)
- Con `castigo = 0,2` no se selecciona siquiera elegir la comida. Con 0,5 sí, si hay tiempo (rampa de toxicidad 150 000).
- La digestión inducible (inercia de 100 pasos) impedía seguir una comida que cambia. Sin ella, una población llegó a 0,97 en la versión reactiva.
- Con la tarea real, en el texto de calibración (9 semillas, 500 000 pasos, último tercio):
  - **texto:** 0,534, **0,579**, 0,549, **0,575**, **0,561**, 0,549, 0,555, 0,532 (1 extinta);
  - **barajado:** 0,548, 0,551, 0,537 (3 semillas).
- La predicción aparece de forma **parcial y en parte de las poblaciones**. La potencia de este prerregistro es **moderada**: es honesto esperar un resultado dudoso.

## Diseño (fijo antes de correr)
- **Mundo:** `vivo.toml` (fase 11), desde LUCA, más los ajustes:
  `texto.activo=true`, `texto.archivos=datos/textos/la_ultima_pregunta.txt,datos/textos/la_ultima_respuesta.txt`, `texto.pasos_por_letra=500`, `texto.sensor_coincide=true`, `texto.pista=anterior`, `estaciones.castigo=0.5`, `estaciones.rampa_toxicidad=150000`, `estaciones.induccion=0`.
- **Condiciones:**
  - **texto:** las letras en su orden;
  - **barajado:** las mismas letras en orden al azar (`texto.barajar=true`, generador propio de la semilla).
- **Semillas nuevas 101–108**, 500 000 pasos, 6 procesos.
- **Comando:**
  `python experiments/fase12/mundo_texto.py --pasos 500000 --semillas 101 102 103 104 105 106 107 108 --set texto.sensor_coincide=true --set estaciones.castigo=0.5 --set estaciones.rampa_toxicidad=150000 --set estaciones.induccion=0 --salida runs/fase12/asimov.json`
  (`--archivos` por defecto: los dos cuentos).

## Reglas (permutación pareada exacta, una cola, α = 0,05; medidas en el último tercio, t ≥ 333 334)
| Regla | Qué afirma | Criterio |
|---|---|---|
| **R1** | La evolución aprovecha la secuencia del texto | `acierto_comida` texto > barajado, p < 0,05 |
| R2 | Aprovechamiento por encima de lo posible sin secuencia | al menos 3 de las corridas de texto superan 0,56, y a lo sumo 1 del barajado lo hace |

- **Exploratorias:** genes medios, memoria A, población, y la serie del acierto en el tiempo.
- **Validez:** si hay más de 2 extinciones en una condición, el resultado se declara inválido.

## Cómo se interpretará
- **R1 positiva:** primera evidencia en el proyecto de que la evolución **descubre y usa una regularidad del lenguaje para predecir**. No es comprensión: es estadística de la alternancia de vocales y consonantes. Pero es predicción de verdad, con un control que la descarta como artefacto.
  - Pasos siguientes: revisión con `revisor-cientifico`; clases más ricas, donde mirar más atrás pague y la memoria tenga motivo; poblaciones más grandes.
- **R2 sola:** algunas poblaciones lo logran, pero no de forma general.
- **Ambas negativas:** la tasa de descubrimiento es demasiado baja en este tamaño de población. Siguiente: poblaciones más grandes (GPU), no más ajustes de la física.
