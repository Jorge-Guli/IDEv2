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

## Addendum (2026-10-23, antes de la repetición)

**Qué pasó con H3 en la primera evaluación.** Las colonias sembradas se extinguieron en las 15 semillas (5 aquí y 10 en el equipo local). El diagnóstico posterior mostró que la causa principal fue el **genoma secretor diseñado a mano**: secretaba en el 20–27 % de los pasos y la población sembrada colapsaba (de 200 a ~20) **con o sin colonias**. El control inerte también colapsaba y solo sobrevivía en algunas semillas por suerte. H3 quedó confundida y **no se considera puesta a prueba**. H1, H2 y H4 no dependen de ese genoma (H2 sí lo usa, pero su resultado, la pérdida de la secreción, se mantiene con más razón: un secretor malo se pierde antes).

**Corrección.** Un nuevo genoma secretor (secreta en el 1–3 % de los pasos, solo con recurso complejo, sin comida a mano y bien alimentado), con verificación automática de viabilidad: no puede quedar por debajo del 70 % de la población de LUCA en el mismo mundo (`verificar_viabilidad` en `evaluar.py`).

**Repetición prerregistrada (10 semillas, 30 000 pasos):**
- **H3** (sin cambios en su enunciado): `sembrado_colonial` supera a `sembrado_colonial_asoc_inerte` en `tiene_secretar` final en ≥ 8/10 semillas pareadas, con diferencia media ≥ 0,2.
- **H3-empuje**: lo mismo para `sembrado_colonial_empuje` (colonias que se mueven por la suma de los empujes de sus miembros) contra el mismo control.
- Se registra también la **supervivencia** de cada condición: si las colonias se extinguen en ≥ 5/10 semillas, la conclusión es que en este mundo pegarse tiene un costo letal que la cooperación no compensa.
