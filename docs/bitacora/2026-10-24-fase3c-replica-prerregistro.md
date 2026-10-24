# 2026-10-24 · Fase 3c, réplica: ¿la información aumenta la probabilidad del régimen con grupos?

Escrito antes de correr. La hipótesis surge de mirar las semillas 61–70 ([evaluación](2026-10-24-fase3c-evaluacion.md)), por eso se prueba con **semillas nuevas, 71–90**, sin reutilizar aquellas.

## Diseño
- `experiments/fase3c/evaluar.py`, solo con `fuerza05_base`, `fuerza05_ambos` y `fuerza05_barajado`.
- Semillas 71–90 (20), 60 000 pasos, el resto igual que en la fase 3c.

## Hipótesis y reglas (las calcula el script: `R1`, `R2`)
| # | Predicción | Regla |
|---|---|---|
| **R1** | Con percepción del rumbo, más poblaciones terminan en el régimen con grupos | Corridas con fracción en grupos ≥ 3 de al menos 0,2: `ambos` > `barajado`, con Fisher exacto de una cola p < 0,05 |
| R2 | Dentro del régimen con grupos, la información no reduce el tamaño | Media de la fracción en grupos ≥ 3 entre corridas en régimen: `ambos` ≥ `barajado` (descriptiva) |
| R3 (control) | Barajar no es peor que no percibir | Corridas en régimen: `barajado` y `base` no difieren con Fisher de dos colas p < 0,05 |

## Qué haría cambiar de rumbo
- **R1 se cumple:** la información sobre los socios ayuda a conservar la asociación y a formar grupos cuando la física no tiene un valle. Se adopta "fuerza" con α = 0,5 y se pasa a la fase 4 (el colectivo como individuo) con percepción del rumbo.
- **R1 no se cumple:** el efecto de la información, si existe, es chico. Igual se adopta "fuerza" con α = 0,5, porque es la única regla con la que aparecen grupos de 3 o más, pero sin afirmar que la coordinación sea la causa. La fase 4 parte de esa física.
