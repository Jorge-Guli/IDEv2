# 2026-10-23 · Fase 2b: prerregistro de hipótesis

Escrito **antes** de correr la evaluación (`experiments/fase2b/evaluar.py`, 8 condiciones × 5 semillas × 30 000 pasos), para no acomodar la interpretación a los datos.

## Contexto
- **Calibración** (`experiments/fase2b/calibrar.py`), recalibrada tras la revisión científica: un secretor solo recupera el 0,81 de su costo, un bloque de 3×3 secretores el 1,39, y lo producido en total es 2,1 veces el costo. Es decir, hay un dilema: secretar no conviene en soledad, pero sí si los vecinos también secretan.
- **Piloto** (2 semillas, 15 000 pasos): desde LUCA, con **bien privado** la secreción llega al 100 %; con **bien público** se queda en ~1 %. Coincide con la teoría de los bienes públicos: un cooperador raro no puede invadir.

## Hipótesis y predicciones
Las medidas son del último cuarto de cada corrida; "en k de 5" se cuenta por semilla.

| # | Hipótesis | Predicción (umbral) |
|---|---|---|
| H1 | Con bien público, la secreción no se descubre (no invade desde rara); con bien privado, sí | `publico`: `tiene_secretar` < 0,2 en ≥ 4/5; `privado`: > 0,8 en ≥ 4/5 |
| H2 | Si la secreción ya está, los aprovechados la invaden con bien público | `sembrado_secretor`: `tiene_secretar` final < 0,5 en ≥ 4/5 (parte de 1,0) |
| H3 | **La agrupación clonal rescata la cooperación**: los grupos de clones retienen el bien público entre parientes | `sembrado_colonial` supera a `sembrado_colonial_asoc_inerte` en `tiene_secretar` final en ≥ 4/5 semillas pareadas, con diferencia media ≥ 0,2 |
| H4 | Desde LUCA, la asociación no cambia nada a esta escala (el cuello de botella es descubrir la combinación) | `publico` contra `publico_asoc_inerte`: diferencia media de `tiene_secretar` < 0,1 |

**Controles:** `secrecion_inerte` (la secreción no hace nada: la población solo tiene recurso simple) y los inertes de asociación (mismo espectro mutacional, sin enlaces efectivos).

## Decisiones según el resultado
- **H3 se cumple** → la agrupación entre parientes vuelve rentable un bien público: primera condición identificada en la que la asociación paga. Siguiente paso: fase 3 (colectivo como individuo) en este mundo, y medir si los grupos se reproducen como unidad.
- **H3 no se cumple, pero H2 sí** → la agrupación clonal no alcanza con esta difusión. Probar un beneficio más local (difusión menor) y la variante "compartir + división unida".
- **Ni H2 ni H3** → el dilema no es tal en la dinámica completa (por ejemplo, porque los secretores se agrupan solos por la estructura espacial). Recalibrar o pasar a la condición de depredación.
