# 2026-10-26 · Fase 9: regulación condicionada, evaluación

Prerregistro: [2026-10-26-fase9-prerregistro.md](2026-10-26-fase9-prerregistro.md). Informe: [2026-10-26-fase9-informe.json](2026-10-26-fase9-informe.json). Series por corrida en `resultados/fase9/`.

## Corrida
`experiments/fase9/evaluar.py`, 300 000 pasos, semillas 171–178, 4 condiciones (32 corridas, 69 minutos en la PC del autor). No hubo extinciones: la rampa de toxicidad cumplió su función.

| Condición | Acierto final | Generaciones | Con gen de memoria | Con gen condicionado | Seguimiento |
|---|---|---|---|---|---|
| `sem_info` | 0,540 | 1824 | 0,12 | 0,92 | 0,010 |
| `sem_ruido` | 0,542 | 1662 | 0,00 | 0,84 | 0,000 |
| `sem_sin_reg` | 0,537 | 1875 | 0,00 | 0 | 0,000 |
| `luca_info` | 0,540 | 1652 | 0,01 | 0,89 | 0,000 |

## Hipótesis
| # | Regla | Resultado |
|---|---|---|
| **R3** | acierto `sem_info` > 0,6 en ≥ 4 semillas | **No** (máximo 0,551) |
| R1 | `sem_info` > `sem_ruido`, p < 0,05 | **No** (diferencias −0,011 a +0,003; p = 0,88) |
| R2 | `sem_info` > `sem_sin_reg`, p < 0,05 | Formalmente **sí** (p = 0,004), pero el efecto es de +0,004 y **no pasa por la memoria** (ver abajo) |
| R4 | acierto `luca_info` > 0,6 en ≥ 4 semillas | **No** (máximo 0,554) |

## Lectura
1. **La memoria no se usa.**
   - **Pérdida del gen:** el gen de memoria sembrado se pierde en 7 de 8 semillas de `sem_info`, y en todas las de los controles. El seguimiento queda en ~0 en las cuatro condiciones.
   - **La única excepción, la semilla 176 de `sem_info`,** conserva el gen casi todo el tiempo, pero su memoria es casi constante: el seguimiento vale 0,08 y la alineación da entre −0,1 y −0,27 en ambas estaciones.
   - Su acierto oscila con la estación (≈ 0,57 en A y ≈ 0,54 en B): es un sesgo hacia un tipo de comida, no un recuerdo.
2. **R2 no se lee como éxito.**
   - **Mecanismo:** perdido el gen de memoria, la memoria de cada linaje queda congelada en el valor heredado. Entonces una condición equivale a "gen encendido" o "gen apagado" de forma heredable: un **interruptor genético barato** (silenciamiento).
   - Eso da una ventaja mínima (+0,004 de acierto, 8 de 8 a favor), consistente con la mayor flexibilidad del genoma.
   - Los genes condicionados se difunden en casi todas las poblaciones (84–92 %), incluso con la pista aleatoria. Son útiles, pero no como memoria.
3. **Coincide con los pilotos y con la literatura** ([estado del arte](../05-estado-del-arte.md)):
   - el camino gradual existe (memoria → avanzar condicionado → comer condicionado), pero su primer paso no se premia;
   - Lenski et al. (2003) mostraron en Avida que una función compleja evoluciona solo si sus peldaños también se premian.
   - En unas 1800 generaciones, ni la regulación ni la siembra del gen alcanzan.

## Qué queda establecido (fases 6–9)
- **El mundo mosaico premia la memoria:** un módulo armado a mano gana siempre.
- **La evolución desde LUCA no la encuentra en ~2000–3000 generaciones,** ni con regulación condicionada ni sembrando el gen.
- **El cuello de botella ya no es representar la regla:** con condiciones, la regla cabe en genes simples. Lo que falta es **el primer peldaño**. Una memoria que sigue a la pista no da nada mientras nadie la usa, y además se borra por deriva: un sesgo pequeño se integra en cada paso.
- **Un hallazgo lateral:** los genes condicionados funcionan como interruptores heredables y se difunden. Pueden servir cuando haya estados internos estables (por ejemplo, la diferenciación celular en grupos).

## Decisión: fase 10, peldaños para la memoria
Se prueban dos cambios por separado, cada uno con su control, en la física (no en el genoma) y fijos para todos:
1. **Memoria tipo cerrojo:** la memoria cambia solo ante impulsos de magnitud mayor que un umbral (zona muerta). Un gen de memoria imperfecto deja de borrar lo recordado, como pasa en los Markov Brains. Ataca la deriva del primer peldaño.
2. **Rampa de la pista (currículo):**
   - la pista empieza frecuente (por ejemplo, p = 0,2) y baja hasta 0,01 durante la corrida;
   - con pistas frecuentes, un módulo memoria + gen condicionado sirve aunque la memoria sea mala, porque se renueva todo el tiempo;
   - a medida que las pistas escasean, se selecciona una memoria que dure.

   Es el mismo principio de la rampa de depredación (fase 2c, que funcionó) y de los peldaños de Avida.

Antes de pedir corridas largas: competencias de invasión y pilotos locales que verifiquen que cada peldaño se premia (lección de las fases 3 y 7).
