# Tasks

## 1. Genoma y configuración

- [x] 1.1 Agregar `AsociacionCfg`, primitivas, sensores y etiqueta en `config.py` y `genoma.py`; verificar con tests de herencia (etiqueta heredada, primitivas permitidas según interruptores)

## 2. Mecánica de asociación

- [x] 2.1 Implementar enlaces (validación, unirse, soltarse, costo) y verificar con tests de los escenarios de `asociacion`
- [x] 2.2 Implementar compartir, dividirse unido y conjugación; verificar con tests de reparto, hijo enlazado y transferencia
- [x] 2.3 Implementar sensores sociales y exclusiones de aprendizaje; verificar con tests
- [x] 2.4 Verificar invariantes (simetría, vecindad, sin enlaces a muertos) en una corrida con asociación forzada

## 3. Medición y visualización

- [x] 3.1 Métricas de organización (grupos, compartido, aprovechados, parentesco) y enlaces en la imagen del mundo; verificar con test de grupo A–B–C

## 4. Experimentos

- [x] 4.1 `experiments/fase2/evaluar.py` con criterios C1–C4 y condiciones exploratorias; verificar a escala reducida
- [ ] 4.2 Ejecutar la evaluación, registrar en `docs/bitacora/` y actualizar el ODD
- [x] 4.3 Revisión con `revisor-cientifico` y correcciones

## Workflow follow-up

- Archivar `fase-2-asociacion` cuando C1–C4 estén aprobados y la revisión esté resuelta.
