# Proposal

## Why

El 2026-11-02 a las 09:02 la PC del autor pasó 10 s casi al tope (CPU libre 0,018). El recrecimiento de la comida cayó al 1,7 % y en 256 pasos se extinguió un universo de 9 h (`docs/bitacora/2026-11-02-primera-extincion-por-el-equipo.md`). La población vive al día. Además, su física no le deja otra salida:

- estar vivo cuesta siempre lo mismo (`costo_basal`), haga lo que haga el organismo;
- la reserva máxima (100) no alcanza para pasar ~500 pasos de escasez (~250 de energía), ni siquiera con el mejor ahorro posible.

Esa regla no es fiel al mundo físico de LUCA, que es la computadora donde corre. En una PC, un programa en pausa casi no usa CPU, y uno trabajando usa mucha. En la naturaleza pasa lo mismo: el metabolismo de reposo es mucho menor que el activo, y el letargo, la hibernación, las semillas y las esporas lo llevan al extremo. El autor lo aprobó el 2026-11-02: "eso es correcto, pasa en la realidad".

No se regala ninguna semilla, espora ni órgano de letargo (principio 7). Se cambia una sola ley de la física: **el gasto de estar vivo sigue a la actividad reciente.** Cuándo aquietarse, cuándo despertar y si las crías nacen dormidas (una "semilla" que germina cuando el entorno lo permite) queda en manos del genoma.

## What Changes

- **Metabolismo por actividad** (`metabolismo.*`, apagado por defecto). Cada organismo lleva su actividad reciente `a`: un promedio móvil de "hizo algo distinto de descansar", con inercia `metabolismo.inercia` (entrar en letargo lleva tiempo). El costo basal pasa a ser `costo_basal · (piso + (1 − piso) · a)`.
  - El costo por gen no cambia: es la memoria que ocupa el programa, que en una PC se paga aunque esté en pausa.
  - Las acciones siguen costando lo mismo.
- **Herencia de la actividad:** la cría nace con la actividad del progenitor. Una cría de un padre aquietado nace aquietada, y eso es lo que permite una semilla.
- **Experimento prerregistrado** (`experiments/fase15/`), con un diseño 2 × 3:
  - física: actual o metabolismo por actividad;
  - mundo físico: la serie grabada del equipo, el mismo promedio quieto, o la misma serie barajada.

## Capabilities

### Modified Capabilities
- `organismo`: costo basal según la actividad reciente, y herencia de esa actividad.
- `experimentacion`: métricas de letargo y reproducción determinista de la serie grabada del equipo.

## Impact

- **Código:** cambian `config.py` (`MetabolismoCfg`), `poblacion.py` (campo `actividad`), `simulacion.py` (cobro basal, herencia y métricas) y `continuo.py` (nada: la serie se reproduce en el experimento).
- **Compatibilidad:** apagado no consume azar ni cambia ningún número; las huellas quedan iguales. Las poblaciones guardadas se completan con actividad 1 (gasto pleno, como hoy).
- **El universo natural** recién se pasa a la física nueva si el experimento lo justifica y el autor lo aprueba, porque hay que reiniciarlo desde LUCA.
- **Fuera de alcance:** que los muertos de hambre devuelvan comida al suelo. Hoy la energía es lo único que tiene un cuerpo, y el que muere de hambre muere con energía cero: no queda nada que reciclar. Darle masa al cuerpo es otra ley y otra fase. El reciclaje de los vivos ya existe: `atacar`.
