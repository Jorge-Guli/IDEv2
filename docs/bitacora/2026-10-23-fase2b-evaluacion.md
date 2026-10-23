# 2026-10-23 · Fase 2b: bien público, resultados

Hipótesis y umbrales prerregistrados en [`2026-10-23-fase2b-prerregistro.md`](2026-10-23-fase2b-prerregistro.md), con un addendum agregado antes de la repetición.

## Configuración
- `experiments/configs/bien_publico.toml`: recurso simple escaso (capacidad 5) y recurso complejo abundante (capacidad 20). La enzima se recalibró tras la revisión científica (`experiments/fase2b/calibrar.py`) para que haya dilema: un secretor solo recupera el 0,81 de su costo, un bloque de secretores el 1,39, y lo producido en total es 2,1 veces el costo.
- Evaluación 1: 8 condiciones × 15 semillas (5 aquí y 10 en el equipo local), 30 000 pasos. Informes: [`2026-10-23-fase2b-informe.json`](2026-10-23-fase2b-informe.json) y `resultados/fase2b/informe_semillas_6_15.json`.
- Evaluación 2 (repetición de H2 y H3 con un genoma secretor viable): 5 condiciones × 10 semillas. Informe: [`2026-10-23-fase2b-h3-informe.json`](2026-10-23-fase2b-h3-informe.json).

```bash
python experiments/fase2b/evaluar.py --salida runs/fase2b --semillas 5
python experiments/fase2b/evaluar.py --salida runs/fase2b_h3 --semillas 10 --condiciones sembrado_secretor \
    sembrado_secretor_asoc_inerte sembrado_colonial sembrado_colonial_empuje sembrado_colonial_asoc_inerte
```

## Criterios
Los cuatro aprobados en ambos equipos:
- C1, persistencia: 4/5 aquí y 9/10 en el equipo local.
- C2, conservación de la materia: error relativo de ~1e-16.
- C3, reproducibilidad: huella idéntica.
- C4, rendimiento: 50 pasos/s aquí y 198 en el equipo local.

## Hipótesis

| # | Predicción | Resultado | Veredicto |
|---|---|---|---|
| H1 | Público: secreción < 0,2; privado: > 0,8 | Público: 0,2–12 % en las 13 semillas que sobrevivieron (media ~2 %). Privado: ~100 % en 12 de 13 | ✅ **Confirmada** |
| H4 | Desde LUCA, la asociación no cambia nada (diferencia < 0,1) | Diferencia de 0,01–0,04 | ✅ **Confirmada** |
| H2 | Si la secreción ya está, cae por debajo de 0,5 en ≥ 8/10 | 7/10 con asociación activa; 4/10 con asociación inerte | ❌ No alcanza el umbral |
| H3 | Las colonias superan al control en ≥ 8/10 (diferencia ≥ 0,2) | Unánime: sobreviven 3/10, superan al control en 1/10 (diferencia −0,23). Empuje: sobreviven 6/10, superan en 3/10 (−0,13). El control sobrevive 10/10 | ❌ **Refutada** |

**Sobre la primera evaluación de H2 y H3.** Las colonias se extinguieron en 15 de 15 semillas, pero esa prueba quedó **anulada**: el genoma secretor diseñado a mano secretaba en el 25 % de los pasos y colapsaba con o sin colonias. Ver el addendum.

## Lo que muestran los datos
1. **El dilema del bien público existe en la simulación.** La misma química con el beneficio privado lleva la secreción al 100 % y la población a ~1400. Con el beneficio público, la secreción no arranca desde rara y la población queda en ~250 (tragedia de los comunes).
2. **La estructura espacial sostiene la cooperación en parte.** Sembrada la secreción y sin asociación efectiva, se mantiene por encima de 0,5 en la mitad de las semillas. La razón es que los hijos nacen en una celda vecina a la de su progenitor: **los vecinos ya son parientes sin necesidad de pegarse**, y el bien público queda en buena parte "en familia".
3. **Pegarse no agrega parentesco, pero sí costos.** Las colonias pagan mantenimiento de enlaces y movilidad, y como el parentesco con los vecinos ya era alto, no ganan nada a cambio. El movimiento por empuje colectivo duplica la supervivencia de las colonias (3/10 → 6/10) y permite grupos más grandes (hasta 11), pero no las vuelve ventajosas.

## Interpretación
- La pregunta "¿bajo qué condiciones rinde asociarse?" tiene ahora una respuesta parcial y precisa. **Un bien público no alcanza cuando la dispersión ya es local**: el parentesco espacial cumple la función que se esperaba de la asociación. Esto coincide con la teoría de la selección de parentesco en poblaciones estructuradas, donde la competencia local y la dispersión limitada pueden sustituir a la agregación.
- Para que asociarse rinda, el grupo tiene que conseguir algo que **solo es posible estando físicamente juntos**, no solo cerca.

## Limitaciones
- No se hizo la prueba de invasión del aprovechado ni el cruce factorial asociación × difusión que sugirió la revisión. Quedan pendientes si se retoma el bien público.
- La supervivencia de las colonias es muy variable entre semillas (mapas distintos). Diez semillas alcanzan para el veredicto, pero no para medir bien el tamaño de los efectos.

## Decisión
Pasar a una ecología donde el beneficio dependa del **tamaño físico del grupo**: **depredación limitada por tamaño** (fase 2c). Es el mecanismo con mejor respaldo experimental para el origen de la multicelularidad: el alga *Chlorella vulgaris* evolucionó colonias en menos de 100 generaciones bajo un depredador que solo podía tragar células sueltas (Boraas et al. 1998), y *Chlamydomonas reinhardtii* lo repitió en experimentos de evolución (Herron et al. 2019).
