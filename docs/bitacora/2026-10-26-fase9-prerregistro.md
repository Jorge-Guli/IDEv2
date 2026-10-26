# 2026-10-26 · Fase 9: regulación genética condicionada, prerregistro

Escrito antes de correr. Antecedentes: [fase 8](2026-10-26-fase8-evaluacion.md). Allí la memoria no evolucionó en ~3000 generaciones, y el diagnóstico fue un cuello de botella en la arquitectura del genoma: combinar "qué comida hay" con "qué recuerdo" exigía una regla de cinco genes con pesos coordinados.

## Qué cambia
- **Condición de expresión por gen** (campo heredable `cond`, 5 valores): el gen se expresa siempre, o solo si la memoria A (o B) está alta (> 0,5), o solo si está baja.
- **Mutación de la condición:** la condición muta (`herencia.k_condicion = 0,3`, escalado por la tasa de mutación) solo si la memoria está permitida. Con la memoria apagada, la dinámica es idéntica a la anterior: las huellas de las corridas de referencia coinciden.
- **Rampa de toxicidad** (`estaciones.rampa_toxicidad`): la comida fuera de estación pasa de nutrir como la buena a la toxicidad plena en N pasos.
- Métrica nueva: `con_gen_condicionado`.
- **Métrica de seguimiento corregida:** era la media de (2m − 1)·estación y daba ±1 para una memoria fija en ventanas de una sola estación. Ahora es la covarianza entre memoria y estación en la ventana. En las ventanas largas de las fases 7–8, el sesgo anterior es de ±0,05 como máximo, así que sus conclusiones no cambian.

## Pilotos (semillas 901–916, no entran en la evaluación)
1. **Desde LUCA puro, 100 000 pasos (400–1000 generaciones), mundo mosaico como en la fase 8:** el acierto queda entre 0,51 y 0,56 en las cuatro condiciones, y los genes de memoria se pierden.
2. **Sembrando un gen de memoria conectado a la pista:**
   - todas las corridas se extinguieron temprano.
   - **Causa:** con toxicidad plena desde el paso 0, LUCA (sembrado o no) colapsa a unas decenas de organismos en los primeros 1000 pasos, por el veneno diferido. Pasa en la mitad de las semillas.
   - **Solución:** con una rampa de toxicidad de 20 000–30 000 pasos, no hay extinciones tempranas.
3. **Con rampa de 30 000 pasos, 100 000 pasos en total:**
   - no hay efecto (acierto 0,51–0,55 en todas las condiciones);
   - en `sem_info`, el gen de memoria sembrado cae del 100 % al ~20 % en 8000 pasos, más rápido que sin regulación.
   - **Interpretación probable:** las mutaciones de condición sobre los genes de LUCA hacen que una memoria cambiante apague genes útiles la mitad del tiempo.
4. **El mundo premia la regulación bien armada:**
   - **Diseño:** LUCA con un módulo de memoria de cinco genes condicionados (memoria A ← pista; comer y avanzar condicionados a la memoria, mirando solo el tipo de comida) compite contra LUCA con los mismos genes en cero.
   - **Resultado:** con toxicidad plena, gana en 6 de 6 semillas (2 a 10 000 pasos y 4 a 20 000).
5. **Mapa de los pasos intermedios** (módulos parciales contra LUCA, toxicidad plena, 4 semillas, varias extintas):
   - memoria + avanzar condicionado: gana en 2/2 de las semillas con sobrevivientes;
   - comer condicionado sin avanzar, con o sin memoria: pierde siempre, porque el organismo se queda quieto sobre la comida que no debe comer;
   - avanzar condicionado sin gen de memoria: pierde;
   - gen de memoria solo: resultados dispersos, por los cuellos de botella.
   - **Conclusión:** existe un camino gradual (memoria → avanzar condicionado → comer condicionado), pero el primer paso es neutro y cuesta energía.
   - **Con la rampa activa, hasta el módulo completo pierde:** mientras la comida fuera de estación nutre, rechazarla es una desventaja. La selección a favor de la memoria empieza recién cuando la rampa termina.

## Diseño
- `python experiments/fase9/evaluar.py`.
- **Mundo:** el mosaico de la fase 8 (castigo 0,2, toxicidad diferida, pista 0,01, estaciones de 2000 pasos, memoria con tasa 1), sin aprendizaje, con rampa de toxicidad de 30 000 pasos.
- **Duración:** 300 000 pasos (~1000–3000 generaciones); semillas nuevas 171–178 (8, por las extinciones esperables).
- **Condiciones:**
  - `sem_info`: LUCA + gen de memoria A conectado a la pista; regulación posible.
  - `sem_ruido`: igual, con la pista aleatoria (control: la memoria no informa).
  - `sem_sin_reg`: igual a `sem_info`, pero las condiciones no mutan (control: sin regulación).
  - `luca_info`: LUCA puro, regulación posible (¿aparece todo desde cero?).

## Hipótesis y reglas (las calcula el script)
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| **R3** | La regulación permite usar la memoria | acierto final de `sem_info` > 0,6 en ≥ 4 semillas | Baja (pilotos negativos) |
| R1 | El beneficio viene de la información | acierto `sem_info` > `sem_ruido`, pareada, p < 0,05 | Baja |
| R2 | El beneficio requiere la regulación | acierto `sem_info` > `sem_sin_reg`, pareada, p < 0,05 | Baja |
| R4 | Todo aparece desde LUCA | acierto final de `luca_info` > 0,6 en ≥ 4 semillas | Muy baja |

Medidas exploratorias: el seguimiento (covarianza entre memoria y estación; > 0,3 indicaría una memoria funcional) y la fracción de organismos con genes condicionados.

Control de fugas: `sem_ruido` y `sem_sin_reg` deberían quedar en ~0,5–0,55. Si superan claramente 0,6, se investiga antes de interpretar.

## Cómo se interpretará
- **R3, R1 y R2 positivas:** la regulación condicionada destraba la memoria. Sería el primer uso evolucionado de un estado interno para decidir. Seguirían la ablación (fijar la memoria en poblaciones evolucionadas), el análisis de qué genes se condicionaron y, después, R4 con más tiempo.
- **Negativo:** aunque existe un camino gradual, la evolución no lo recorre en ~2000 generaciones. Los pilotos sugieren por qué: el primer paso (mantener una memoria que sigue a la pista) no se premia por sí solo y se pierde por costo y deriva en unos miles de pasos. Seguiría hacer que la memoria sea más barata o robusta en la física (por ejemplo, una zona muerta ante impulsos pequeños), o un mundo donde una memoria sin uso todavía tenga algún valor. Esos cambios se evaluarán por separado, con su propio control.
