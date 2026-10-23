# Proposal

## Why

La hipótesis fundacional (`docs/00-hipotesis-fundacional.md`) requiere, antes de estudiar asociación, una base que funcione: organismos simples tipo bacteria que vivan, se reproduzcan, hereden, muten y se adapten en un entorno con recursos limitados. Sin esa base validada, cualquier fenómeno colectivo posterior sería imposible de interpretar. Esta fase es el control de todo el experimento.

## What Changes

- Un mundo 2D toroidal con recursos que se regeneran, distribuidos en parches y opcionalmente estacionales o con cambios abruptos.
- Organismos con energía, sensores locales y un **genoma de genes-regla**: cada gen conecta lo que el organismo percibe con una acción primitiva. Las acciones disponibles para cada organismo salen de su genoma; la física del mundo solo define qué primitivas existen y cuánto cuestan.
- Reproducción por división con herencia y mutación (puntual, duplicación, eliminación, gen nuevo, cambio de acción), incluyendo mutación de los propios rasgos de mutación y aprendizaje.
- **Mutagénesis por estrés** (análoga a la respuesta SOS): organismos con hambre sostenida producen descendencia con más variación.
- **Aprendizaje durante la vida**: ajuste no heredable de los genes según el resultado energético de las acciones.
- Infraestructura de experimentación: configuración en archivo, semillas reproducibles, métricas, guardado/carga de poblaciones, competencia entre poblaciones, imágenes y gráficos.
- Criterios de éxito verificables de la fase (persistencia, adaptación, reproducibilidad, rendimiento) y experimentos exploratorios (efecto del estrés y del aprendizaje).

## Capabilities

### New Capabilities
- `entorno`: mundo espacial, recursos, regeneración, heterogeneidad espacial y temporal.
- `organismo`: energía, percepción, expresión de acciones a partir del genoma, física de las acciones, división y muerte.
- `herencia`: estructura del genoma, operadores de mutación y mutagénesis por estrés.
- `aprendizaje`: plasticidad no heredable durante la vida del organismo.
- `experimentacion`: configuración, reproducibilidad, métricas, persistencia de poblaciones, competencia e intervenciones de control.

### Modified Capabilities

## Impact

Proyecto nuevo: paquete Python `simbio` (NumPy, Matplotlib), tests con `pytest`, configuraciones en `experiments/`, resultados en `docs/bitacora/`. Sin dependencias externas de red ni modelos preentrenados.
