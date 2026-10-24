# 2026-10-24 · Exploración previa a la fase 4: ciclo de vida de los grupos

Exploración (no prerregistrada) para diseñar la fase 4 (el colectivo como individuo). Script: `experiments/fase4/ciclo_de_vida.py`.
- **Población:** evolucionada 30 000 pasos con movimiento por fuerza (α = 0,5), rumbo y señales (piloto de la fase 3c, semilla 301).
- **Mundo:** 600 genomas sembrados con refugio 3, sin mutación; 1000 pasos de formación y 2000–3000 pasos de registro.
- El script sigue la identidad de cada grupo paso a paso, por solapamiento de miembros, y registra cómo se funda.

## Cómo nacen los grupos
| Fundación | Todos los grupos | Grupos que llegan a 3 o más |
|---|---|---|
| **división** (un suelto se divide quedando unido) | 93 % | **84 %** |
| fisión (fragmento de un grupo) | 5 % | 8 % |
| unión de sueltos | 2 % | 8 % |

- Duración mediana: 45 pasos (todos) y 238 pasos (grupos que llegan a 3 o más).
- **Los grupos se desarrollan de forma clonal desde una sola célula:** es un ciclo de vida con cuello de botella unicelular, como el de muchos organismos multicelulares.

## Cómo se reproducen
Origen de los sueltos nuevos (2000 pasos):
- 4081 nacen de un padre que está en un grupo (división libre);
- 5890 se desprenden de un grupo (muerte de un socio, ruptura);
- 186 nacen de un padre suelto.

Cada suelto funda un grupo nuevo dividiéndose unido (los sueltos eligen esa acción en el 20 % de los pasos). **El grupo se reproduce con propágulos unicelulares.**

## Heredabilidad del tamaño
Correlación entre el tamaño máximo del grupo padre y el del hijo:
- r = 0,23 por fisión (n = 368);
- r = 0,06 desde un fundador unicelular (n = 3571).

El tamaño del grupo casi no es un rasgo heredable del grupo.

## Diferenciación dentro de los grupos
- **Conducta:** borde (1 socio) e interior (3 socios) hacen casi lo mismo: ~37 % comer, ~32 % avanzar, ~15 % girar. El interior descansa algo más (5–8 % contra 3 %). **No hay división del trabajo.**
- **Energía:** el interior tiene menos que el borde (11–15 contra 15–19) y el coeficiente de variación dentro de los grupos de 3 o más es 0,32. Hay desigualdad, pero compartir no evolucionó (gen presente en ~1–2 %).

## Lectura
- La teoría de la división del trabajo en las transiciones a la multicelularidad (Michod 2006; Koufopanou 1994) predice que la especialización aparece cuando hay un **compromiso con retornos crecientes** entre dos funciones, y los grupos son clonales.
- La clonalidad ya está: 84 % de los grupos nacen de una célula. Lo que falta es el compromiso: en esta física, una célula reparte sus pasos entre comer y empujar de forma lineal, y un generalista rinde lo mismo que un especialista.
- **El ejemplo biológico mejor documentado es la restricción flagelar** de las algas volvocales: una célula no puede dividirse y moverse a la vez, porque al dividirse pierde temporalmente los flagelos. En *Volvox*, eso favoreció la separación entre células somáticas, que nadan y no se dividen, y germinales, que se dividen y no nadan.
