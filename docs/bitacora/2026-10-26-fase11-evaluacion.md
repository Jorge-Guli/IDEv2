# 2026-10-26 · Fase 11: modulación por el estado interno, evaluación

Prerregistro: [2026-10-26-fase11-prerregistro.md](2026-10-26-fase11-prerregistro.md). Informe y series: `resultados/fase11/` (incluye las poblaciones finales).

## Corrida
`experiments/fase11/evaluar.py`, parte A:
- **Punto de partida:** las 6 poblaciones de la fase 10 con memoria.
- **Condiciones:** 4 (`a_mod` y `a_sin_mod`, cada una con argmax y con softmax a T = 0,25).
- **Duración:** 300 000 pasos, ~1700–2700 generaciones adicionales; 70 minutos en la PC del autor.
- **Extinciones:** una sola población de origen (186), en los dos brazos con softmax. Esa población ya era la más chica (~60–90 organismos).

## Hipótesis
| # | Regla | Resultado |
|---|---|---|
| A1 | acierto `a_mod` > `a_sin_mod` (6 pares) | **No**: diferencias de −0,008 a +0,004, p = 0,63 |
| A2 | acierto `a_mod` > 0,6 en ≥ 3 de 6 | **No** (0,516–0,534) |
| A3 | acierto `a_mod_softmax` > `a_sin_mod_softmax` (5 pares) | **No**: diferencias de −0,005 a +0,003, p = 0,91 |
| A4 | acierto `a_mod_softmax` > 0,6 en ≥ 3 | **No** (0,521–0,535) |

## Lectura
1. **La memoria se sostiene otra vez,** ahora ~2000 generaciones más, con memoria inicial 0,5: seguimiento ~0,5 (el máximo práctico de la métrica) en 22 de 23 corridas sobrevivientes. La excepción es `a_sin_mod` 186, que perdió la memoria. Es una réplica de la persistencia observada en la fase 10.
2. **La memoria no se recluta para decidir,** ni con modulación ni con decisión estocástica.
   - **Genomas finales:** hay genes modulados en algunas poblaciones (hasta 4 por organismo en la 183), pero casi ninguno pesa el tipo de comida.
   - **Los dos únicos casos con peso apreciable no sirven para elegir comida:** un gen de **dividirse** modulado por la memoria A (183) y un gen de comer modulado por la memoria **B**, que nadie escribe (184 con softmax).
3. **Por qué, según los pilotos y las competencias:**
   - el módulo modulado de dos genes, armado a mano, gana en 7–8 de 8 competencias, así que el premio existe;
   - pero el camino para construirlo empieza con piezas neutras o costosas: un gen nuevo, la condición de modulación y un peso grande sobre el tipo de comida;
   - y los genes ya presentes están saturados: pesos de ~10–20 dentro de una tanh por gen, que ni el softmax destraba;
   - **es el mismo patrón de las fases 8 y 9,** un paso más arriba: el premio final existe, y el camino tiene un tramo sin pendiente.

## Qué queda establecido (fases 9–11)
- **Primer peldaño:** con premio propio y protegido contra atajos, la memoria se sostiene miles de generaciones (fases 10 y 11).
- **Segundo peldaño, el uso para decidir:** ninguna de las tres arquitecturas probadas lo vuelve alcanzable en ~2000 generaciones:
  - condición de expresión por gen;
  - modulación del receptor químico;
  - decisión estocástica.
- **Lo que limita ya no es el mundo ni la representación.** La hipótesis de una saturación general de los genes no se confirmó en la medición posterior (ver abajo). El límite parece ser que el segundo peldaño exige varias piezas que solo pagan juntas.

## Medición de evolucionabilidad (posterior a la corrida, exploratoria)
**Qué se midió:** en qué fracción de las decisiones cambia la acción elegida tras una mutación puntual de peso o de sesgo de un gen al azar. Situaciones reales tomadas a los 1000 pasos de una corrida sin mutación; 20 repeticiones.

| Origen | σ = 0,3 (la de la simulación) | σ = 3 |
|---|---|---|
| LUCA | 0,14 % | 8,0 % |
| Fase 10, población 188 | 1,5 % | 9,9 % |
| Fase 11, `a_mod` 183 | 1,7 % | 11,3 % |

**Las poblaciones evolucionadas no son menos evolucionables que LUCA en esta medida global:** una mutación cambia más decisiones, no menos. **La hipótesis de la saturación como límite general no se sostiene así como está.** Puede valer para las decisiones específicas que harían falta (irse de la comida que no coincide con la memoria), pero eso queda por medir. La explicación más simple que sigue en pie es la de las piezas neutras o costosas: un gen nuevo, la condición y un peso grande sobre el tipo de comida, que solo pagan juntas.

## Decisión
Pendiente de la revisión científica independiente de las fases 9–11 (en curso). Las opciones que se evalúan para la fase 12:
- **Medir la evolucionabilidad directamente:** qué fracción de mutaciones al azar cambia la conducta, en LUCA y en poblaciones evolucionadas. Así se cuantifica la saturación antes de cambiar el genoma.
- **Una regla de impulso menos saturable:** por ejemplo, la tanh sobre la suma de los genes de cada primitiva, en lugar de una tanh por gen. Sería una decisión de modelo nueva, con sus controles.
- **Mutaciones de peso con colas largas:** saltos grandes ocasionales.
