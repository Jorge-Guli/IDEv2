# 2026-10-29 · Fase 12: mundo del texto (pilotos)

## Idea
La serie de la luz mostró que una señal solo importa si cambia la supervivencia, y que el mundo casi nunca premia predecir. El mundo del texto hace que predecir sea la forma de comer bien:
- Un texto real pasa letra por letra (500 pasos cada una) y decide la estación: vocal nutre el tipo A, consonante el B.
- El sensor "pista" muestra siempre la letra **anterior**, nunca la vigente.
- Como en castellano vocales y consonantes se alternan, "invertir la pista" acierta ~0,76. Seguirla acierta ~0,24, y la frecuencia base es ~0,55.
- **Control:** las mismas letras barajadas. Ahí no hay secuencia y nada supera la base.

Techos medidos (solo conteos de letras):

| Texto | Letras | Vocales | Seguir la pista | Orden 1 | Orden 2 y 3 |
|---|---|---|---|---|---|
| Calibración (docs 00, 01, 04 y 06 del proyecto) | 22 525 | 0,455 | 0,242 | 0,758 | 0,758 |
| Asimov, los dos cuentos (`datos/textos/`, sha256 `5a985d7c…` y `d6548766…`, ignorados por Git) | 34 307 | 0,458 | 0,242 | 0,758 | 0,758 |

- Con dos clases, mirar más de una letra atrás no agrega nada.
- Los dos textos tienen la misma estructura en este nivel.

Motor: `texto.*` (apagado por defecto), `src/simbio/texto.py`, `tests/test_texto.py`. Las huellas no cambian.

## Piloto 1 (calibración, semillas 1–3, 100 000 pasos)
- **Resultado:** acierto 0,52–0,53 en las dos condiciones, sin diferencia (p = 0,75). Ni siquiera llega a la base (0,545).
- **Por qué:** "comer el tipo contrario a la pista" es un **O exclusivo**: comer si el tipo y la pista difieren. Un gen lineal (pesos sobre los sensores) no puede expresarlo; la suma de las condiciones se contradice.
- **Lo que sí podría hacerlo:** la vía con memoria, en tres pasos:
  1. un gen de memoria que escriba "la pista fue consonante";
  2. genes de comer condicionados a la memoria (fase 9);
  3. un signo distinto para cada caso.
- Son tres piezas coordinadas que la evolución no encontró en 100 000 pasos. En la semilla 1, la memoria se fijó en el 99 % de la población, pero no quedó alineada con la letra.

## Piloto 2 (en curso)
- **Sensor opcional `texto.sensor_coincide`:** `tipo_aqui × pista` (+1 si la comida de acá es la que nutría la letra anterior). Con él, "comer si no coincide" lo resuelve un solo gen.
- **Es una ayuda de percepción, no una solución dada:** el sensor también existe en el control barajado, donde no sirve, porque ahí la pista no predice nada.
- Si funciona, el experimento oficial con Asimov mide si la evolución aprovecha la estructura del lenguaje. La memoria queda para clases más ricas (más de dos), donde mirar más atrás sí paga.
- **Corrida:** semillas 1–3, 200 000 pasos.
- **Resultado:** igual que sin el sensor. Acierto 0,52–0,54 en las dos condiciones, sin diferencia (p = 0,5). Ninguna llega a 0,545.
- La memoria A se fija en algunas corridas (texto 2 y 3: 93–99 %) y desaparece en otras, sin relación con el acierto.

## Diagnóstico en curso
- Si con un sensor que hace la regla de un solo gen tampoco aparece, el problema no es la predicción: es que **casi no discriminan qué comida comer**.
- Ese 0,53 es el mismo que en el archipiélago (0,53–0,55, con estaciones y pista rara), y en todo el mundo de la fase 11 el acierto apenas sube de 0,5.
- **Prueba:** el mundo de la fase 11 con la pista de la estación **vigente** siempre visible (`p_pista = 1`), donde basta reaccionar. Con castigo 0,2 y con castigo 1,0. Si ni así suben de ~0,55, el techo está en la presión para discriminar, no en predecir.

## Resultado del diagnóstico: el castigo de 0,2 casi no selecciona la discriminación
Corridas con `reina_roja.py --condiciones sin`, mundo de `vivo.toml`, semillas 1–2, 100 000 pasos:

| Mundo | Castigo | Acierto al final |
|---|---|---|
| Estación cambiante, pista vigente siempre visible | 0,2 | 0,52 y 0,52 |
| Ídem | 1,0 | extintas (~31 000, al terminar la rampa de toxicidad) |
| Estación **fija** (comer bien es "comer el tipo A", un gen lineal) | 0,2 | 0,53 y 0,51 |
| Estación fija | **0,5** | 0,55 y **0,997** |

- Con castigo 0,2, **ni siquiera con la estación fija** se aprende a elegir la comida: comer la equivocada cuesta tan poco que no conviene buscar otra.
- Con 0,5, en una de dos semillas la discriminación aparece y se vuelve casi perfecta.
- **Consecuencia para fases anteriores:** en el mundo de las fases 7 a 11 (castigo 0,2), la presión para distinguir la comida era mínima. Eso explica en parte por qué la memoria y la pista casi no se usaron. Hay que revisarlo al actualizar el ODD.
- **Siguiente:** piloto 3 del texto con castigo 0,5 y el sensor coincide.

## Piloto 3 (castigo 0,5, sensor coincide, semillas 1–3, 200 000 pasos): extinciones
- **Extinciones:** 4 de 6, todas al terminar la rampa de toxicidad (pasos 30 878–56 244). Con letras que cambian cada 500 pasos, el veneno a pleno llega antes de que la discriminación evolucione.
- **Sobrevivientes (semilla 3):** acierto 0,551 con el texto y 0,540 barajado. Llega a la base, pero no hay predicción todavía.
- **Siguiente:** piloto 4 con la rampa de toxicidad en 150 000 pasos, para que la discriminación tenga tiempo de aparecer mientras el veneno sube, y 300 000 pasos en total.

## Piloto 4 (castigo 0,5, rampa de toxicidad 150 000, coincide, semillas 1–3, 300 000 pasos): sin predicción
- **Texto:** 3 de 3 vivas, acierto final 0,536–0,549. Es la base: comer siempre el tipo de las consonantes. Sin predicción.
- **Barajado:** 2 de 3 extintas (194 811 y 282 635). La semilla 1 llegó a 0,59 antes de extinguirse.
- **Lectura:** la rampa larga evita las extinciones con el texto, pero la población se queda en la estrategia de la base.
- **Pregunta de diagnóstico:** ¿pueden *reaccionar* a letras que cambian cada 500 pasos, aunque sea sin predecir? Para responderla, opción `texto.pista = "vigente"`: la pista muestra la letra vigente y "comer si coincide" resuelve todo con un gen. Si así tampoco pasan la base, el obstáculo es seguir un mundo que cambia tan rápido (digestión, veneno diferido), no la predicción.

## Diagnóstico reactivo (`texto.pista = vigente`, mismo mundo que el piloto 4): tampoco
- Viendo la letra **vigente**, con un sensor que hace la regla de un solo gen ("comer si coincide"), el acierto queda en 0,53–0,55 en las 6 corridas (1 extinción en el barajado).
- **Conclusión:** el obstáculo no es predecir, es **seguir una comida buena que cambia cada 500 pasos**. Candidatos:
  - la inercia de la digestión (100 pasos), que premia quedarse con un tipo;
  - el veneno diferido, que separa el error de su costo;
  - una presión todavía débil.
- **Siguiente diagnóstico:** dos variantes reactivas, cada una cambiando una sola cosa:
  - (a) sin digestión inducible (`estaciones.induccion = 0`);
  - (b) letras de 2000 pasos, como las estaciones de la fase 11.

## Resultado de los diagnósticos reactivos
| Variante (pista vigente, coincide, castigo 0,5, rampa 150 000, 300 000 pasos) | Acierto final, texto | Barajado |
|---|---|---|
| Base (piloto reactivo) | 0,53–0,54 | 0,53–0,55 |
| (a) **Sin digestión inducible** (`induccion = 0`) | 0,55, **0,97**, 0,54 | 0,57, 0,56, 0,54 |
| (b) Letras de 2000 pasos | 0,54, 0,54 (1 extinta) | 0,53–0,54 |

- **Sin la inercia de la digestión,** una población (texto, semilla 2) descubrió cómo seguir la comida: el acierto subió de 0,54 a 0,78 entre los pasos 200 000 y 260 000, y a 0,97 al final.
- La digestión inducible, que premia quedarse con un tipo, era un freno para seguir cambios rápidos.
- El descubrimiento es un **evento raro** (1 de 6 en 300 000 pasos, como 1 de 2 con la estación fija). Hacen falta corridas más largas o más semillas.
- **Alargar las letras no ayuda.**
- **Consecuencia para el diseño:** con `coincide`, la regla reactiva ("comer si coincide") y la predictiva ("comer si NO coincide con la letra anterior") tienen la misma complejidad: un gen. Lo que cambia es el premio (1,0 contra ~0,76).
- **Siguiente:** piloto 5, la tarea real (`pista = anterior`) con `induccion = 0`, castigo 0,5, rampa 150 000 y 500 000 pasos.

## Piloto 5 (la tarea real: pista anterior, coincide, sin digestión inducible, castigo 0,5, rampa 150 000, 500 000 pasos)
- **Texto:** acierto final 0,534, **0,579** y 0,549. **Barajado:** 0,548, 0,551 y 0,537. Sin extinciones. R1: p = 0,375.
- Solo la semilla 2 del texto pasa la base (0,545) y el barajado. Sube de forma sostenida de 0,553 (paso 179 000) a 0,58, que es un aprovechamiento parcial de la alternancia, lejos del techo de 0,758.
- **Lectura:** el cuello de botella es la **tasa de descubrimiento**. La regla es de un gen, pero aparece en pocas poblaciones. Con 1 de 3 y diferencias chicas, un prerregistro de 8 semillas tendría poca potencia.
- **Siguiente:** estimar la tasa de descubrimiento con más semillas (texto, semillas 4–9). Opciones para subirla sin tocar los principios: poblaciones más grandes (más mutantes por generación; ahí la GPU sí ayudaría), más tiempo o una presión mayor.

## Tasa de descubrimiento (texto, semillas 4–9, mismo mundo que el piloto 5)
- **Último tercio:** 0,575, extinta (155 692), 0,561, 0,549, 0,555, 0,532.
- **Junto con el piloto 5 (8 corridas vivas):** 4 superan a todos los barajados (0,555–0,579 contra un máximo barajado de 0,551).
- Se pasa al prerregistro con los textos de Asimov: `2026-10-30-fase12-asimov-prerregistro.md`.

