# 2026-10-24 · Fase 3c: movimiento de grupos por fuerza, prerregistro

Escrito antes de correr la evaluación. Cambio de modelo justificado por las fases 3 y 3b; detalle en `openspec/changes/fase-3c-fuerza/`.

## Pregunta
Si los grupos se mueven por la suma de las fuerzas de sus miembros, sin umbral, ¿crecen cuando el depredador lo exige? ¿Cuánto se debe a la física y cuánto a que los miembros coordinen su rumbo?

## Diseño (`experiments/fase3c/evaluar.py`)
- Igual que la fase 3: un ancestro por semilla y 600 genomas sembrados en cada condición, con el refugio subiendo de 2 a 3 entre los pasos 2000 y 32 000, en 60 000 pasos.
- **Nueve condiciones:** movimiento (`empuje`, `fuerza` con α = 1, `fuerza05` con α = 0,5) × percepción (`base`, `ambos` = rumbo y señales, `barajado`). El control barajado es la versión corregida tras la revisión de la fase 3.
- **Semillas 61–70** (piloto: 301).
- **Variable principal:** fracción en grupos de 3 o más en el último cuarto (una corrida extinta cuenta como 0).
- **Alineación:** solo en corridas con ≥ 20 pares enlazados por registro.

## Piloto (semilla 301, ancestro de la fase 2c, 30 000 pasos, sin barajado)
| Condición | Grupos ≥ 3 (final) | Alineación |
|---|---|---|
| fuerza α = 1, base | 0,01 | 0,66 |
| fuerza α = 1, ambos | 0,00 | 0,78 |
| fuerza α = 0,5, base | 0,09 | 0,11 |
| fuerza α = 0,5, ambos | **0,55** | 0,75 |

## Hipótesis y reglas
| # | Predicción | Regla | Expectativa según el piloto |
|---|---|---|---|
| F1 (por α) | La física sola hace crecer los grupos | `fuerza_base` supera a `empuje_base` por ≥ 0,2 en ≥ 70 % | α = 0,5: probablemente no; α = 1: no |
| **F2** (por α) | **Con fuerza, la información sobre los socios aumenta los grupos** | `fuerza_ambos` supera a `fuerza_barajado` por ≥ 0,1 en ≥ 70 % | **α = 0,5: sí**; α = 1: no |
| F3 (por α) | La información rinde más con fuerza que con empuje (interacción) | (fuerza_ambos − fuerza_barajado) − (empuje_ambos − empuje_barajado) ≥ 0,1 en ≥ 70 % | α = 0,5: sí |
| F4 (por α) | La alineación evoluciona por la información | alineación de `fuerza_ambos` supera a la de `fuerza_barajado` por ≥ 0,2 en ≥ 70 % (semillas con ≥ 20 pares en ambas) | sí |

## Qué haría cambiar de rumbo
- **F2 y F3 se cumplen con α = 0,5:** la coordinación emerge y rinde cuando la física no tiene un valle. Se adopta "fuerza" con α = 0,5 como modelo y se pasa a la fase 4 (el colectivo como individuo) sobre esos grupos.
- **F1 se cumple pero F2 no:** los grupos crecen por la física, sin coordinación. Se puede pasar a la fase 4 igual, pero sin afirmar que la coordinación emergió.
- **Nada se cumple:** revisar otros límites del tamaño de grupo (por ejemplo, el alimento de las celdas interiores) antes de seguir.
