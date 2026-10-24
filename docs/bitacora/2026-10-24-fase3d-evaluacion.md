# 2026-10-24 · Fase 3d: ablación y sensibilidad, resultados

Prerregistro: [`2026-10-24-fase3d-prerregistro.md`](2026-10-24-fase3d-prerregistro.md). Corrido en el equipo local (90 minutos). Informe: [`2026-10-24-fase3d-informe.json`](2026-10-24-fase3d-informe.json).

## Parte A: ablación
20 poblaciones evolucionadas con percepción (réplica de la fase 3c), sin mutación. En 4 de ellas (74, 75, 82 y 83) no hay grupos ni siquiera en el brazo intacto.

| Brazo (media de 20) | Grupos ≥ 3, formación | Grupos ≥ 3, mantenimiento | Población (mantenimiento) | Alineación (mantenimiento) | Éxito del empuje ≥ 3 |
|---|---|---|---|---|---|
| intacto | **0,31** | **0,31** | **686** | **0,74** | 0,60 |
| sin aprendizaje | 0,28 | 0,29 | 672 | 0,75 | 0,61 |
| cero | 0,19 | 0,25 | 627 | 0,17 | 0,55 |
| barajado | 0,15 | 0,22 | 617 | 0,13 | 0,54 |
| solo rumbo | — | 0,31 | 686 | 0,74 | 0,60 |
| solo señales | — | 0,25 | 627 | 0,17 | 0,55 |

| # | Predicción | Resultado | Veredicto |
|---|---|---|---|
| A1 | La información mantiene los grupos | intacto − cero: +0,08 (15 semillas con grupos), p = 0,049 | ✅ en el límite (yo predije que no) |
| A2 | La información es necesaria para formarlos | intacto − cero: **+0,12**, p = **0,002** | ✅ (predicción incierta) |
| A3 | La alineación depende de la información en vida | +0,23 a +0,69 en **16/16** | ✅ |
| A4 | La alineación es heredada | sin aprendizaje − cero: +0,24 a +0,68 en **16/16** | ✅ |
| A5 | El efecto es del rumbo | solo rumbo − solo señales = A1 (+0,08, p = 0,049) | ✅ |
| A6 | La información mejora la economía de la población | +59 organismos (~9 %), en 16/16 semillas con población distinta; p < 0,001 | ✅ |

**Las señales no tienen ningún efecto, ni siquiera mínimo.** En las 20 semillas, "solo rumbo" dio exactamente lo mismo que "intacto", y "solo señales" exactamente lo mismo que "cero". No es un error: con una población que sí emite señales, los brazos difieren (se verificó). Como emitir cuesta energía, cualquier señal habría cambiado la trayectoria. La igualdad exacta prueba que **ninguna población de la réplica emitía señales**: los genes estaban presentes, en hasta el 43 % de la población en la semilla 77, pero callados.

## Parte B: sensibilidad (semillas nuevas, 91–100)
| # | Comparación | Grupos ≥ 3 (media) | p | Veredicto |
|---|---|---|---|---|
| S1 | α = 1/3: ambos contra barajado | **0,41** contra 0,22 (diferencia ≥ 0,1 en 8/10) | 0,008 | ✅ |
| S2 | α = 0,75: ambos contra barajado | 0,05 contra 0,00 | 0,009 | ✅, pero el efecto es mínimo: con α = 0,75 casi no hay grupos |
| S3 | α = 0,5: solo rumbo contra barajado | **0,29** contra 0,07 | 0,001 | ✅ |

La semilla 97, con un ancestro poco asociado (0,29), no forma grupos en ninguna condición, como ya había pasado en la réplica.

## Lo que muestran los datos
1. **La información sobre el rumbo de los socios actúa en vida:**
   - sin ella, la misma población (los mismos genomas) forma menos grupos (−0,12 de la población en grupos de 3 o más), los mantiene algo peor (−0,08), se alinea mucho menos (0,74 → 0,17) y sostiene un 9 % menos de organismos;
   - mi predicción ("la información no sostiene a los grupos en vida") era errónea;
   - el piloto del revisor, con 3 poblaciones, no tenía potencia para verlo.
2. **La alineación es heredada:** se mantiene sin aprendizaje y con los ajustes plásticos en 0. La evolución cableó los genes que conectan el rumbo de los socios con girar.
3. **Todo el efecto es del rumbo; las señales no se usan.** El canal arbitrario de comunicación no se inventó en ningún experimento. La percepción "mecánica" del rumbo sí se usó.
4. **El efecto no depende de un único valor del modelo:** se repite con α = 1/3, con un efecto más grande, y aparece débil con α = 0,75, donde la física casi no permite grupos.

## Conclusión de la línea de fases 3 a 3d
Con movimiento por fuerza (α entre 1/3 y 0,5), los organismos evolucionan, a partir de una percepción local del rumbo de sus socios, una **alineación heredada** que les permite **formar y sostener más grupos de 3 o más** frente a un depredador limitado por tamaño, y sostener poblaciones mayores. Se apoya en lo siguiente:
- dos evaluaciones con 30 semillas;
- una sensibilidad con 10 semillas más;
- una ablación pareada con 20 poblaciones;
- controles barajado y sin percepción.

En el lenguaje de la hipótesis fundacional es un paso mínimo pero real: **una coordinación entre individuos que evoluciona y hace posible un nivel de organización que sin ella es más débil.**

## Límites
- Hizo falta cambiar la regla de movimiento después de un resultado negativo (decisión de modelo justificada por las fases 3 y 3b).
- La comunicación propiamente dicha (señales arbitrarias) no emergió.
- Los grupos son de 3 a 16 miembros, sin división del trabajo ni reproducción propia del grupo.
- El estado del ancestro pesa mucho: sin asociación previa, nada de esto ocurre (5 de 30 semillas).

## Decisión
Pasar a la **fase 4: el colectivo como individuo**, con la física "fuerza" (α = 0,5) y la percepción del rumbo. El canal de señales queda disponible, pero no se espera que se use.
