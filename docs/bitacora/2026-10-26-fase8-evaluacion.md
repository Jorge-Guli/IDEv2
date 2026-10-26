# 2026-10-26 · Fase 8: memoria esencial (mundo de mosaico), resultados

Prerregistro: [`2026-10-26-fase8-prerregistro.md`](2026-10-26-fase8-prerregistro.md). Corrido en el equipo local (41 minutos). Informe: [`2026-10-26-fase8-informe.json`](2026-10-26-fase8-informe.json).

- 6 semillas (151–156), 300 000 pasos: **1600–2950 generaciones** en las corridas que sobrevivieron.
- **Extinciones: 4 de 24** (por el cuello de botella inicial del mundo de mosaico): la semilla 151 en tres condiciones y la 154 en `mem_info`. En `mem_info` 151, la población quedó en 1 organismo.

## Hipótesis
| # | Resultado | Veredicto |
|---|---|---|
| M4: acierto de `mem_info` > 0,6 en ≥ 4/6 | 0,51–0,55 en 5/5 sobrevivientes | ❌ |
| M1: `mem_info` > `mem_ruido` | diferencias −0,01 a +0,01 (p = 0,31) | ❌ |
| M2: la memoria sigue a la estación | \|seguimiento\| = 0,01 en 5/5 | ❌ |
| M3: `mem_info` > `sin_memoria` | −0,01 a +0,01 (p = 0,56) | ❌ |

- **Genes de memoria:** ≤ 1 % en todas las corridas.
- **Acierto medio:** 0,53 en las cuatro condiciones. El pequeño exceso sobre 0,5, igual con memoria y sin ella, viene probablemente de un resto de estructura espacial en el mosaico; no es memoria.

## Lectura
1. **El mundo no es el problema.** En el mosaico, la memoria es la única forma de pasar del azar, y en los pilotos un LUCA con memoria igualaba a poblaciones con ~280 generaciones de evolución sin ella. El premio existe y es grande.
2. **La evolución no encuentra la solución.** Usar la pista exige, a la vez, un gen que escriba la memoria a partir de la pista y una regla de comer que dependa de la combinación tipo × memoria (con este genoma, al menos dos genes coordinados), y además una forma de irse a buscar la comida correcta. Cada pieza sola no da ventaja. Es un valle en el paisaje de aptitud que la mutación al azar no cruza en ~3000 generaciones.
3. **Es el mismo límite que en las fases 3b, 5, 6 y 7:** con un genoma de reglas que suman entradas, las innovaciones que exigen **combinar** información (sincronizar, diferenciarse, recordar y usar) quedan lejos en el espacio de mutaciones.

## Decisión
**Fase 9: regulación genética condicionada.** En biología, un gen se expresa o no según el estado de la célula: factores de transcripción, interruptores epigenéticos. Así, "comer A" o "comer B" puede depender de un estado interno con una sola mutación. Se agrega a cada gen una **condición heredable**: que se exprese siempre, o solo si una variable de memoria está alta, o solo si está baja. Con eso, la regla "en estado X comé A, en estado Y comé B" queda a uno o dos pasos de mutación. Se verificará primero con pilotos y competencias.
