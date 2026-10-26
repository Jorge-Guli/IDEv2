# 2026-10-26 · Fase 7: memoria de contexto, resultados

Prerregistro: [`2026-10-25-fase7-prerregistro.md`](2026-10-25-fase7-prerregistro.md). Corrido en el equipo local (49 minutos). Informe: [`2026-10-26-fase7-informe.json`](2026-10-26-fase7-informe.json).

- 6 semillas (141–146), 200 000 pasos: 650–1450 generaciones.
- Sin extinciones.

## Hipótesis
| # | Resultado | Veredicto |
|---|---|---|
| M1: la pista informativa mejora el acierto frente a la aleatoria | diferencias −0,016 a +0,013 (p = 0,77) | ❌ |
| M2: la memoria sigue a la estación | \|seguimiento\| = 0,04 en 6/6 (memoria fija) | ❌ |
| M3: tener memoria mejora frente a no tenerla | diferencias −0,03 a +0,01 (p = 0,95) | ❌ |

- **Acierto medio (último cuarto):** `mem_info` 0,78, `mem_ruido` 0,78, `sin_memoria` 0,79, `mem_info_apr` 0,79.
- La semilla 143 tiene el acierto más alto en todas las condiciones (0,85–0,87): depende del mapa, no de la memoria.

## Observación exploratoria
**En el control con pista aleatoria, la memoria se fijó en 2 de 6 semillas** (143 y 144: genes de memoria en el 99–100 % de la población) y quedó **correlacionada con la estación** (seguimiento −0,44 y +0,39, también a mitad de la corrida). Como la pista no informaba nada, la memoria tuvo que integrar otra señal que depende de la estación: probablemente el veneno acumulado (que llega por la energía) o la experiencia de comer cada tipo. Es una memoria **de la experiencia**, no de la pista, y no mejoró el acierto frente a las demás condiciones de esas semillas. En `mem_info` no pasó en ninguna semilla. Con 2 casos en el control, es anecdótico.

## Interpretación
1. En este mundo, la memoria de una pista intermitente no evolucionó en ~1000 generaciones. Para usarla, el genoma tiene que combinar dos entradas de forma no lineal (comer A si la memoria dice A, y B si dice B). Con genes que suman sus entradas y una tanh, eso exige varios genes coordinados. Es un problema de **expresividad del genoma**, que ya apareció en las fases 3b, 5 y 6.
2. La memoria sí puede fijarse cuando integra experiencia (semillas 143 y 144 del control). El canal funciona; lo difícil es conectarlo con la decisión.

## Decisión
Ampliar la **regulación genética**: genes reguladores cuyo valor no es una acción, sino una variable interna que leen los demás genes (una capa oculta, como las redes de regulación génica). Así la combinación no lineal queda a un paso de mutación, en lugar de exigir varios genes coordinados. Se prueba primero en el mundo de la fase 7, porque es barato y tiene una respuesta clara.
