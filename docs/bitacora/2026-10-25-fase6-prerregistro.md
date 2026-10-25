# 2026-10-25 · Fase 6: memoria interna y corridas largas, prerregistro

Escrito antes de correr. Antecedentes: [fase 5](2026-10-25-fase5-exploracion.md). Cambio: `openspec/changes/fase-6-memoria/`.

## Pregunta
Con una memoria interna persistente y heredable, que permite interruptores biestables, y con ~1000–1500 generaciones de evolución, ¿aparecen dentro de los grupos estados distintos ligados a roles distintos (tipos celulares)?

## Diseño (`experiments/fase6/largo.py`)
- **Ancestros:** como en la fase 4a (LUCA → ecología de la fase 2c → 60 000 pasos con fuerza α = 0,5 y rumbo), semillas nuevas 131–135.
- **Ramas:** 600 genomas, refugio 3, fuerza, rumbo, mutación activa, 150 000 pasos.
- **Condiciones:**
  - `base`: sin memoria;
  - `memoria`: con memoria;
  - `eco`: γ = 2 y κ = 0,5, sin memoria;
  - `eco_memoria`: γ = 2 y κ = 0,5, con memoria.
- **Medición:** la ventana final, entre el 90 y el 100 % de la corrida; también la del medio, como serie.

## Piloto (semilla 601, 30 000 pasos)
Los genes de memoria aparecen en el 1–8 % de la población y se pierden. La memoria media queda cerca de 0 y no hay dispersión de memoria ni de roles.

## Hipótesis y reglas
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| L1 | Con memoria, los roles dentro de los grupos son más diversos | dispersión de roles en grupos: memoria > base, y eco_memoria > eco, pareada, p < 0,05 | **Probablemente no** |
| L2 | La memoria se diferencia dentro de los grupos | dispersión de la memoria en grupos > 0,1 en ≥ 3 de 5 semillas | Probablemente no |
| L3 | La memoria se asocia al rol | \|correlación memoria–rol\| > 0,3 en ≥ 3 de 5 semillas | Probablemente no |

Con 5 semillas, la prueba pareada solo puede dar p < 0,05 si las 5 van en la misma dirección (mínimo 1/32). Es un experimento de búsqueda: un resultado positivo pediría una réplica.

## Cómo se interpretará
- **Positivo (L2 y L3):** primeros tipos celulares, a confirmar con réplica, ablación de la memoria y jardín común.
- **Negativo:** con estos ingredientes y este tiempo, la división del trabajo no emerge. El siguiente paso es atenuar el conflicto entre niveles (que empujar le rinda también a quien empuja) antes de agregar más maquinaria.
