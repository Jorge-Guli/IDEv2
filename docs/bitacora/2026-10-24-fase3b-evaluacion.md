# 2026-10-24 · Fase 3b: prueba de invasión, resultados

Prerregistro: [`2026-10-24-fase3b-prerregistro.md`](2026-10-24-fase3b-prerregistro.md), con su addendum. Semillas 51–60, corridas en el equipo local (21 minutos). Informe: [`2026-10-24-fase3b-informe.json`](2026-10-24-fase3b-informe.json). La exclusión por genoma lleno resultó casi nula: 0 en 9 ancestros y 0,08 % en la semilla 60.

## Hipótesis prerregistradas
| # | Variante | Resultado | Veredicto |
|---|---|---|---|
| I1 | seguir | Fracción del coordinado ≥ 0,7 en 5/10 semillas: en 1 de ellas quedan solo 2 individuos (semilla 60) y en 3 se extinguen las dos líneas marcadas | ❌ |
| I1 | alinear | 0/10 | ❌ |
| I1 | ambos | 0/10 | ❌ |
| I2 | seguir | Los grupos de 3 o más del coordinado se mueven más que los del control en **10/10** semillas, pero poco: +0,05 de media (+0,002 a +0,11) | ✅ |
| I2 | alinear | Se mueven **menos** en 9/9 (−0,01 a −0,14) | ❌ |
| I2 | ambos | Menos en 7/9 | ❌ |
| I3 | seguir | Mayor fracción con refugio 3 que con refugio 2 en 5/10 | ❌ |
| I3 | alinear, ambos | 0/10 | ❌ |

## Lectura frente a la deriva (exploratorio, no prerregistrado)
Con 20 % de coordinados al inicio y sin mutación, una línea neutral termina presente (> 5 % de la población) en ~2 de 10 semillas. El control marcado, que es neutral por construcción, quedó presente en 2–5 de 10 según la condición: la deriva es fuerte, porque las poblaciones caen al principio con refugio 3.

| Variante | Coordinado presente al final, refugio 3 | Ídem, refugio 2 | Control marcado presente (r3 / r2) |
|---|---|---|---|
| seguir | **4/10** (0,45 / 1,0 / 0,53 / 1,0 de la población) | **0/10** | 2 / 2 |
| alinear | 0/10 | 0/10 | 3 / 5 |
| ambos | 0/10 | 0/10 | 4 / 4 |

- **Seguir al que empuja** tiene una ventaja débil cuando el depredador exige tríos y una desventaja cuando no los exige. Bajo deriva neutral, P(≥ 4/10) = 0,12, y la diferencia entre refugio 3 y refugio 2 (4/10 contra 0/10) da p ≈ 0,04 (Fisher, una cola). Es consistente, pero con una sola comparación elegida después de ver los datos: no es una prueba.
- **Alinearse, tal como se diseñó, es claramente perjudicial:** los grupos se mueven menos, y el coordinado desaparece en 20 de 20 corridas (bajo deriva neutral, P = 0,01). Girar ocupa la acción de un paso: quien gira no come ni empuja.

## Lo que muestran los datos
1. **En esta física, un trío coordinado casi no gana nada.** El mejor diseño probado mejora la movilidad de los grupos grandes en ~5 puntos y no invade de forma confiable.
2. Esto **explica el resultado de la fase 3:** la ventaja de sincronizar es chica frente a la deriva, y alinearse cuesta acciones. La selección no tiene de dónde tirar.
3. El problema no es solo de accesibilidad evolutiva, como se sospechaba: **el valle está en la física del movimiento.** Para empujar juntos hay que estar alineados, alinearse cuesta pasos y el umbral castiga cualquier descoordinación.

## Decisión
Según el prerregistro ("nada invade"), el paso siguiente es una **decisión de modelo sobre la regla de movimiento**, con prerregistro y semillas nuevas, corrigiendo antes la anisotropía, como pidió la revisión de la fase 3. Se presenta como un cambio del modelo justificado por estos resultados, no como evidencia de que la coordinación emergió.
