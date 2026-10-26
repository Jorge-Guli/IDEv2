# simbio: de la autonomía individual a la organización colectiva

Experimento de vida artificial. Organismos simples, que empiezan casi como una bacteria (LUCA), se adaptan para sobrevivir en un mundo de recursos limitados. La pregunta es si, evolución tras evolución, asociándose entre sí (fusionándose en organismos más complejos o coordinándose en sociedades), pueden construir niveles crecientes de organización hasta que emerja algo reconocible como inteligencia.

Las acciones que tiene y usa cada organismo salen de su genoma: genes-regla que conectan lo que percibe (solo localmente) con acciones primitivas de una física fija. No hay modelos preentrenados dentro de los organismos. Toda afirmación se compara con un control y con varias semillas, y las corridas son deterministas.

## Estado (2026-10-26)

**Fase en curso: 10, peldaños para la memoria.** La memoria evoluciona solo si cada paso hacia ella tiene premio propio. Se está probando una digestión inducible por la memoria y cómo bloquear sus atajos.

### Lo que encontramos hasta ahora
- **La evolución básica funciona.** Los organismos se adaptan y la evolución inventa conductas nuevas (el giro, fase 1).
- **La asociación evoluciona sola cuando protege.** Con un depredador que solo come organismos sueltos y aparece de a poco, 18 de 20 poblaciones terminan viviendo en grupos de parientes (fase 2c). Poder asociarse, por sí solo, no alcanza (fase 2).
- **Los grupos se coordinan si moverse juntos es físicamente posible.** Percibir el rumbo de los socios aumenta los grupos de 3 o más (réplica con 20 semillas, p ≈ 0,002, fases 3c y 3d).
- **No apareció la división del trabajo.** Ni con restricción flagelar, ni con retornos crecientes, ni con energía compartida (fases 4 y 5).
- **La memoria no evoluciona sin peldaños.**
  - Aun en un mundo donde recordar es la única forma de pasar del azar y un módulo de memoria armado a mano gana siempre, la memoria no apareció en ~3000 generaciones (fases 6 a 9), ni siquiera con genes cuya expresión depende de la memoria.
  - El camino existe, pero su primer paso no se premia: lo mismo que mostraron Lenski y colegas en Avida (2003).
- **La evolución encuentra atajos.** Aprender en vida, selección espacial o "recordar" lo que tiene debajo: cada mundo nuevo se verifica primero con competencias.

### Fases
| Fase | Tema | Resultado | Bitácora |
|---|---|---|---|
| 1 | Evolución básica | ✅ Criterios cumplidos; la evolución inventa el giro | [evaluación](docs/bitacora/2026-10-23-fase1-evaluacion.md) |
| 2 | Asociación (unirse, compartir, conjugar) | ✅ No rinde con la física base; transición abrupta si rinde | [evaluación](docs/bitacora/2026-10-23-fase2-evaluacion.md) |
| 2b | Bien público (enzimas) | ✅ Dilema clásico; asociarse no lo resuelve | [evaluación](docs/bitacora/2026-10-23-fase2b-evaluacion.md) |
| 2c | Depredación limitada por tamaño | ✅ **La asociación evoluciona sola** (18/20) | [evaluación](docs/bitacora/2026-10-24-fase2c-evaluacion.md) |
| 3–3d | Coordinación del grupo | ✅ Con movimiento por fuerza, percibir a los socios agranda los grupos | [3c](docs/bitacora/2026-10-24-fase3c-replica-evaluacion.md), [3d](docs/bitacora/2026-10-24-fase3d-evaluacion.md) |
| 4a–4c | Restricción flagelar | ✅ Más grupos, sin división del trabajo | [4c](docs/bitacora/2026-10-25-fase4c-evaluacion.md) |
| 5 | Retornos crecientes, energía compartida | ⏸ Sin división del trabajo | [exploración](docs/bitacora/2026-10-25-fase5-exploracion.md) |
| 6 | Memoria interna | ✅ Nunca se usa (una estrategia reactiva alcanza) | [evaluación](docs/bitacora/2026-10-25-fase6-evaluacion.md) |
| 7–8 | Mundo con estaciones ocultas y pista | ✅ Atajos; la memoria no evoluciona aunque sea esencial | [7](docs/bitacora/2026-10-26-fase7-evaluacion.md), [8](docs/bitacora/2026-10-26-fase8-evaluacion.md) |
| 9 | Genes condicionados a la memoria | ✅ La memoria sigue sin evolucionar; falta el primer peldaño | [evaluación](docs/bitacora/2026-10-26-fase9-evaluacion.md) |
| 10 | Peldaños para la memoria | ▶ En curso | [hoja de ruta](docs/02-hoja-de-ruta.md) |

Detalle, decisiones y próximos pasos: **[hoja de ruta viva](docs/02-hoja-de-ruta.md)** y **[síntesis](docs/03-sintesis.md)**.

## Documentos
- Hipótesis y objetivo: [`docs/00-hipotesis-fundacional.md`](docs/00-hipotesis-fundacional.md)
- Metodología: [`docs/01-metodologia.md`](docs/01-metodologia.md)
- Hoja de ruta viva: [`docs/02-hoja-de-ruta.md`](docs/02-hoja-de-ruta.md)
- Síntesis de resultados: [`docs/03-sintesis.md`](docs/03-sintesis.md)
- Visión a largo plazo y salvaguardas: [`docs/04-vision.md`](docs/04-vision.md)
- Estado del arte (Avida, Symbulation, MABE, JaxLife): [`docs/05-estado-del-arte.md`](docs/05-estado-del-arte.md)
- Modelo vigente (protocolo ODD): [`docs/odd/modelo.md`](docs/odd/modelo.md)
- Bitácora de experimentos: [`docs/bitacora/`](docs/bitacora/)
- Especificaciones por fase (OpenSpec): [`openspec/`](openspec/)

## Uso

```bash
pip install -e ".[dev]"
python -m pytest -q          # 155 pasan; 3 se omiten sin GPU NVIDIA con CuPy

# una corrida (genera métricas, población, linaje, imágenes)
python -m simbio correr experiments/configs/base.toml --salida runs/demo --semilla 1 --pasos 20000

# evolucionados contra LUCA
python -m simbio competir luca runs/demo/poblacion.npz experiments/configs/base.toml --pasos 3000 --set herencia.mutacion=false

# evaluación de una fase (cada script documenta sus condiciones y las reglas prerregistradas)
python experiments/fase9/evaluar.py --salida runs/fase9 --pasos 300000 --semillas 8 --procesos 8
```

Cualquier parámetro se puede cambiar con `--set seccion.clave=valor` (ver `src/simbio/config.py`). Los scripts de cada fase están en `experiments/<fase>/`.

**CPU o GPU:** se detecta automáticamente. Con una GPU NVIDIA y CuPy instalado se usa la GPU; si no, la CPU. Ver [`docs/dispositivos.md`](docs/dispositivos.md) y `python -m simbio dispositivo`.
