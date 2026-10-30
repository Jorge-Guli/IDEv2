# Metodología del proyecto

## 1. Marco de trabajo: qué usamos y por qué

Se evaluaron dos marcos para guiar el desarrollo asistido por agentes:

| | Goal-Driven (GDD) | OpenSpec |
|---|---|---|
| Qué es | Un prompt: un agente maestro relanza subagentes en bucle hasta que se cumplen criterios verificables. | Un CLI + flujo de trabajo: cada cambio es una carpeta con `proposal`, `specs`, `design` y `tasks`; al archivarlo, las specs vivas se actualizan. |
| Ideal para | Problemas largos con una meta **objetivamente verificable** (p. ej. "pasar toda la suite de tests de un compilador"). | Proyectos que avanzan por cambios incrementales donde importa dejar registradas las decisiones. |
| Encaje con este proyecto | Parcial. Nuestra meta final (que emerja inteligencia) **no es verificable de antemano**: es una pregunta de investigación, no un test que pasar. Un bucle "seguir hasta cumplir" sobre una meta abierta no termina o se autoengaña. Además consume muchos tokens. | Alto. El proyecto avanza por **fases** (evolución básica → asociación → colectivo como individuo → …) y cada fase es un cambio con propósito, decisiones y criterios propios. Las specs acumuladas describen qué "física" tiene el mundo en cada momento. |

**Decisión:** usamos **OpenSpec** como columna vertebral, y tomamos de GDD la única idea que sí encaja: **cada fase tiene criterios de éxito verificables** (tests y experimentos con umbrales numéricos) que el orquestador comprueba antes de dar la fase por cerrada. No usamos el bucle infinito de GDD.

Complementamos con el **protocolo ODD** (*Overview, Design concepts, Details*; Grimm et al. 2006, 2020), el estándar científico para describir modelos basados en agentes. El documento [`odd/modelo.md`](odd/modelo.md) describe el modelo vigente de forma que otra persona pueda reproducirlo; se actualiza al archivar cada fase.

### Cómo se trabaja una fase

1. `openspec new change fase-N-...` → `proposal.md` (por qué), `specs/` (qué debe cumplir el mundo), `design.md` (cómo), `tasks.md` (pasos con verificación).
2. Implementación con tests (cada requisito tiene escenarios que se traducen en tests).
3. Experimentos de la fase con **criterios de éxito numéricos**; resultados en [`bitacora/`](bitacora/).
4. Revisión independiente (subagente `revisor-cientifico`) de validez: controles, sesgos, si lo observado realmente "emergió" o venía programado.
5. `openspec archive` → las specs pasan a `openspec/specs/` y se actualiza el ODD.

## 2. Principios de diseño

1. **La física es fija, la biología no.** El mundo define *qué es posible* (moverse cuesta energía, comer recursos la aporta, dividirse la reparte), como la química define qué reacciones pueden ocurrir. Pero **qué acciones tiene cada organismo, cuándo las usa y cómo las combina sale de su ADN**, y puede ganarse, perderse, duplicarse o modificarse por mutación. Un organismo sin el gen de división no se reproduce; uno sin gen de movimiento queda quieto.
2. **Empezar como una bacteria.** El primer organismo ("LUCA") tiene un genoma mínimo diseñado a mano, con pocas conductas básicas. El origen de la vida queda fuera del alcance.
3. **Tres escalas de adaptación**, como en la biología:
   - *Aprendizaje* (durante la vida): el organismo ajusta la intensidad de sus genes según le va bien o mal. No se hereda.
   - *Respuesta al estrés* (al límite de la supervivencia): un organismo hambriento aumenta su tasa de mutación al reproducirse, como la respuesta SOS de las bacterias. Así "evoluciona cuando está al límite": la variación aumenta justo cuando lo actual no alcanza.
   - *Evolución* (entre generaciones): mutación + selección natural.
   La capacidad de aprender y la sensibilidad al estrés **también están en el genoma**: la evolución decide si le convienen.
4. **Nada de inteligencia importada.** No se usan LLMs ni modelos preentrenados dentro de los organismos.
5. **Toda afirmación se contrasta con un control.** Cada resultado se compara con la misma simulación sin el mecanismo que se pretende estudiar.
6. **Reproducibilidad.** Misma configuración + misma semilla = mismo resultado.
7. **El universo no se acomoda al organismo; el organismo se adapta al universo** (pedido del autor, 2026-10-30). Las células de una persona viven en un universo que no se ajusta a su conveniencia: se adaptan, y si no, lo hacen las generaciones siguientes. Por eso:
   - **El universo solo se modifica para que sea más fiel a la realidad del autor**, nunca para facilitar un resultado buscado (que aparezca la memoria, que no se extingan, que acierten más). Una extinción es un dato, no algo que corregir retocando costos.
   - **Cuanta más conexión segura con el mundo real, mejor:** clima real, cambio climático, fenómenos como El Niño y La Niña, luz, y las acciones del propio autor. Entran como parte de un ambiente indiferente, no como premio.
   - **Hacia la física real:** a largo plazo, moverse en un espacio continuo de tres dimensiones con gravedad, en lugar de una grilla plana.
   - **Lo que sí se amplía es qué pueden llegar a ser los organismos** (qué permite su genoma: memoria, señales, asociarse), no lo que el mundo les regala.
   - Elegir un universo rico (con regularidades, cambios, escasez y otros seres) no viola esta regla, como no la viola que la Tierra tenga estaciones. La viola cambiarlo después según les vaya.
   - Los ajustes hechos en las fases 7–12 (castigo, rampa de toxicidad) fueron acomodar el mundo y quedan registrados como tales.

## 3. Hoja de ruta

> El camino detallado, con el estado actual, los criterios para cambiar de rumbo y el registro de decisiones, está en [`02-hoja-de-ruta.md`](02-hoja-de-ruta.md). Esta tabla es el resumen.

| Fase | Ingrediente nuevo | Pregunta |
|---|---|---|
| 1 | Organismos tipo bacteria: genoma de genes-regla, metabolismo, división, mutación, mutagénesis por estrés, aprendizaje | ¿La población persiste y se adapta? ¿Ayudan el estrés y el aprendizaje? |
| 2 | Primitivas de **asociación**: unirse a un vecino, compartir energía, transferencia horizontal de genes | ¿Bajo qué condiciones evoluciona la asociación? ¿Aparecen aprovechados? |
| 2b | **Condiciones ecológicas** que hagan rendir al grupo (recurso complejo, depredación, dispersión), como física del mundo | ¿Qué condiciones vuelven ventajosa la asociación? (la fase 2 mostró que poder asociarse no alcanza) |
| 3 | **El colectivo como individuo**: reproducción del grupo (fragmentación / brote) | ¿Aparecen especialización y dependencia? |
| 4 | Señales, memoria interna, comunicación | ¿Se propaga la información útil? ¿Memoria distribuida? |
| 5 | Asociación entre colectivos | ¿Se apilan niveles o el sistema se estanca? |
| 6 | Problemas del entorno que exijan coordinación y anticipación | ¿Los colectivos resuelven lo que los individuos no? |
| — | Mundo 3D (si alguna fase lo justifica) | ¿La geometría (superficie/volumen, interior) habilita organizaciones nuevas? |

## 4. Herramientas

- Python 3.11+ con NumPy (vectorizado) y Matplotlib. GPU NVIDIA opcional mediante CuPy, detectada automáticamente (`docs/dispositivos.md`).
- `pytest` para tests; `openspec validate` para los artefactos de cada fase.
- Corridas grandes: se preparan como scripts con configuración en archivo para ejecutarlas en una máquina local con más recursos.
