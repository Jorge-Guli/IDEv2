# 2026-10-28 · Fase 12, etapa 5: archipiélago (prerregistro)

## Pregunta
En casi todas las fases, la población termina en un monocultivo: la tasa de mutación colapsa y la innovación se frena. El modelo de islas de la biología evolutiva propone una salida. Varias poblaciones evolucionan por separado y de vez en cuando intercambian unos pocos individuos. Cada isla explora su propio camino, y la migración lleva a las otras lo que una encontró.

¿Eso mejora la adaptación y mantiene viva la variación, frente a las mismas islas aisladas?

## Motor
- `src/simbio/archipielago.py`: islas en anillo. Cada `cada` pasos, `migrantes` organismos de cada isla, sorteados, pasan a la siguiente.
- Todas las islas eligen sus migrantes antes de recibir.
- Los migrantes llegan a celdas libres sorteadas, con su genoma, su energía y su generación, sin enlaces ni memoria interna.
- Generador propio de CPU: es determinista.
- Tests: `tests/test_archipielago.py` (conservación, islas independientes sin migración, determinismo). Las huellas no cambian.

## Piloto (semillas 1–3, 60 000 pasos; exploratorio)
- 3 islas de 74 × 74 (área total ≈ un universo de 128 × 128), 2 migrantes cada 1000 pasos.
- Las islas quedan con 75–150 organismos.
- **Extinciones de islas:** 1 en las aisladas y 0 con migración (rescate).
- No hay diferencias claras: acierto −0,004 y +0,005, y la tasa de mutación algo *menor* con migración (−0,002 en los 2 pares).
- Se corrigió un error del script: una isla extinta cortaba la serie de todas.

## Diseño (fijo antes de correr)
- **Islas:** 3 de 74 × 74, mundo de `vivo.toml` (fase 11), desde LUCA. Semilla de la isla i = semilla · 100 + i.
- **Condiciones:**
  - migracion: 2 migrantes por isla cada 1000 pasos;
  - aisladas: las mismas islas, con las mismas semillas, sin migración.
- **Semillas nuevas 11–18**, 300 000 pasos, 6 procesos.
- **Comando:**
  `python experiments/fase12/archipielago.py --pasos 300000 --semillas 11 12 13 14 15 16 17 18 --salida runs/fase12/archipielago.json`
- **Medidas:** promedio de las islas vivas en el último tercio (t ≥ 200 000).

## Reglas (permutación pareada exacta, una cola, α = 0,05)
| Regla | Qué afirma | Criterio |
|---|---|---|
| **R1** | La migración mejora la adaptación a las estaciones ocultas | `acierto_comida` migración > aisladas, p < 0,05 |
| R2 | La migración mantiene viva la variación | `tasa_efectiva_media` migración > aisladas, p < 0,05 |

- **Exploratorias:** perfiles distintos, genes medios, población, fracción enlazada, y extinciones de islas por condición.
- **Expectativa honesta:** el piloto no muestra efecto. Lo más probable es un resultado nulo. Con islas de este tamaño (~100–150 organismos), la deriva es fuerte, y el rescate de islas puede ser el único efecto visible.

## Cómo se interpretará
- **R1 positiva:** primera mejora de la adaptación por estructura de población, sin cambiar la física. Siguiente: islas con físicas distintas (clima real, estímulos, más dura), que es la visión original de la etapa.
- **R2 sola:** la migración sostiene la variación, pero esa variación no se traduce en mejor adaptación.
- **Ambas negativas:** con islas homogéneas, la migración solo mezcla poblaciones que ya se parecen. Siguiente: islas heterogéneas, donde cada isla seleccione algo distinto.

## Resultado (2026-10-29): negativo en R1 y R2; menos extinciones con migración
- **Pares completos:** 7. La semilla 13 aislada perdió sus 3 islas antes del paso 106 475 y no tiene último tercio.
- **R1 (acierto_comida):** 3 de 7 diferencias positivas (−0,012 a +0,010); p = 0,71. **No se cumple.** Las dos condiciones quedan en ~0,53–0,55.
- **R2 (tasa_efectiva_media):** 1 de 7 positiva; p = 0,91. **No se cumple.** La tasa colapsa a ~0,001–0,002 en las dos condiciones, es decir, el monocultivo de siempre.
- **Exploratorias:** perfiles, genes, población y enlazados, todo nulo (p de 0,55 a 0,73).
- **Extinciones de islas (exploratorio, no prerregistrado como regla):** 3 de 24 con migración contra 8 de 24 aisladas, incluida una semilla con las 3 islas extintas. La migración evita extinciones, sobre todo en el primer tramo (pasos 28 000–35 000, cuando la toxicidad llega a pleno). Ojo: una isla que llega a cero no se repuebla, porque el anillo solo incluye islas con más de un organismo. El efecto es de **prevención**, no de recolonización.
- **Lectura:** se cumple la expectativa escrita antes de correr. Con islas iguales, la migración mezcla poblaciones que ya se parecen: no aporta variación nueva ni mejora la adaptación. Solo amortigua los malos momentos.
- **Siguiente:**
  - islas heterogéneas, cada una seleccionando algo distinto;
  - y, sobre todo, un mundo donde aprender o predecir pague: el "mundo del texto", con predicción de la próxima letra (ver `07-traspaso.md`).
