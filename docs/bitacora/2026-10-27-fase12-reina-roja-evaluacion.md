# 2026-10-27 · Fase 12, etapa 4: depredación evolucionada, evaluación

Prerregistro: [2026-10-27-fase12-reina-roja-prerregistro.md](2026-10-27-fase12-reina-roja-prerregistro.md). Informe: `runs/fase12/reina_roja_prerregistro_informe.json`.

## Resultado: negativo en todas las reglas
| # | Regla | Resultado |
|---|---|---|
| R1 | tasa de mutación `ataque` > `sin` | **No** (n = 3 pares; diferencias −0,0010, −0,0059, −0,0006) |
| R2 | perfiles distintos `ataque` > `sin` | **No** (−0,05, −8,0, −3,4) |
| R3 | extinciones de `ataque` ≤ 2/8 | **No: 5/8** (`fijo` 1/8, `sin` 1/8) |
| R4 | tasa de mutación `ataque` > `fijo` | **No** (p = 0,5) |

- **Extinciones con ataque:** semillas 21, 24, 25, 26 y 27, entre los pasos 30 894 y 61 652. Justo antes, el gen de atacar estaba en el 77–100 % de la población.
- **Las 3 sobrevivientes** (22, 23 y 28) son monocultivos de depredadores: el gen está en el 99–100 %, se usa ~3 % del tiempo, y la tasa de mutación es baja (0,0007–0,009).
- **Exploratoria:** el genoma es algo más grande con ataque (+0,2 a +5,3 genes; p = 0,125).
- Los controles también tienen una extinción cada uno, en el mismo tramo. La rampa de toxicidad termina en el paso 30 000, y el ataque se suma a ese momento crítico.

## Diagnóstico
- **No se forman especies de presa y depredador.** Todos descienden de LUCA y son casi idénticos: un depredador ataca a sus propios parientes, y la estrategia que se impone es "todos un poco caníbales".
- **No hay carrera armamentista** porque no hay nada que mejorar de un lado que el otro tenga que contrarrestar. La única defensa física son los enlaces, y no se usan.
- **El sensor de similitud** (que compara etiquetas) permitiría no atacar a los parecidos, pero la evolución no lo encuentra.
- **El 4/4 sin extinciones del barrido** (120 000 pasos, semillas 1–4) era optimismo de pocas semillas y horizonte corto: la lección 3 otra vez.

## Qué haría falta (diseño, no probado)
Para que haya Reina Roja hacen falta **dos nichos** y un **compromiso** que impida ser bueno en ambos:
- **Especialización trófica,** física igual para todos: lo que se gana atacando se multiplica por la "maquinaria" de atacar (promedio móvil de su uso, como la maquinaria por uso de la fase 5), y lo que se gana comiendo, por la de comer. Un generalista rinde poco en las dos cosas. Así aparecen presas que comen y depredadores que atacan, y atacar a un depredador (que no se especializó en comer) no rinde lo mismo que atacar a una presa.
- **Defensa con grados de libertad:** que la presa pueda evolucionar algo que el depredador tenga que contrarrestar. Por ejemplo, una etiqueta que el atacante debe "reconocer" para que el ataque rinda, y que la presa puede cambiar.
- **Control:** el mismo mundo con la maquinaria apagada (γ = 0).

## Especialización trófica, exploratoria 1 (2026-10-27): artefacto de la física
- **Corrida:** `reina_roja.py --condiciones ataque`, semillas 1–4, 150 000 pasos, `fisica.maquinaria_gamma=1`, `ataque.especializacion_gamma=1`.
- **Lo que se vio:** 4 de 4 vivas, pero con la grilla **llena** (16 384 organismos). El 95 % son depredadores, que atacan el 30–47 % del tiempo y casi no comen (uso de comer ~0,01). No hay separación de nichos: depredadores y presas comen igual.
- **Causa (un error del diseño):** el factor de especialización tenía tope `maquinaria_max = 2,5`. Con eficiencia 0,6, un depredador habitual ganaba 1,5 veces lo que le quitaba a la víctima: **atacar creaba energía**. Una población que se ataca entre sí se alimentaba sola, como una máquina de movimiento perpetuo. No es un resultado biológico.
- **Corrección:** el factor tiene ahora tope 1. La especialización solo castiga al que ataca poco, y atacar nunca rinde más de lo que quita (test actualizado). La exploratoria se repite con la corrección y con el control γ = 0 (`runs/fase12/rr_especializacion_v2.json` y `_g0.json`).
- **Lección:** toda regla que multiplica una transferencia de energía entre organismos tiene que respetar la conservación (ganancia ≤ lo quitado). Agregarlo a los chequeos de diseño.
