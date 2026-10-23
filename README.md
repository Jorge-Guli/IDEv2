# simbio: de la autonomía individual a la organización colectiva

Experimento de vida artificial. Organismos simples, que empiezan casi como una bacteria, se adaptan para sobrevivir en un mundo de recursos limitados. La pregunta es si, evolución tras evolución, asociándose entre sí (fusionándose en organismos más complejos o coordinándose en sociedades), pueden construir niveles crecientes de organización hasta que emerja algo reconocible como inteligencia.

- Hipótesis y objetivo: [`docs/00-hipotesis-fundacional.md`](docs/00-hipotesis-fundacional.md)
- Metodología y hoja de ruta: [`docs/01-metodologia.md`](docs/01-metodologia.md)
- Modelo vigente (protocolo ODD): [`docs/odd/modelo.md`](docs/odd/modelo.md)
- Bitácora de experimentos: [`docs/bitacora/`](docs/bitacora/)
- Especificaciones por fase (OpenSpec): [`openspec/`](openspec/)

## Estado

**Fase 1 — evolución básica: cerrada (2026-10-23).** Organismos con un genoma de genes-regla: cada gen conecta lo que el organismo percibe con una acción primitiva, de modo que las acciones disponibles salen del ADN. Tienen metabolismo, división, mutación (puntual, duplicación, eliminación, gen nuevo), mutagénesis por estrés y aprendizaje durante la vida. Se cumplieron los cuatro criterios de éxito, y la evolución "inventó" el giro, una conducta que LUCA no tenía ([bitácora](docs/bitacora/2026-10-23-fase1-evaluacion.md)).

**Próximo: fase 2 — asociación.**

## Uso

```bash
pip install -e ".[dev]"
python -m pytest -q

# una corrida (genera métricas, población, linaje, imágenes)
python -m simbio correr experiments/configs/base.toml --salida runs/demo --semilla 1 --pasos 20000

# evolucionados contra LUCA
python -m simbio competir luca runs/demo/poblacion.npz experiments/configs/base.toml --pasos 3000 --set herencia.mutacion=false

# evaluación completa de la fase 1 (criterios de éxito + exploratorios)
python experiments/fase1/evaluar.py --salida runs/fase1 --procesos 4

# experimento largo de mutagénesis por estrés (para un equipo con más núcleos)
python experiments/fase1/estres_extendido.py --salida runs/e1 --semillas 20 --pasos 100000 --procesos 8
```

Cualquier parámetro se puede cambiar con `--set seccion.clave=valor` (ver `src/simbio/config.py`).

**CPU o GPU:** se detecta automáticamente. Con una GPU NVIDIA y CuPy instalado se usa la GPU; si no, la CPU. Ver [`docs/dispositivos.md`](docs/dispositivos.md) y `python -m simbio dispositivo`.
