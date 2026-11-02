# Primera extinción causada por el equipo (2026-11-02)

## Qué pasó
El universo natural, reiniciado desde LUCA el 2026-11-01 a las 23:45 con los niveles docker y pc, vivió ~9 h y 1,77 millones de pasos, con unos 1 500–1 900 organismos. A las 09:02:47 la PC tuvo una sola muestra con la CPU casi al tope (pc = 0,018; memoria libre 9,6 %). Las muestras de antes y de después eran normales (0,70–0,89). El universo leyó esa muestra en el paso 1 773 000: el recrecimiento de la comida cayó al 1,7 % de lo normal. **En 256 pasos se extinguió toda la población** (1 706 → 0, t = 1 773 256).

## Por qué tan rápido
- La población vive al día: come ~0,66 por organismo y por paso, y su reserva media (31 de energía) alcanza para unas pocas decenas de pasos sin comer. Depende del recrecimiento de cada paso, no de un depósito.
- En casi 1 800 lecturas anteriores el mínimo había sido 0,22: la población nunca había enfrentado un corte así.

Una extinción es un dato. Es la primera muestra de que el equipo afecta al universo de verdad, y de que una perturbación de 10 s alcanza para borrar 9 h de evolución.

## Dos problemas de implementación (no de física), corregidos
1. **Fidelidad del tiempo:** el universo revisaba el equipo cada 1 000 pasos (~20 s). La muestra de 10 s pesó el doble de lo real, y la mitad de las muestras no se sentía. Ahora se revisa cada 100 pasos (`natural.toml`, `equipo.revisar_cada = 100`). Igual, con 10 s reales (~500 pasos) la población también habría muerto: murió en 256.
2. **Bucle tras la extinción:** con `restart: unless-stopped`, Docker relanzaba el universo extinto cada minuto, y cada vez se anotaba otra retoma y otra extinción, un paso por vez (156 veces). Ahora `vivir` no retoma un universo extinto si no se resiembra (`tests/test_continuo.py::test_universo_extinto_no_se_retoma`).

La física no se tocó: el recrecimiento sigue siendo `regeneracion · cpu_libre`.

## Después
- El mundo extinto queda en `runs/vivo/natural_extinto_2026-11-02`.
- Universo nuevo desde LUCA (mismo `natural.toml`, semilla 0) en `runs/vivo/natural`.
- Para la validación pendiente (equipo real contra promedio quieto y contra serie barajada), la tasa de extinción es una medida más: el promedio quieto nunca habría tenido este corte.
