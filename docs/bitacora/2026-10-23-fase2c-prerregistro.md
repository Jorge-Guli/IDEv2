# 2026-10-23 · Fase 2c: prerregistro de hipótesis

Escrito **antes** de la evaluación (`experiments/fase2c/evaluar.py`, 6 condiciones × 10 semillas × 30 000 pasos).

## Contexto
- **Física:** la base, con asociación, movimiento de grupos por empuje y un depredador limitado por tamaño. En cada paso, cada organismo es atacado con probabilidad 0,015; el ataque mata con probabilidad 1 − (tamaño − 1)/(refugio − 1), con refugio = 2, es decir, los sueltos mueren y los grupos de 2 o más quedan a salvo. Ver `experiments/configs/depredacion.toml`.
- **Calibración** (pilotos de 2 semillas): con intensidad 0,02 todo se extingue y con 0,01 o menos no hay efecto. Con 0,015 y refugio 2, desde LUCA, ~92 % de la población terminó en grupos en 2 de 2 semillas; con depredación uniforme, 0–7 %. Con refugio 3, una semilla se extinguió y la otra llegó al 30 % enlazado.
- Los pilotos sirvieron para elegir los parámetros; **la evaluación usa las semillas 1–10**, que incluyen las 2 del piloto. Por eso el criterio exige ≥ 8/10.

## Hipótesis
Medidas del último cuarto de cada corrida.

| # | Hipótesis | Predicción |
|---|---|---|
| P1 | Con refugio por tamaño, la asociación evoluciona desde LUCA | `refugio`: `frac_en_refugio` > 0,5 en ≥ 8/10 |
| P2 | La causa es el refugio, no la mortalidad | `uniforme`: `frac_en_refugio` < 0,1 en ≥ 8/10 |
| P3 | La asociación es la que protege (no otro rasgo) | `refugio_asoc_inerte`: `frac_en_refugio` = 0 y población media menor que `refugio` en ≥ 8/10 semillas pareadas |
| P4 | Asociarse aumenta la población sostenible bajo el depredador | `refugio` > `uniforme` en población, en ≥ 8/10 semillas pareadas |

**Exploratorias** (sin umbral): tamaño de los grupos (¿pasan de pares?), velocidad de la transición (paso en que se supera el 50 % de enlazados), si los grupos son clonales (distancia de etiqueta), si aparecen compartir y aprovechados, el efecto del modo de movimiento (`refugio_unanime`) y el refugio 3.

## Decisiones según el resultado
- **P1–P4 se cumplen** → primera condición identificada en la que la asociación evoluciona por sí sola. Siguiente paso: fase 3 (el colectivo como individuo), con este mundo como base. ¿Se reproducen los grupos como unidad? ¿Aparece división del trabajo?
- **P1 sí y P2 no** → la mortalidad por sí sola favorece la asociación; revisar el mecanismo antes de seguir.
- **P1 no** → los pilotos fueron casualidad; revisar la calibración (intensidad y refugio).
