# Proposal

## Why

En la fase 2c la asociación evolucionó sola bajo un depredador limitado por tamaño, pero los grupos son casi siempre pares. La exploración previa (`docs/bitacora/2026-10-24-fase3-exploracion.md`) mostró por qué:
- si el depredador escala y un par deja de estar a salvo, la población **abandona la asociación** en vez de formar grupos más grandes;
- los grupos de 3 o más **no pueden moverse**: cada miembro gira por su cuenta, sin percibir hacia dónde apuntan sus socios, y el empuje colectivo casi nunca alcanza el umbral; quedan quietos y pasan hambre;
- cuando mover al grupo no exige alinearse (control de física "fácil"), los grupos crecen y siguen al depredador (tamaño medio 4,2–4,8 con refugio 4).

El techo de tamaño es, entonces, un problema de **coordinación**. Antes de que el colectivo pueda volverse un individuo (reproducción del grupo, especialización), sus miembros tienen que poder actuar juntos. La hoja de ruta preveía este caso como el disparador del paso B (comunicación). En biología, la coordinación de las colonias se apoya en señales por contacto y en la orientación compartida de las células (por ejemplo, la polaridad de los flagelos en *Volvox*).

## What Changes

- **Percepción del rumbo de los socios** (`coordinacion.rumbo`): tres sensores locales, por contacto con los enlazados: seno y coseno del rumbo medio de los socios respecto del propio, y fracción de socios que avanzaron en el paso anterior. La física no impone ninguna conducta: un gen tiene que conectar esos sensores con girar o avanzar.
- **Canal de señales** (`coordinacion.senales`): primitiva `senalar` cuyos genes no compiten por la acción del paso, sino que fijan una salida continua en [0, 1] que cuesta energía; sensores de la señal media de los socios y de la señal propia del paso anterior (una memoria mínima).
- **Control barajado** (`coordinacion.barajar`): los mismos sensores reciben los valores de otro organismo al azar.
- **Escalada del refugio** (`depredacion.refugio_final`, `escalada_inicio`, `escalada_pasos`): el tamaño de grupo que el depredador no puede tragar sube linealmente.
- **Métricas de coordinación:** alineación del rumbo entre enlazados, éxito del empuje colectivo (en general y en grupos de 3 o más) y señal media.
- Los genomas guardados con menos sensores se completan con pesos nulos al cargarlos.

## Capabilities

### New Capabilities
- `coordinacion`: sensores de rumbo y empuje de los socios, canal de señales, control barajado y métricas.

### Modified Capabilities
- `depredacion`: escalada del refugio.
- `experimentacion`: configuración y criterios de la fase 3.

## Impact

Cambian `genoma.py` (una primitiva y cinco sensores nuevos), `simulacion.py`, `poblacion.py`, `config.py` y `persistencia.py`. Se agregan `experiments/configs/coordinacion.toml` y `experiments/fase3/`. Al cambiar la forma del genoma, las corridas de fases anteriores no se reproducen bit a bit con este código: sus resultados se reproducen en el commit `8099dd8`.
