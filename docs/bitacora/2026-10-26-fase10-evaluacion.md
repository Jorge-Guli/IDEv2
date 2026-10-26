# 2026-10-26 · Fase 10: peldaños para la memoria, evaluación

Prerregistro: [2026-10-26-fase10-prerregistro.md](2026-10-26-fase10-prerregistro.md). Informe: `resultados/fase10/informe.json`. Series y poblaciones finales de `sem_induccion` en `resultados/fase10/`.

## Corrida
`experiments/fase10/evaluar.py`, 300 000 pasos, semillas 181–188, 4 condiciones (48 minutos en la PC del autor).

**Extinciones:**
| Condición | Extintas |
|---|---|
| `sem_induccion` | 1 de 8 |
| `ruido_induccion` | 4 de 8 |
| `luca_induccion` | 4 de 8 |
| `sem_cerrojo` | 0 de 8 |

Casi todas ocurrieron entre los pasos 25 000 y 38 000.

## Hipótesis
| # | Regla | Resultado |
|---|---|---|
| **P1** | seguimiento de `sem_induccion` > 0,3 en ≥ 4 de 8 | **Sí**: 6 de 7 sobrevivientes (0,48–0,51); la otra (182) evolucionó el atajo del tipo de comida |
| P2 | seguimiento `sem_induccion` > `ruido_induccion` | **No formalmente:** n = 4 pares por las extinciones del control, con las 4 diferencias positivas (+0,40 a +0,51). p = 0,0625 es el mínimo posible con 4 pares |
| P5 | seguimiento `sem_induccion` > `sem_cerrojo` (sin inducción) | **Sí** (7 de 7 positivas, p = 0,008) |
| **P3** | acierto `sem_induccion` > `ruido_induccion` | **No** (las 4 diferencias son negativas) |
| P4 | acierto `sem_induccion` > 0,6 en ≥ 4 | **No** (0,51–0,55) |
| P6 | seguimiento de `luca_induccion` > 0,3 en ≥ 4 | **No** |

## Lectura

### 1. Primera memoria evolucionada del proyecto
Con un primer peldaño premiado (digestión inducible), el gen de memoria sembrado se sostiene ~1750 generaciones y codifica la estación en 6 de 7 poblaciones.

**Genomas finales:** peso mediano de ~19–20 sobre la pista y ~0 sobre el tipo de comida. Es memoria de la pista, no el atajo.

**Precisión:** en la población 188, sin mutación, el **99–100 %** de los organismos tiene la memoria acorde a la estación. Tras cada cambio de estación se actualiza en menos de 250 pasos.

**Nota sobre la métrica:** el seguimiento se mide cada 500 pasos, y una de cada cuatro mediciones cae justo en el cambio de estación, cuando la memoria todavía es la anterior. Por eso **0,5 es el máximo práctico**: los valores observados (0,48–0,51) equivalen a una memoria casi perfecta.

Sin el peldaño (`sem_cerrojo`), el gen se pierde en las 8 semillas, como en la fase 9. Es lo que predice Lenski et al. (2003): **la función evoluciona cuando su primer paso tiene premio propio**.

### 2. La memoria no se recluta para la conducta
- **Acierto:** no sube. Los únicos genes "condicionados" que aparecieron dependen de la memoria B, que nadie escribe; se expresan siempre (deriva neutral).
- **El segundo peldaño no se premia.** Se agregó el módulo de conducta condicionada (comer y avanzar según memoria y tipo) a las poblaciones evolucionadas, compitiendo contra un control con los mismos genes en cero, sin mutación, 20 000 pasos, 4 poblaciones × 2 semillas:

  | Módulo | Con inducción | Sin inducción |
  |---|---|---|
  | Completo | gana 1 de 8 | gana 0 de 8 |
  | Solo avanzar | gana 2 de 8 | gana 0 de 8 |
  | Un gen de avanzar | gana 2 de 8 | — |

  Que también pierda sin inducción descarta que la inducción sustituya a la conducta.
- **Diagnóstico (población 188):**
  - el mutante come mucha menos comida mala (0,04 contra 0,17 de las acciones), pero también menos buena (0,12 contra 0,19);
  - el 52 % de sus acciones son giros y volteretas;
  - **causa:** un gen condicionado aporta como mucho ±1, y los genes evolucionados de comer y avanzar ya están saturados en ±1 (pesos ~20 sobre "recurso aquí"). Sobre la comida mala, el módulo deja comer y avanzar empatados en ~0, y gana otra acción: el organismo da vueltas en lugar de irse;
  - sobre LUCA, con genes más débiles, el mismo módulo ganaba siempre (fase 9).
- **El valle del segundo peldaño es de magnitud:** para torcer una decisión saturada hacen falta varios genes condicionados a la vez.

### 3. Efecto colateral de la inducción: las extinciones de los controles
Sin memoria, la memoria queda fija (en 0) y el estado digestivo termina preparado siempre para el tipo B. En promedio es neutro: más nutrientes y más veneno en una estación, menos en la otra. Pero **aumenta la varianza**: en la estación A se absorbe un 25 % más de veneno.

Al terminar la rampa de toxicidad (paso 30 000), las poblaciones sin memoria de pista colapsan en las malas rachas. Eso explica las extinciones de `ruido_induccion` y `luca_induccion` (4 de 8 cada una), y la falta de potencia de P2.

Para próximas versiones: que un estado digestivo sin información sea neutro en cada estación (por ejemplo, que la inducción actúe solo cuando la memoria está lejos de 0,5, con la memoria inicial en 0,5).

## Qué queda establecido
1. **Memoria funcional evolucionada y sostenida**, cuando el primer peldaño se premia (P1 y P5; P2 en la dirección esperada).
2. **La evolución vuelve a buscar atajos** (escribir la memoria con el tipo de comida), y hay que bloquearlos con física y verificarlos con duelos directos.
3. **El reclutamiento de la memoria para la conducta** choca con un valle de magnitud: un gen condicionado no alcanza para torcer decisiones que los genes evolucionados ya saturan.

## Decisión: fase 11, modulación por el estado interno
- **Propuesta:** en lugar de (o además de) encender y apagar genes, que un gen pueda tener su **entrada modulada por la memoria**. Una condición nueva haría que el aporte de los sensores del gen cambie de signo según la memoria A (z = b + (2m_A − 1)·w·s).
- **Efecto:** un solo gen, "comer con peso +5 sobre el tipo de comida, modulado", implementa "en la estación A comé A, en la B comé B": la combinación que hasta ahora exigía varios genes coordinados. En biología corresponde a la neuromodulación y a los receptores cuya respuesta depende del estado interno.
- **Antes de correr:** verificar con competencias, sobre poblaciones evolucionadas con memoria (las de esta fase), que un gen modulado de comer o avanzar invade.
- **Arreglo de diseño:** corregir la asimetría de la inducción (estado digestivo neutro sin información).
