# Tasks

## 1. Andamiaje

- [x] 1.1 Crear `pyproject.toml`, paquete `src/simbio/` y `tests/`; verificar que `pip install -e .` y `pytest` corren

## 2. Entorno

- [x] 2.1 Implementar `config.py` (dataclasses + carga TOML con valores por defecto) y verificar con test de carga/override
- [x] 2.2 Implementar `entorno.py` (parches reproducibles, regeneración acotada, estacionalidad, cambio abrupto) y verificar con tests de los escenarios de `entorno`

## 3. Genoma y población

- [x] 3.1 Implementar `genoma.py` (LUCA, expresión de primitivas, operadores de mutación, mutagénesis por estrés) y verificar con tests de los escenarios de `herencia`
- [x] 3.2 Implementar `poblacion.py` (estructura de arreglos, alta/baja, compactación, linaje) y verificar con tests unitarios

## 4. Simulación

- [x] 4.1 Implementar `simulacion.py` (sensores, decisión, física, conflictos, división, muerte, estrés) y verificar con tests de los escenarios de `organismo`
- [x] 4.2 Implementar aprendizaje plástico y verificar con tests de los escenarios de `aprendizaje`
- [x] 4.3 Verificar reproducibilidad (misma semilla → métricas idénticas) con test

## 5. Experimentación

- [x] 5.1 Implementar `metricas.py`, `persistencia.py`, `visual.py` y `cli.py`; verificar que `python -m simbio run` produce config, CSV, población y gráficos
- [x] 5.2 Implementar competencia entre poblaciones y verificar con test (población contra sí misma ≈ 50 %)
- [x] 5.3 Escribir `experiments/fase1/evaluar.py` (C1–C4) y experimentos exploratorios (estrés, aprendizaje); verificar que corren a escala reducida

## 6. Integración y registro

- [x] 6.1 Ejecutar la evaluación de la fase, registrar resultados en `docs/bitacora/` y actualizar `docs/odd/modelo.md`
- [x] 6.2 Revisión independiente de validez científica y de código; aplicar correcciones

## Workflow follow-up

- Archivar el cambio con `openspec archive fase-1-evolucion-basica` cuando los criterios C1–C4 estén aprobados.
