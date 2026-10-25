# Proposal

## Why

Las fases 3 a 3d dejaron grupos coordinados de 3 a 16 miembros que se desarrollan de forma clonal desde una sola célula (84 %) y se reproducen con propágulos unicelulares. Pero sus miembros hacen todos lo mismo: no hay división del trabajo (`docs/bitacora/2026-10-24-fase4-exploracion.md`). La teoría predice que la especialización necesita un **compromiso con retornos crecientes** entre funciones. En esta física, comer y empujar se reparten linealmente. El caso biológico mejor documentado es la **restricción flagelar** de las algas volvocales: una célula no puede dividirse y moverse a la vez. Es la explicación clásica de la separación entre soma y germen en *Volvox* (Koufopanou 1994; Michod 2006).

## What Changes

- **Restricción flagelar** (`fisica.refractario_division`, 0 = desactivada): tras dividirse, progenitor e hijo no pueden avanzar durante T pasos. El genoma decide qué hace en su lugar.
- **Control aleatorio** (`fisica.refractario_modo = "aleatorio"`): períodos de T pasos sorteados en cada paso con la misma frecuencia por organismo que las divisiones de ese paso, sin relación con dividirse.
- **Contadores de vida por organismo** (avances y divisiones) y **métricas de especialización en grupos de 3 o más:** concentración reproductiva, correlación entre las tasas de avanzar y de dividirse, fracción de miembros que nunca se dividieron y fracción en período refractario.

## Capabilities

### Modified Capabilities
- `organismo`: restricción flagelar y contadores de vida.
- `experimentacion`: métricas y evaluación de la fase 4a.

## Impact

Cambian `config.py`, `poblacion.py` y `simulacion.py`. Se agrega `experiments/fase4/`. Con la restricción desactivada, la dinámica es idéntica.
