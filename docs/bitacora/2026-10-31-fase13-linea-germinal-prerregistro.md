# 2026-10-31 · Fase 13, peldaño 3: ¿el cuerpo se reproduce como unidad? (prerregistro)

Escrito antes de correr. Viene de los [controles del cuerpo](2026-10-30-fase13-cuerpo-controles-prerregistro.md): hay cuerpos clonales, robustos al canibalismo, con la curva del tamaño [respaldada por datos reales](2026-10-31-fase13-curva-tamano-prerregistro.md).

## Idea
En la naturaleza, el paso a "un cuerpo" como unidad de la evolución es la **línea germinal**: pocas células fundan los cuerpos nuevos (con un propágulo de una sola célula) y el resto, el soma, mantiene el cuerpo sin reproducirse (Michod 2006; Grosberg y Strathmann 2007).

**Antes de agregar mecanismos, se mide si el genoma actual ya lo logra.** No hace falta física nueva:
- un cuerpo crece con `dividirse_unido`;
- funda otro con `dividirse`: el hijo nace suelto, un propágulo de una célula;
- la red regulatoria y los sensores (por ejemplo, la cantidad de enlaces, que distingue el borde del interior) permiten que células del mismo cuerpo hagan cosas distintas.

## Medidas nuevas (código)
- Por célula: `n_propagulos` (hijos sueltos en la vida) y `n_lugar` (pasos con alguna celda vecina libre, o sea, la oportunidad física de dividirse).
- En cuerpos de 3 o más (miembros con edad ≥ 100 y al menos 3 propágulos):
  - `concentracion_propagulos`: fracción de los propágulos que hizo el tercio más fértil;
  - la misma medida si se repartieran al azar según la oportunidad física, con 20 sorteos y un generador propio: `concentracion_propagulos_lugar`;
  - **`exceso_germinal`** = concentración observada − azar por oportunidad.
- El azar por oportunidad es necesario: las células del interior no tienen dónde dividirse, y eso solo ya concentra los propágulos. Una prueba corta sin ese control daba un exceso de 0,3 que era geometría.
- Descriptivas: `frac_sin_propagulos` (soma), `frac_propagulos_de_cuerpo` (fracción de los propágulos que salen de cuerpos de 3 o más).

Tests: 209 pasan, 1 omitido. Huellas iguales a la referencia.

## Diseño
- **Universo:** `natural.toml`, desde LUCA.
- **Condiciones:**
  - **red:** el universo tal cual;
  - **inerte:** los genes no leen la red.
- **Semillas:** 19–24, nuevas. **Pasos:** 300 000. Medición desde el paso 200 000.
- **Ejecución:** Docker (`experiments/fase13/germinal.py`, contenedor `fase13-germinal`). **Salida:** `runs/fase13/germinal.json`.

## Criterios
| | Medida | Cumple si |
|---|---|---|
| **G1, línea germinal** | `exceso_germinal` en red | > 0, permutación de signos exacta, p ≤ 0,05 (en la práctica, 6 de 6 positivas) |
| **G2, la red la hace posible** | `exceso_germinal` red − inerte | > 0, permutación pareada, p ≤ 0,05 |

**Exploratorias:** `frac_sin_propagulos`, `frac_propagulos_de_cuerpo`, `concentracion_propagulos` y las dos referencias al azar.

## Qué significaría cada resultado
- **G1 y G2:** hay línea germinal y nace de la red regulatoria: el cuerpo empieza a ser la unidad de reproducción.
- **G1 sin G2:** la división del trabajo reproductivo existe, pero alcanza con los sensores (por ejemplo, la posición).
- **Ninguno:** cada célula se reproduce por su cuenta; el cuerpo todavía es una colonia clonal. El paso siguiente sería buscar qué capacidad real le falta al genoma: por ejemplo, que el flujo de energía entre células unidas dependa del genoma, como los puentes citoplasmáticos de *Volvox*. Sin fuerzas diseñadas.

## Enmienda (2026-10-31, antes de ver ningún resultado)
Por un comentario de Gemini sobre la potencia: con 6 semillas, una sola semilla ruidosa deja p en 0,078, como pasó con P2' en los controles. **Se amplía a 10 semillas (19–28).** Cuando terminan las 12 corridas de 19–24, el mismo script retoma y agrega 25–28, sin abrir el resultado parcial. Los criterios no cambian; se evalúan sobre las 10.

También se agrega como exploratoria `eta_media`, la tasa de aprendizaje en vida (heredable). Pregunta: ¿el refuerzo individual en vida (premia la energía propia) se apaga en los cuerpos o frena la línea germinal? Si G1 da nulo, un control sin aprendizaje (`aprendizaje.activo=false`) es candidato.
