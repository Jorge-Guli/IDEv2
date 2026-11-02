# Tasks

## 1. Física
- [ ] 1.1 `MetabolismoCfg` (activo, piso = 0,1, inercia = 0,05) y campo `actividad` de la población (1 al nacer LUCA y al cargar lo viejo)
- [ ] 1.2 Cobro basal según la actividad y actualización tras decidir; herencia en la división suelta y en la unida
- [ ] 1.3 Métricas `actividad_media`, `frac_letargo` y `frac_nacen_quietos`
- [ ] 1.4 Tests (reposo prolongado, apagado sin cambios, herencia, carga de lo viejo); suite completa y huellas iguales

## 2. Experimento
- [ ] 2.1 `experiments/fase15/serie.py`: arma la serie (docker × pc) desde `datos/equipo/registro_*`, con las variantes real, quieta y barajada
- [ ] 2.2 `experiments/fase15/experimento.py` (condiciones A–D, 6 semillas, 1 000 000 pasos) y `evaluar.py` con C1–C3
- [ ] 2.3 Esperar ≥ 3 días de registro y ≥ 3 caídas por debajo de 0,2; prerregistro en `docs/bitacora/`
- [ ] 2.4 Correr en Docker, evaluar, registrar
- [ ] 2.5 Revisión con `revisor-cientifico`

## 3. Cierre
- [ ] 3.1 Si C1 y C2 se cumplen, proponer al autor pasar el universo natural a la física nueva (reinicio desde LUCA)
- [ ] 3.2 ODD, hoja de ruta, traspaso; archivar
