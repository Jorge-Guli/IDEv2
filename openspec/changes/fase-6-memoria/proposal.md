# Proposal

## Why

La fase 4 dejó grupos clonales con un ciclo de vida, pero sin división del trabajo. En la fase 5 se agregaron los ingredientes que pide la teoría (retornos crecientes a la especialización y energía compartida), y en los pilotos no apareció nada (`docs/bitacora/2026-10-25-fase5-exploracion.md`). El diagnóstico tiene dos partes:
- el aprendizaje individual premia la tarea que paga al individuo, que es comer;
- los organismos no tienen un **estado interno estable** que permita tipos celulares.

En biología, la diferenciación se apoya en estados regulatorios biestables que persisten y se heredan al dividirse (memoria epigenética). Es el paso C de la hoja de ruta. Como la evolución tiene que descubrir el interruptor y su uso, se combina con corridas largas (paso D).

## What Changes

- **Maquinaria por uso** (fase 5, `fisica.maquinaria_*`): promedio móvil del uso de comer y de avanzar; la eficiencia (k / k_ref)^γ, con tope, multiplica el rendimiento al comer y el peso del empuje. Con γ = 0 no tiene efecto.
- **Puentes citoplasmáticos** (fase 5, `asociacion.difusion_energia`, `difusion_aprende`): la energía se difunde por los enlaces y se conserva. Una opción decide si cuenta para el aprendizaje.
- **Memoria interna** (paso C, `memoria.*`): dos variables en [0, 1] por organismo. Las primitivas `memoria_a` y `memoria_b` no ocupan la acción y suman `tasa` × impulso. Dos sensores leen la memoria propia, y el hijo la hereda.
- **Métricas:** dispersión de roles (índice de uso comer/avanzar) en los grupos y en la población; memoria media, su dispersión en los grupos y su correlación con el rol.

## Capabilities

### Modified Capabilities
- `organismo`: maquinaria por uso y memoria interna.
- `asociacion`: puentes citoplasmáticos.
- `experimentacion`: métricas de roles y memoria; corridas largas de la fase 6.

## Impact

Cambian `genoma.py` (dos primitivas y dos sensores), `simulacion.py`, `poblacion.py` y `config.py`. Con todo apagado la dinámica es la misma, pero el genoma cambia de forma: los resultados anteriores se reproducen en sus commits, y los genomas guardados se completan con pesos nulos al cargarlos.
