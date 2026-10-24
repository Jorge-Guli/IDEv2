# Proposal

## Why

Las fases 2 y 2b mostraron que asociarse no rinde ni en la física base ni con un bien público. En el segundo caso, el parentesco espacial ya cumplía la función esperada. Para que la asociación pague, el grupo tiene que obtener algo que **solo se consigue estando físicamente juntos**. El mecanismo con mejor respaldo experimental es la **depredación limitada por tamaño**: *Chlorella vulgaris* evolucionó colonias en menos de 100 generaciones bajo un depredador que solo podía tragar células sueltas (Boraas et al. 1998), y *Chlamydomonas reinhardtii* repitió el resultado (Herron et al. 2019).

## What Changes

- **Depredación** como física del mundo: en cada paso, cada organismo sufre un ataque con una probabilidad configurable, que es mortal solo si su grupo conexo es más chico que un tamaño de refugio configurable (el depredador no puede tragar grupos grandes).
- **Control de depredación uniforme**: la misma probabilidad de ataque mortal, sin refugio por tamaño.
- Se activa con `depredacion.activa` (desactivada por defecto).
- Métricas: muertes por depredación y fracción de organismos en grupos refugio.
- Se reutilizan las primitivas de asociación y el movimiento por empuje de las fases anteriores.

## Capabilities

### New Capabilities
- `depredacion`: mortalidad por ataque, refugio por tamaño de grupo, control uniforme y métricas.

### Modified Capabilities
- `experimentacion`: la configuración de la depredación y los criterios de la fase 2c.

## Impact

Cambian `src/simbio/simulacion.py` (paso de depredación y métricas) y `config.py`. Se agregan `experiments/configs/depredacion.toml` y `experiments/fase2c/`. Con la depredación desactivada, todo sigue igual.
