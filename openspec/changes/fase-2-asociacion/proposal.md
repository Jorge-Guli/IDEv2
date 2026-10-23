# Proposal

## Why

La hipótesis del proyecto es que la complejidad surge cuando los organismos se asocian. La fase 1 validó una base de organismos que evolucionan de forma individual. Ahora hay que darles la **posibilidad física** de asociarse y estudiar si la evolución la aprovecha, bajo qué condiciones y con qué conflictos (aprovechados, inestabilidad), sin imponer que lo hagan.

## What Changes

- Nuevas primitivas físicas, disponibles solo para los organismos cuyo genoma las exprese:
  - **unirse**: crea un enlace con el organismo de enfrente.
  - **soltarse**: rompe todos los enlaces propios.
  - **compartir**: cede una fracción de la propia energía a los enlazados, con pérdidas.
  - **dividirse unido**: el hijo nace enlazado al progenitor. Es el camino clonal a la multicelularidad.
  - **conjugar**: copia un gen propio en un enlazado. Es la transferencia horizontal de genes.
- Los enlaces son físicos: solo existen entre vecinos y se rompen si los organismos dejan de estar en la misma posición relativa. Si dos enlazados se mueven en la misma dirección, el enlace se mantiene, así que el movimiento en grupo es posible pero tiene que surgir por coordinación.
- Mantener un enlace cuesta energía en cada paso.
- Una **etiqueta heredable** sin función propia, que otros organismos pueden percibir. Permite que evolucione el reconocimiento de parientes, pero no lo impone.
- Nuevos sensores locales: cantidad de enlaces, energía media de los enlazados, si el de enfrente es un enlazado y la similitud de etiqueta con el de enfrente.
- LUCA no cambia: **no tiene ningún gen de asociación**. Si la asociación aparece, tiene que hacerlo por mutación.
- Métricas de organización: fracción de organismos enlazados, tamaño de los grupos (componentes conexas), energía compartida, parentesco dentro de los enlaces contra el azar y balance de dar y recibir (aprovechados).
- Controles: asociación desactivada, y "compartir sin beneficio" (eficiencia 0).

## Capabilities

### New Capabilities
- `asociacion`: enlaces físicos entre organismos, compartir energía, división unida, conjugación, etiqueta y métricas de organización.

### Modified Capabilities
- `organismo`: el conjunto de primitivas y de sensores se amplía.
- `herencia`: el genoma incluye la etiqueta heredable.
- `aprendizaje`: las acciones sin retorno energético propio (compartir, conjugar, dividirse unido) se excluyen del refuerzo, como dividirse.
- `experimentacion`: interruptores de asociación y conjugación, el control de compartir sin beneficio, métricas de grupo y criterios de la fase 2.

## Impact

Cambia `src/simbio/` (genoma, simulación, configuración, métricas y visualización): las poblaciones guardadas en la fase 1 no son compatibles, porque cambia la cantidad de sensores. **BREAKING** para archivos `.npz` de la fase 1. Se agregan `experiments/fase2/` y una configuración nueva.
