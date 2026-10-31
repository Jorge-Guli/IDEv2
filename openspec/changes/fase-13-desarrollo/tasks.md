# Tasks

## 1. Peldaños 1 y 2: red regulatoria y señal por contacto
- [x] 1.1 `DesarrolloCfg` (activo, tasa, asimetria, inerte) y campos `R`, `rb`, `v` del genoma; estado `reg`
- [x] 1.2 `Simulacion.regular`, lectura en `decidir`, herencia y división asimétrica, mutación (sin azar nuevo si está apagada)
- [x] 1.3 Compatibilidad de genomas y poblaciones guardados
- [x] 1.4 Tests (`tests/test_desarrollo.py`), entre ellos la inhibición lateral; huellas iguales
- [x] 1.5 Métricas: `con_gen_regulado`, `peso_regulador_medio`, `reg_medio_abs`, dispersión del estado en los grupos y en la población, `corr_reg_rol_max`

## 2. Piloto
- [x] 2.1 Prerregistro (`docs/bitacora/2026-10-30-fase13-red-regulatoria-prerregistro.md`) y `experiments/fase13/piloto.py`
- [x] 2.2 Correr (semillas 1–6, 300 000 pasos), evaluar y registrar: nulo (P1 saturada, P2 sin grupos)
- [x] 2.3 Diagnóstico de los grupos y física del tamaño (`ataque.tamano`), con tests
- [x] 2.4 Piloto del cuerpo (semillas 7–12): C1 se cumple, P2 no
- [x] 2.5 Revisión con `revisor-cientifico`; medidas nuevas (parentesco, canibalismo interno, correlación dentro del cuerpo) y controles (`forma`, `intragrupo`)
- [x] 2.6 Controles del cuerpo (semillas 13–18): S2 y K se cumplen; S1 (curva suave) y P2' no
- [x] 2.7 Fundamentar la forma de la curva del tamaño con datos reales de depredadores unicelulares: se queda r²/(1+r²) (la realidad es aún más empinada)

## 3. Peldaños siguientes (diseño pendiente, uno por vez)
- [ ] 3.1 El cuerpo como unidad que se reproduce (línea germinal, cuello de botella unicelular)
- [ ] 3.2 Reproducción sexual
- [ ] 3.3 Tipos celulares y células mensajeras

## Workflow follow-up
- Actualizar el ODD, la hoja de ruta y el traspaso con cada peldaño; archivar al cerrar la fase.
