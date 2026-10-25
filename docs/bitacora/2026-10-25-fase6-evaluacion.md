# 2026-10-25 · Fase 6: memoria interna y corridas largas, resultados

Prerregistro: [`2026-10-25-fase6-prerregistro.md`](2026-10-25-fase6-prerregistro.md). Corrido en el equipo local (103 minutos). Informe: [`2026-10-25-fase6-informe.json`](2026-10-25-fase6-informe.json).

- 5 semillas (131–135), 150 000 pasos por rama: entre **940 y 2750 generaciones** (más en las condiciones con retornos crecientes, porque la población es mayor y se reproduce más).
- No hubo extinciones.

## Hipótesis
| # | Resultado | Veredicto |
|---|---|---|
| L1: roles más diversos con memoria | memoria − base: −0,01 a +0,01 (p = 0,38); eco_memoria − eco: −0,03 a +0,00 (p = 0,88) | ❌ |
| L2: la memoria se diferencia en los grupos | dispersión de la memoria ≤ 0,001 en todas las semillas | ❌ |
| L3: la memoria se asocia al rol | no medible (memoria ≈ 0) | ❌ |

## Lo que muestran los datos
1. **La memoria nunca se usó.** Los genes de memoria quedaron en ≤ 0,5 % de la población (3,7 % en un caso aislado), y la memoria media siempre fue ≈ 0. No fue seleccionada en ningún momento: tampoco en la ventana del medio.
2. **Sin diferenciación de roles:** la dispersión dentro de los grupos quedó en ~0,11–0,14, igual que sin memoria. Los valores altos aislados (0,30 y 0,49) corresponden a poblaciones casi sin grupos, donde la métrica se calcula sobre muy pocos.
3. **Hallazgo inesperado: los grupos se pierden en corridas largas.** Al final:
   - `base`: grupos de 3 o más en 4 de 5 semillas;
   - `memoria`: 4 de 5;
   - `eco` (retornos crecientes y puentes): **2 de 5**;
   - `eco_memoria`: **2 de 5**.
   
   Con retornos crecientes la población se triplica y la asociación se erosiona. Una hipótesis posible es que, con comida que rinde más, el costo de no estar en grupo baja frente al costo de los enlaces y del movimiento conjunto. No se probó.

## Interpretación
- Una memoria disponible no se usa si nada en el mundo la recompensa. En este mundo, las decisiones buenas dependen de lo que el organismo percibe en el momento: comida aquí y al frente, socios, rumbo. Una estrategia reactiva alcanza. **La memoria (y probablemente cualquier cognición más rica) solo va a evolucionar en un mundo que la exija.**
- La división del trabajo sigue sin aparecer con todos los ingredientes teóricos que se agregaron: grupos clonales, retornos crecientes, energía compartida y memoria.

## Decisión
Cambiar de eje. En lugar de agregar más maquinaria para la división del trabajo, **construir un mundo que exija memoria y anticipación** (fase 7): recursos que cambian de lugar con un patrón, o que solo se pueden encontrar recordando. Primero se pregunta si la memoria evoluciona por razones individuales. Una memoria ya establecida podría después ser reclutada para diferenciar roles (exaptación). Este eje apunta además directamente a la pregunta de fondo del proyecto: la emergencia de inteligencia.
