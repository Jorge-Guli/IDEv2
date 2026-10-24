# Proposal

## Why

Las fases 3 y 3b mostraron que el techo de tamaño de los grupos está en la regla de movimiento:
- con el modo "empuje", un grupo se mueve solo si la suma de los empujes alcanza la mitad de su tamaño. Eso exige empujar alineados y en el mismo paso;
- alinearse cuesta acciones (quien gira no come);
- un trío coordinado diseñado a mano casi no gana nada y no invade (3b).

Esa regla fue una decisión de modelo (fase 2b), no una propiedad biológica. Las colonias reales se mueven por la suma de las fuerzas de sus células, más lento cuanto más grandes, sin "votar". La revisión de la fase 3 advirtió que cambiar la física después de un resultado negativo solo es aceptable como **decisión de modelo explícita, con prerregistro y semillas nuevas**, y midiendo por separado cuánto aporta la física y cuánto la información (controles base y barajado).

## What Changes

- **Modo de movimiento "fuerza"** (`asociacion.movimiento = "fuerza"`). Cada empuje es un vector unitario, sin ventaja diagonal. El grupo se desplaza en la dirección más alineada con la suma, con probabilidad (proyección de la suma sobre esa dirección) / tamaño^α (`asociacion.exponente_arrastre`), sin umbral. Las celdas de destino tienen que estar libres, como antes.
- El modo "empuje" no cambia: las huellas de las corridas anteriores son idénticas.

## Capabilities

### Modified Capabilities
- `asociacion`: modo de movimiento por fuerza.
- `experimentacion`: configuración y criterios de la fase 3c.

## Impact

Cambian `simulacion.py` (`_mover_grupos`) y `config.py`. Se agrega `experiments/fase3c/`.
