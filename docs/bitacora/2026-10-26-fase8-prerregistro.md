# 2026-10-26 · Fase 8: un mundo donde la memoria es esencial, prerregistro

Escrito antes de correr. Antecedentes: [fase 7](2026-10-26-fase7-evaluacion.md) y [fase 7b/7c](2026-10-26-fase7b-invasion.md).

## Qué cambia respecto de la fase 7
En la fase 7, los dos tipos de comida estaban en parches grandes. Sin memoria se acertaba ~75 % gracias a la selección espacial, y una población evolucionada sin memoria eliminaba a un LUCA con memoria. **En el mundo de mosaico, los dos tipos están entremezclados celda a celda:** no hay zonas buenas donde refugiarse y, sin memoria, el acierto no puede pasar del azar.

## Pilotos (semilla 801, 50 000 pasos, ~100–280 generaciones; no entran en la evaluación)
- **Con castigo 0,5,** todas las poblaciones se extinguieron cerca del paso 3300. Con castigo 0 y 0,2 son viables.
- **Acierto:** 0,52 con memoria y sin ella. El mundo bloquea los atajos, pero en ese tiempo la memoria no evolucionó.
- **Competencias (castigo 0,2):**
  - LUCA con memoria contra LUCA: gana en 4/4.
  - LUCA con memoria contra una población evolucionada sin memoria (~280 generaciones): parejo (gana en 1, pierde en 2, una tendencia a perder).
  - En el mundo de parches perdía siempre: aquí **la memoria vale tanto como ~280 generaciones de otras mejoras**.

## Diseño
- `python experiments/fase7/evaluar.py --mundo mosaico`, desde LUCA.
- **Mundo:** mosaico fino, castigo 0,2, toxicidad diferida, pista con probabilidad 0,01, estaciones de 2000 pasos, memoria con tasa 1.
- **Duración:** 300 000 pasos (~1000–1500 generaciones); semillas nuevas 151–156.
- **Condiciones:** `mem_info`, `mem_ruido` (pista aleatoria), `sin_memoria` y `mem_info_apr` (con aprendizaje).

## Hipótesis y reglas (las calcula el script)
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| **M4** | La memoria evoluciona y se usa (en este mundo es la única forma de pasar del azar) | acierto de `mem_info` > 0,6 en ≥ 4 de 6 | Incierta |
| M1 | El beneficio viene de la información | acierto `mem_info` > `mem_ruido`, pareada, p < 0,05 | Incierta |
| M2 | La memoria sigue a la estación | \|seguimiento\| > 0,3 en ≥ 4 de 6 | Incierta |
| M3 | Tener memoria mejora frente a no tenerla | acierto `mem_info` > `sin_memoria`, p < 0,05 | Incierta |

Control de fugas: `sin_memoria` y `mem_ruido` deberían quedar en ~0,5. Si superan claramente 0,55, hay otra fuente de información, y eso se investiga antes de interpretar.

## Cómo se interpretará
- **M4, M1 y M2:** **primera memoria evolucionada del proyecto**, usada para decidir según una información que ya no está presente. Es un peldaño cognitivo real. Seguiría la ablación (apagar la memoria en poblaciones evolucionadas) y después reclutarla en grupos.
- **Negativo con el control limpio:** la evolución no encuentra en ~1500 generaciones la regla de cinco genes que hace falta, aunque el premio exista. Seguiría ampliar la regulación genética, para que esa regla quede más cerca en el espacio de mutaciones.
