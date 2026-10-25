# 2026-10-25 · Fase 7: memoria de contexto, prerregistro

Escrito antes de correr. Antecedente: [exploración](2026-10-25-fase7-exploracion.md).

## Pregunta
En un mundo donde la única forma de saber qué comida es buena es recordar una pista intermitente, ¿evoluciona una memoria que siga a la estación y mejore las decisiones?

## Diseño (`experiments/fase7/evaluar.py`)
- **Mundo:** base, desde LUCA. Estaciones de 2000 pasos, toxicidad diferida (castigo 0,5) y pista con probabilidad 0,01.
- **Duración:** 200 000 pasos; semillas 141–146.
- **Condiciones:**
  - `mem_info`: memoria, pista informativa, sin aprendizaje;
  - `mem_ruido`: ídem con pista aleatoria (control: recordar no sirve);
  - `sin_memoria`: sin memoria, pista informativa;
  - `mem_info_apr`: memoria y pista informativa, con aprendizaje.
- **Métricas** (último cuarto, ~25 estaciones):
  - acierto al comer;
  - seguimiento de la memoria: promedio en el tiempo de (2m − 1) × estación, que vale ±1 si la memoria sigue a la estación y ≈ 0 si está fija;
  - genes de memoria.

## Hipótesis y reglas
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| M1 | Recordar mejora las decisiones | acierto `mem_info` > `mem_ruido`, pareada, p < 0,05 (con 6 semillas, las 6 a favor) | Incierta, probablemente no |
| M2 | La memoria sigue a la estación | \|seguimiento\| > 0,3 en ≥ 4 de 6 semillas de `mem_info` | Incierta, probablemente no |
| M3 | Tener memoria mejora frente a no tenerla | acierto `mem_info` > `sin_memoria`, p < 0,05 | Incierta |

## Cómo se interpretará
- **M1 y M2:** primera memoria evolucionada en el proyecto; seguiría reclutarla para coordinar o diferenciar dentro de los grupos.
- **Negativo:** la regla no lineal que hace falta es difícil de descubrir con este genoma. El siguiente paso sería darle al genoma una forma de combinar entradas, como genes que lean el producto de dos sensores o una segunda capa de regulación, antes de exigir memoria.
