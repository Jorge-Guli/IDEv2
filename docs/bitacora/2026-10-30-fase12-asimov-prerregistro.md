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

## Resultado (2026-10-29, salida `runs/fase12/asimov.json`)

**Veredicto según el prerregistro: inválido** (texto 4 extinciones, barajado 3; el límite era 2). Aun leyendo lo que sobrevivió, **no hay efecto**.

| Semilla | texto | barajado |
|---|---|---|
| 101 | 0,553 | 0,547 |
| 102 | extinta (t=184 676) | extinta (t=312 054) |
| 103 | extinta (t=210 318) | extinta (t=390 986) |
| 104 | extinta (t=254 134) | 0,562 |
| 105 | **0,578** | **0,572** |
| 106 | extinta (t=262 582) | extinta (t=258 907) |
| 107 | 0,558 | 0,558 |
| 108 | 0,539 | 0,536 |

(`acierto_comida`, media del último tercio.)

- **R1:** 4 pares completos, diferencias +0,007, +0,005, 0,000, +0,003; p = 0,125. **No cumple.** Las diferencias son diez veces menores que lo que daría usar la alternancia.
- **R2:** texto 1 de 4 sobre 0,56; barajado 2 de 6. **No cumple.**
- **Exploratorias:** sin diferencias en memoria (p = 0,31), genes (p = 0,25) ni población (p = 0,88).

### Lectura posterior (exploratoria, no prerregistrada)
En 500 000 pasos de 500 pasos por letra se recorren solo **1 000 letras**. La frecuencia base hay que medirla **en la ventana** del último tercio (letras 667–1 000), no en el texto entero:
- **texto:** base local 0,530; invertir la pista 0,754. Las 4 sobrevivientes superan la base local por +0,009 a +0,048.
- **barajado** (cada semilla con su orden): base local 0,518–0,575. Sus poblaciones también la superan, hasta **+0,038** (semilla 104: 0,562 contra 0,524).

Conclusiones:
- **Superar la base no prueba predicción.** Hay una ganancia de ~0,01–0,04 que no usa la secuencia: reaccionar dentro de cada letra (el sensor `coincide` y el tipo de la celda permiten corregir después de los primeros bocados).
- **El umbral 0,56 de R2 estaba mal calibrado.** Salió de 3 semillas barajadas del piloto, y la base local varía ±0,03 entre semillas barajadas. R1 (pareado) era la regla correcta y dio nulo.
- **La física con `castigo = 0,5` y rampa de 150 000 es frágil:** 7 de 16 poblaciones se extinguieron entre t = 185 000 y 391 000, después de la rampa. En el piloto con el texto de calibración había sido 1 de 12. Con estas tasas, cualquier diseño pierde la mitad de la potencia.
- **Ningún sobreviviente se acerca a 0,754.** El mejor (texto 105, 0,578) está al nivel de su par barajado (0,572). La evolución, con ~200 organismos y 500 000 pasos, **no descubrió la alternancia** en el texto real, igual que en el de calibración, donde el aparente 0,579 tampoco se distinguía de la reacción.

### Qué sigue
1. **No repetir con Asimov.** El prerregistro se usó; repetirlo con otras semillas sería buscar hasta que salga. Los cuentos se reservan para un diseño nuevo y prerregistrado, cuando un piloto con el texto de calibración muestre un efecto pareado claro (diferencia ≥ 0,05 contra barajado, no contra el techo).
2. **Antes, arreglar la física:** las extinciones tardías con castigo 0,5. Probar un castigo intermedio (0,35) o una rampa más larga, midiendo supervivencia y acierto con la estación fija.
3. **Tasa de descubrimiento:** poblaciones mayores (GPU) o letras más largas, para que una mutación que invierte la pista tenga tiempo de pagar.
