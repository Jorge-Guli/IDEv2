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
