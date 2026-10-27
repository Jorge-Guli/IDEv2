# IDE: Inteligencia Distribuida Emergente

*De la autonomía individual a la organización colectiva.* El simulador se llama `simbio`.

Experimento de vida artificial. Organismos simples, que empiezan casi como una bacteria, se adaptan para sobrevivir en un mundo de recursos limitados. La pregunta es si, evolución tras evolución, asociándose entre sí (fusionándose en organismos más complejos o coordinándose en sociedades), pueden construir niveles crecientes de organización hasta que emerja algo reconocible como inteligencia.

Todas las poblaciones parten de **LUCA** (*Last Universal Common Ancestor*, "último antepasado común universal"), el nombre que la biología da al ancestro de toda la vida actual. Aquí es el genoma inicial mínimo: cuatro genes escritos a mano: comer si hay recurso, avanzar si no hay, dar una voltereta al azar o si está bloqueado, y dividirse con energía alta. Todo lo demás lo agrega la evolución.

Las acciones que tiene y usa cada organismo salen de su genoma: genes-regla que conectan lo que percibe (solo localmente) con acciones primitivas de una física fija. No hay modelos preentrenados dentro de los organismos. Toda afirmación se compara con un control y con varias semillas, y las corridas son deterministas.

## Estado (2026-10-26)

**Próxima fase: 12, universo vivo.** Un universo que corre sin parar, alimentado con datos reales, con una interfaz para estimularlo, organismos que se comen entre sí y varios universos conectados ([diseño](docs/06-universo-vivo.md)).

### Lo que encontramos hasta ahora
- **La evolución básica funciona.** Los organismos se adaptan y la evolución inventa conductas nuevas (el giro, fase 1).
- **La asociación evoluciona sola cuando protege.** Con un depredador que solo come organismos sueltos y aparece de a poco, 18 de 20 poblaciones terminan viviendo en grupos de parientes (fase 2c). Poder asociarse, por sí solo, no alcanza (fase 2).
- **Los grupos se coordinan si moverse juntos es físicamente posible.** Percibir el rumbo de los socios aumenta los grupos de 3 o más (réplica con 20 semillas, p ≈ 0,002, fases 3c y 3d).
- **No apareció la división del trabajo.** Ni con restricción flagelar, ni con retornos crecientes, ni con energía compartida (fases 4 y 5).
- **La memoria se sostiene cuando su primer peldaño se premia.** Con una digestión que se prepara según lo recordado, un gen de memoria sembrado se retiene miles de generaciones y coincide con la estación en el 96–99,6 % de los organismos (fases 10 y 11). No evolucionó desde LUCA y todavía no se usa para decidir qué comer.
- **En un mundo fijo, la evolución apaga su propia capacidad de innovar.** La tasa de mutación cae de 0,02 a ~0,0006. Por eso el siguiente paso es un universo que no deje de cambiar.
- **Sin peldaños, la memoria no evoluciona.**
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
| 10 | Peldaños para la memoria | ✅ Memoria sembrada **sostenida por selección** (6/8 contra 0/8 sin peldaño); no se usa para decidir | [evaluación](docs/bitacora/2026-10-26-fase10-evaluacion.md) |
| 11 | Modulación por el estado interno | ✅ La memoria no se recluta; la tasa de mutación había colapsado | [evaluación](docs/bitacora/2026-10-26-fase11-evaluacion.md) |
| 12 | Universo vivo | ▶ Siguiente | [diseño](docs/06-universo-vivo.md) |

Detalle, decisiones y próximos pasos: **[hoja de ruta viva](docs/02-hoja-de-ruta.md)** y **[síntesis](docs/03-sintesis.md)**.

## Documentos
- Hipótesis y objetivo: [`docs/00-hipotesis-fundacional.md`](docs/00-hipotesis-fundacional.md)
- Metodología: [`docs/01-metodologia.md`](docs/01-metodologia.md)
- Hoja de ruta viva: [`docs/02-hoja-de-ruta.md`](docs/02-hoja-de-ruta.md)
- Síntesis de resultados: [`docs/03-sintesis.md`](docs/03-sintesis.md)
- Visión a largo plazo y salvaguardas: [`docs/04-vision.md`](docs/04-vision.md)
- Estado del arte (Avida, Symbulation, MABE, JaxLife): [`docs/05-estado-del-arte.md`](docs/05-estado-del-arte.md)
- Universo vivo (evolución constante, estimulada por la realidad): [`docs/06-universo-vivo.md`](docs/06-universo-vivo.md)
- Traspaso (estado actual y próximos pasos, para retomar el trabajo): [`docs/07-traspaso.md`](docs/07-traspaso.md)
- Modelo vigente (protocolo ODD): [`docs/odd/modelo.md`](docs/odd/modelo.md)
- Bitácora de experimentos: [`docs/bitacora/`](docs/bitacora/)
- Especificaciones por fase (OpenSpec): [`openspec/`](openspec/)

## Uso

```bash
pip install -e ".[dev]"
python -m pytest -q          # 160 pasan; 3 se omiten sin GPU NVIDIA con CuPy

# una corrida (genera métricas, población, linaje, imágenes)
python -m simbio correr experiments/configs/base.toml --salida runs/demo --semilla 1 --pasos 20000

# evolucionados contra LUCA
python -m simbio competir luca runs/demo/poblacion.npz experiments/configs/base.toml --pasos 3000 --set herencia.mutacion=false

# evaluación de una fase (cada script documenta sus condiciones y las reglas prerregistradas)
python experiments/fase9/evaluar.py --salida runs/fase9 --pasos 300000 --semillas 8 --procesos 8
```

**Universo vivo (fase 12):** un universo que corre sin plazo y retoma tras un corte.

```bash
python -m simbio vivir experiments/configs/vivo.toml --salida runs/vivo/universo   # Ctrl+C guarda y sale
python -m simbio mirar runs/vivo/universo                                         # resumen, sin detenerlo
docker compose up -d --build                                                      # lo mismo en Docker, sin red
```

Cualquier parámetro se puede cambiar con `--set seccion.clave=valor` (ver `src/simbio/config.py`). Los scripts de cada fase están en `experiments/<fase>/`.

**CPU o GPU:** se detecta automáticamente. Con una GPU NVIDIA y CuPy instalado se usa la GPU; si no, la CPU. Ver [`docs/dispositivos.md`](docs/dispositivos.md) y `python -m simbio dispositivo`.
