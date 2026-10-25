# simbio: de la autonomía individual a la organización colectiva

Experimento de vida artificial. Organismos simples, que empiezan casi como una bacteria, se adaptan para sobrevivir en un mundo de recursos limitados. La pregunta es si, evolución tras evolución, asociándose entre sí (fusionándose en organismos más complejos o coordinándose en sociedades), pueden construir niveles crecientes de organización hasta que emerja algo reconocible como inteligencia.

- Hipótesis y objetivo: [`docs/00-hipotesis-fundacional.md`](docs/00-hipotesis-fundacional.md)
- Metodología: [`docs/01-metodologia.md`](docs/01-metodologia.md)
- **Hoja de ruta viva** (fases en orden, estado y decisiones): [`docs/02-hoja-de-ruta.md`](docs/02-hoja-de-ruta.md)
- Modelo vigente (protocolo ODD): [`docs/odd/modelo.md`](docs/odd/modelo.md)
- Bitácora de experimentos: [`docs/bitacora/`](docs/bitacora/)
- Especificaciones por fase (OpenSpec): [`openspec/`](openspec/)

## Estado

**Fase 1 — evolución básica: cerrada (2026-10-23).** Organismos con un genoma de genes-regla: cada gen conecta lo que el organismo percibe con una acción primitiva, de modo que las acciones disponibles salen del ADN. Tienen metabolismo, división, mutación (puntual, duplicación, eliminación, gen nuevo), mutagénesis por estrés y aprendizaje durante la vida. Se cumplieron los cuatro criterios de éxito, y la evolución "inventó" el giro, una conducta que LUCA no tenía ([bitácora](docs/bitacora/2026-10-23-fase1-evaluacion.md)).

**Fase 2 — asociación: cerrada (2026-10-23).** Los organismos pueden unirse, soltarse, compartir energía, dividirse quedando unidos y pasarse genes. Con la física actual, la asociación **no rinde** y no despega. En el control positivo, donde rinde, ocurre una transición abrupta: de casi 0 % a más del 98 % de enlazados en ~800 pasos, con un tapete de más de 10 000 organismos y aprovechados ([bitácora](docs/bitacora/2026-10-23-fase2-evaluacion.md)).

**Fase 2b — bien público: cerrada (2026-10-23).** Con una enzima que digiere un recurso complejo hay dilema del bien público: con beneficio privado la secreción llega al ~100 %; con beneficio público no arranca. Asociarse no lo resuelve, porque la dispersión local ya deja a los parientes al lado ([bitácora](docs/bitacora/2026-10-23-fase2b-evaluacion.md)).

**Fase 2c — depredación limitada por tamaño: cerrada (2026-10-24).** Un depredador que solo puede comer organismos sueltos y que aparece de a poco hace que **la asociación evolucione sola desde LUCA**: 18 de 20 semillas terminan con la mayoría de la población en grupos, sobre todo pares de parientes que se dividen quedando unidos. Con depredador uniforme o con protección al azar no pasa. Con aparición brusca, la prueba prerregistrada falló ([bitácora](docs/bitacora/2026-10-24-fase2c-evaluacion.md)).

**Fase 3 — coordinación del grupo: cerrada (2026-10-24).** Los grupos no pasan de pares porque los de 3 o más no logran moverse juntos. Si los organismos perciben el rumbo de sus socios, la alineación evoluciona, pero los grupos no crecen; un canal de señales no se inventa. Cuando moverse en grupo es fácil, los grupos crecen ([bitácora](docs/bitacora/2026-10-24-fase3-evaluacion.md)).

**Fases 3b y 3c — invasión y movimiento por fuerza: cerradas (2026-10-24).** Con la regla de movimiento anterior, coordinarse casi no rinde (3b). Con una regla en la que el grupo se mueve por la suma de las fuerzas de sus miembros (α = 0,5), percibir a los socios aumenta mucho la fracción de la población en grupos de 3 o más (réplica con 20 semillas nuevas, p ≈ 0,002) ([bitácora](docs/bitacora/2026-10-24-fase3c-replica-evaluacion.md)).

**Fase 3d — ablación y sensibilidad: hecha (2026-10-24).** La percepción del rumbo de los socios actúa en vida: sin ella, las mismas poblaciones forman menos grupos y sostienen menos organismos. La alineación es heredada, el efecto vale para varios valores del arrastre y las señales arbitrarias nunca se usaron ([bitácora](docs/bitacora/2026-10-24-fase3d-evaluacion.md)).

**Fase 4a — restricción flagelar: cerrada (2026-10-25).** Si dividirse impide moverse un tiempo, como en *Volvox*, la evolución deja grupos más grandes y miembros que no se reproducen aunque podrían. Es un cambio heredable, que se ve en un jardín común. Todavía no es división del trabajo: los no reproductores no hacen otra cosa útil ([bitácora](docs/bitacora/2026-10-25-fase4b-evaluacion.md)).

**Fase 4c — réplica y controles: hecha (2026-10-25).** Con 20 poblaciones, el "sesgo reproductivo" visto en una sola resultó no generalizarse: lo que se selecciona es dividirse menos. La restricción favorece los grupos (replicado con semillas nuevas), pero no aparece la división del trabajo ([bitácora](docs/bitacora/2026-10-25-fase4c-evaluacion.md)).

**Próximo: fase 5** — retornos crecientes a la especialización y energía compartida dentro del grupo.

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
