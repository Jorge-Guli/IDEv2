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
