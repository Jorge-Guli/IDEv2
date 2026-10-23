# Proposal

## Why

La fase 2 mostró que poder asociarse no alcanza: en la física actual el grupo no obtiene nada que el individuo no pueda conseguir, y la selección purga la asociación. La hipótesis pregunta **bajo qué condiciones** surge. Esta fase introduce la condición mejor documentada en la biología: un **bien público**. Las levaduras que digieren sacarosa liberan una enzima al medio, y el alimento resultante queda disponible para cualquiera cerca, incluidos los que no la fabrican.

## What Changes

- **Recurso complejo**: un campo nuevo, abundante y en parches propios, que ningún organismo puede comer directamente.
- **Secretar**: una primitiva nueva y costosa que libera enzima en la propia celda.
- **Enzima**: se difunde a las celdas vecinas y se degrada con el tiempo.
- **Digestión**: la enzima convierte el recurso complejo en **alimento libre**, que también se difunde y se degrada, y que cualquier organismo puede comer junto con el recurso simple.
- Sensor nuevo: recurso complejo en la propia celda. Los sensores de alimento pasan a medir todo lo comestible (simple más libre).
- Secretar no se refuerza por aprendizaje: su beneficio es demorado y compartido.
- Todo se activa con `bien_publico.activo` (desactivado por defecto: las fases 1 y 2 no cambian).
- Controles: secreción inerte (cuesta pero no produce enzima), asociación desactivada o inerte.
- Métricas: secretores, uso de secretar, campos totales y agrupación de secretores contra no secretores.

## Capabilities

### New Capabilities
- `bien-publico`: recurso complejo, enzima, digestión, alimento libre y la primitiva secretar.

### Modified Capabilities
- `organismo`: se agregan la primitiva secretar y el sensor de recurso complejo; los sensores de alimento incluyen el alimento libre.
- `aprendizaje`: secretar no se refuerza.
- `experimentacion`: la configuración del bien público, sus controles y los criterios de la fase 2b.

## Impact

Cambian `src/simbio/` (entorno, genoma, simulación, configuración y métricas) y se agregan `experiments/fase2b/` y `experiments/configs/bien_publico.toml`. **BREAKING** para las poblaciones `.npz` anteriores, porque cambia la cantidad de sensores. Con `bien_publico.activo = false`, la dinámica es la de la fase 2 con un sensor y una primitiva que no se usan.
