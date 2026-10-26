# 2026-10-26 · Fase 11: modulación por el estado interno, prerregistro

Escrito antes de correr. Antecedentes: [fase 10](2026-10-26-fase10-evaluacion.md). La memoria de la pista evolucionó y acierta la estación en el 99–100 % de los organismos, pero no se usa para decidir. Un gen que se enciende o se apaga (±1) no alcanza para torcer decisiones que los genes evolucionados ya saturan.

## Cambios (opcionales; con todo apagado, las huellas de referencia no cambian)
- **Modulación** (`herencia.modulacion`):
  - dos condiciones nuevas por gen (5 y 6): la memoria A o B cambia el signo de la respuesta del gen a los receptores químicos (el tipo de comida de la celda): z = b + w·s + (2m − 1 − 1)·w_q·s_q;
  - un solo gen "avanzar si el tipo de comida no coincide con lo recordado" cabe en un gen;
  - modular un gen que no mira el tipo de comida es neutro.
- **Decisión estocástica** (`fisica.decision = "softmax"`, `temperatura`):
  - la acción se sortea con probabilidad ∝ exp(impulso / T), con descansar siempre disponible con impulso ≥ 0. Con argmax, eso equivale a "descansar si nada es positivo";
  - un cambio chico de impulso cambia un poco la probabilidad;
  - las poblaciones de la fase 10 son viables con T = 0,1–0,5 (con T = 0,25, ~20 % menos organismos).
- **Memoria inicial 0,5:** sin información, el estado digestivo queda neutro en cada estación. Corrige la causa de las extinciones de los controles en la fase 10.

## Pilotos (poblaciones 183 y 188 de la fase 10; no entran en la evaluación)
1. **Competencias** (sin mutación, 20 000 pasos, 4 poblaciones × 2 semillas): genes modulados agregados a poblaciones con memoria, contra un control con los mismos genes en cero.

   | Genes agregados | Gana |
   |---|---|
   | Dos genes modulados de avanzar | 7 de 8 |
   | Comer + dos de avanzar | 8 de 8 |
   | Uno de avanzar | 2 de 8 |
   | Uno de comer | 0 de 8 |

   - **Diagnóstico:** el mutante come comida mala en el 0,7 % de sus acciones, contra el 18 % del control. **La modulación resuelve el problema de magnitud** de la fase 10.
   - **Camino evolutivo:** gen de avanzar modulado → duplicación (que copia la condición) → comer modulado.
   - (Una primera versión de los genes de prueba daba 0/8 por un error de diseño: sin el sesgo, "comía" en celdas vacías del tipo correcto.)
2. **Evolución, 100 000 pasos (~800–1000 generaciones), tres variantes:**
   - modulación de todas las entradas del gen;
   - modulación solo del receptor químico;
   - lo anterior con softmax.

   En las tres, sin diferencias con el control: acierto 0,52–0,54. Los genes modulados se difunden (hasta el 57 %), pero sin uso.
   - **Diagnóstico:** cada gen satura su tanh (pesos de ~10–20 sobre "recurso aquí"), así que un peso chico sobre el tipo de comida no cambia nada, ni siquiera con softmax.
   - **De dónde podría salir el gradiente:** de genes nuevos, no saturados, que necesitan tres piezas: el gen, la condición de modulación y el peso sobre el tipo de comida. Cada una es neutra sin las otras y tiene costo por gen.
   - Hace falta más tiempo evolutivo.

## Diseño
- `python experiments/fase11/evaluar.py`, parte A.
- **Punto de partida:** las 6 poblaciones finales de la fase 10 cuya memoria sigue a la pista (181, 183, 184, 186, 187, 188). Cada corrida usa 600 organismos muestreados de una población.
- **Mundo:** el de la fase 10 con memoria inicial 0,5 y toxicidad plena desde el inicio (las poblaciones ya están adaptadas).
- **Duración:** 300 000 pasos (~2000–3000 generaciones).
- **Condiciones:** `a_mod` y `a_sin_mod` (argmax); `a_mod_softmax` y `a_sin_mod_softmax` (T = 0,25). Las comparaciones son pareadas por población de origen.

## Hipótesis y reglas
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| **A1** | Con modulación, la memoria se recluta para decidir | acierto `a_mod` > `a_sin_mod`, pareada, p < 0,05 (con 6 pares, el mínimo es 0,016) | Baja |
| A2 | Uso fuerte | acierto de `a_mod` > 0,6 en ≥ 3 de 6 | Baja |
| **A3** | Con decisión estocástica | acierto `a_mod_softmax` > `a_sin_mod_softmax`, p < 0,05 | Baja a moderada |
| A4 | Uso fuerte con softmax | acierto de `a_mod_softmax` > 0,6 en ≥ 3 de 6 | Baja |

## Cómo se interpretará
- **A1 o A3 positivas:** **primera memoria usada para decidir.** Un organismo evolucionado actúa según información que ya no está presente. Seguiría la ablación (fijar la memoria y medir la caída del acierto) y luego la parte B (todo desde LUCA).
- **Negativo:** el reclutamiento choca con la saturación de los genes. Las opciones serían:
  - una regla de decisión menos saturable (impulsos sin tanh por gen, o una tanh sobre la suma);
  - mutaciones de peso con colas largas (saltos ocasionales grandes, como las inserciones en biología);
  - medir directamente la evolucionabilidad: cuántas mutaciones al azar cambian el acierto.
