# 2026-10-24 · Fase 3b: prueba de invasión de un mutante coordinado, prerregistro

Escrito antes de correr la evaluación. Es un experimento diagnóstico, como el experimento E, sin física nueva: no tiene cambio de OpenSpec. Antecedente: [`2026-10-24-fase3-evaluacion.md`](2026-10-24-fase3-evaluacion.md).

## Pregunta
En la fase 3, la percepción del rumbo de los socios hizo evolucionar la alineación, pero los grupos no crecieron. La revisión mostró que el genoma actual ya puede sincronizar un trío: basta con "seguir al que empuja". **¿La física premia esa coordinación cuando el depredador exige tríos?**
- Si un mutante coordinado diseñado a mano invade, lo que faltó en la fase 3 fue tiempo o accesibilidad evolutiva.
- Si no invade, la ecología no premia a los tríos coordinados, y cambiar la regla de movimiento pasa a ser una decisión de modelo.

## Diseño (`experiments/fase3b/invadir.py`)
- **Ancestros:** iguales a los de la fase 3 (LUCA, 30 000 pasos en la ecología de la fase 2c), con semillas nuevas, 51–60.
- **Siembra:** 600 genomas del ancestro: 60 % residentes, 20 % mutante coordinado (cepa 1) y 20 % control marcado (cepa 2).
- **Genes extra:** todos reciben los mismos tres genes con sesgo 0 (girar a la derecha, girar a la izquierda y avanzar), así que el costo genético es el mismo para todos. Solo en el mutante esos genes están conectados a los sensores de los socios:
  - **seguir:** avanzar con 3 · empuje de los socios;
  - **alinear:** girar a la derecha con 4 · seno del rumbo de los socios, y a la izquierda con −4 · seno;
  - **ambos:** los dos anteriores.

  Con sesgo 0 y sensores en 0 (sueltos, socios alineados, nadie empuja), los genes aportan 0.
- **Ecologías:**
  - `refugio3`: el depredador ya escaló; un par se salva de un ataque con probabilidad 1/2 y un trío siempre.
  - `refugio2`: control; un par basta.
- 20 000 pasos, sin mutación (prueba de selección), con aprendizaje y percepción del rumbo activos.
- **Variable principal:** fracción del coordinado = coordinados / (coordinados + control marcado) al final. Si se extinguen las dos líneas, cuenta como que no invade.

## Pilotos (semilla 31, ancestro de la fase 2c; no entran en la evaluación)
- **Primera versión, con sesgos negativos (−1 y −0,6):** los dos mutantes se extinguieron en 300 pasos, el control incluido. El impulso de una primitiva es la suma de las tanh de sus genes, así que un gen con sesgo negativo resta impulso a avanzar y girar aunque nunca gane. Se pasó a sesgo 0.
- **Segunda versión, con genes extra solo en los mutantes:** los dos mutantes desaparecieron por el costo de 3 genes (+0,03 por paso). Se pasó a dar los genes a todos.
- **Variantes, 3000 pasos, refugio 3, 10 % por línea:**

  | Variante | Coordinados (inicio → paso 2500) | Control marcado (inicio → paso 2500) |
  |---|---|---|
  | seguir | 60 → 190 | 60 → 2 |
  | alinear | 60 → 0 | 60 → 0 |
  | ambos a media intensidad | 60 → 0 | 60 → 283 |
  | ambos a media intensidad, siguiendo solo sin comida | 60 → 0 | 60 → 33 |
  | ambos a intensidad completa (versión anterior) | 60 → 0 | 60 → 8 |

  Una semilla y con mucha deriva: solo orienta. Por eso las líneas marcadas suben al 20 % en la evaluación.

## Hipótesis y reglas
| # | Predicción | Regla | Expectativa según los pilotos |
|---|---|---|---|
| **I1** (por variante) | El coordinado invade con refugio 3 | fracción del coordinado ≥ 0,7 en ≥ 70 % de las semillas | seguir: sí; alinear y ambos: no |
| I2 (por variante) | Los grupos de 3 o más del coordinado se mueven más | movilidad del coordinado > control en ≥ 70 % de las semillas | seguir: sí |
| I3 (por variante) | La ventaja depende de que el depredador exija tríos | fracción del coordinado mayor con refugio 3 que con refugio 2 en ≥ 70 % de las semillas | seguir: sí |

## Qué haría cambiar de rumbo
- **Seguir invade y depende del refugio (I1 e I3):** la física premia la sincronía. El techo de la fase 3 es de accesibilidad evolutiva. Siguiente paso: probar si la evolución la encuentra con más tiempo o con más suministro de mutaciones sobre ese sensor.
- **Nada invade:** la ecología no premia a los tríos coordinados. Se diseña una regla de movimiento nueva, con prerregistro, semillas nuevas y la anisotropía corregida.
- **Que la alineación sea perjudicial es informativo:** girar cuesta un paso que no se usa para comer. Eso explicaría por qué en la fase 3 la alineación evolucionó de forma moderada.
