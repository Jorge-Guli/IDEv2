# 2026-10-28 · Fase 12, etapa 3: la luz que anuncia la comida (prerregistro)

## Pregunta
En la versión 2 (`2026-10-27-fase12-luz-prerregistro.md`) la luz hacía crecer comida en el momento. La evolución no la miró (R1, p = 0,42), porque la luz no decía nada que los sensores de comida no dijeran ya. Ahora la luz **anuncia**: la comida crece en el mismo lugar 200 pasos después del pulso. Para entonces, la luz ya se apagó (0,98²⁰⁰ ≈ 0,02). Quien reacciona a la luz (quedarse, volver, no irse) llega antes que quien espera ver la comida.

## Cambio en el motor
- `estimulos.retraso_luz` (por defecto 0, apagado): el recrecimiento lo hace un campo "abono" que recibe los mismos pulsos `retraso_luz` pasos después y se apaga al mismo ritmo.
- El sensor de luz ve la luz al instante.
- Test: `test_la_luz_anuncia_la_comida_con_retraso`. Las huellas de determinismo no cambian.

## Diseño (fijo antes de correr)
- **Mundo, frases y medidas:** los mismos de la versión 2: `clima.toml` (capacidad 20) con estímulos, una frase cada 3000 pasos, y medidas sobre la segunda mitad.
- **Condiciones:**
  - acoplado: `retraso_luz = 200`, acople 0,05.
  - desacoplado: `retraso_luz = 200`, acople 0. Es el control: la misma luz, sin comida.
- **Semillas nuevas 41–48**, 200 000 pasos.
- **Comando:**
  `python experiments/fase12/respuesta_estimulos.py --pasos 200000 --semillas 41 42 43 44 45 46 47 48 --set estimulos.retraso_luz=200 --salida runs/fase12/luz_anticipa.json`

## Reglas (permutación pareada exacta, una cola, α = 0,05)
| Regla | Qué afirma | Criterio |
|---|---|---|
| **R1** | La selección mira la luz cuando la luz anuncia comida | peso_luz acoplado > desacoplado, p < 0,05 |
| R2 | La población está en la luz cuando se enciende | enriquecimiento acoplado > desacoplado, p < 0,05 |

- **Exploratorias:** `E_peso_ruido` (debe no diferir), y el signo del peso de la luz en avanzar y en comer.
- **Validez:** si hay más de 2 extinciones en una condición, el resultado se declara inválido.

### Confusión conocida en R2
Cada letra enciende siempre el mismo lugar. Por eso los lugares de las letras frecuentes reciben comida una y otra vez, y la población puede quedarse en ellos por la historia de la comida, sin anticipar nada. R2 positiva sola no prueba anticipación: **la prueba es R1**.

## Cómo se interpretará
- **R1 positiva con E_peso_ruido nula:** primera evidencia de que la evolución incorpora una señal de afuera que *predice* algo. Es anticipación, un paso hacia la inteligencia que buscamos. Siguiente: ablación del sensor en poblaciones evolucionadas, y probar si el orden de las letras importa.
- **R1 negativa:** con percepción solo local y un genoma sin aprendizaje durante la vida, una señal fugaz que predice comida 200 pasos después puede quedar fuera de alcance. Siguientes opciones: un retraso menor (50) o una luz que dure más.

## Resultado (2026-10-28): válido y negativo
- **Validez:** 0 extinciones en 16 corridas.
- **R1 (peso sobre la luz):** 6 de 8 diferencias positivas (−0,16 a +0,64); p = 0,074. **No se cumple.**
- **E_peso_ruido:** también sube en el acoplado, en 6 de 8 (p = 0,10). La tendencia de R1 no es específica de la luz: los dos pesos derivan juntos, que es lo que hace la deriva cuando cambia la estructura de la población.
- **R2 (enriquecimiento):** p = 0,11. **No se cumple.** Exploratorias de signo (avanzar, comer): nada.
- **Lectura:** ni en el momento (versión 2) ni anunciando la comida, la luz es incorporada por la evolución con este diseño. La confusión prevista para R2 no llegó a importar.
- **Diagnóstico probable (sin probar):** la presión de selección es demasiado débil. Una frase cada 3000 pasos enciende pocas celdas por poco tiempo, así que la comida que trae la luz es una fracción chica de la energía total. Además, los pesos de los sensores derivan con fuerza (|w| ~0,3–0,9 también en el control).
- **Siguiente:** antes de otro prerregistro, **medir cuánta energía aporta la luz** (fracción de lo comido en celdas con abono). Solo si la luz es una parte importante del alimento tiene sentido esperar que la selección la mire. Si no lo es, subir la frecuencia de los estímulos o el acople, verificando primero esa fracción.

## Cuánta comida aporta la luz (medición, 2026-10-28)
- **Cómo se midió:** recrecimiento atribuible al abono sobre el recrecimiento total, semilla 41, pasos 5000 a 30 000, con `retraso_luz = 200` (script de exploración, fuera del repositorio).

| Frase cada | Pasos por letra | Acople | Fracción de la comida que trae la luz |
|---|---|---|---|
| 3000 | 40 | 0,05 | **0,003** (el diseño de las versiones 2 y 3) |
| 500 | 40 | 0,05 | 0,021 |
| 500 | 40 | 0,2 | 0,070 |
| 1000 | 10 | 0,5 | 0,071 |
| 1000 | 10 | 1,0 | 0,126 |
| 500 | 10 | 1,0 | **0,230** |

- **Lectura:** se confirma el diagnóstico. En los dos prerregistros anteriores, la luz traía el 0,3 % de la comida: para la selección, prácticamente nada. Los negativos dicen que la señal era irrelevante, no que la evolución no pueda usarla.

## Repetición prerregistrada (versión 4), escrita antes de correr
- **Mismas reglas R1 y R2, mismas exploratorias, misma regla de validez.**
- **Cambian tres cosas:** `--cada 500`, `estimulos.pasos_por_letra = 10` y `estimulos.acople_luz = 1,0` en el acoplado. El desacoplado sigue con acople 0, porque lo fija la condición después de los ajustes.
- Con eso, la luz trae ~23 % de la comida.
- **Semillas nuevas 51–58**, 200 000 pasos, 6 procesos.
- **Comando:**
  `python experiments/fase12/respuesta_estimulos.py --pasos 200000 --semillas 51 52 53 54 55 56 57 58 --cada 500 --procesos 6 --set estimulos.retraso_luz=200 --set estimulos.pasos_por_letra=10 --set estimulos.acople_luz=1.0 --salida runs/fase12/luz_anticipa_v4.json`
- **Si R1 sigue negativa con la luz como un cuarto de la comida:** el límite está en el organismo (percepción solo local, sin aprendizaje en vida), no en la señal. Ese sería un resultado informativo por sí mismo.

## Resultado de la versión 4 (2026-10-28): R1 negativa, R2 positiva con la confusión prevista
- **Validez:** 1 extinción por condición (acoplado 57 en el paso 155 845, desacoplado 51 en el 72 977). Por debajo del límite: el resultado vale. Pares completos: 6.
- **R1 (peso sobre la luz):** +0,21, +0,18, −0,36, −0,03, +0,22, +0,24; p = 0,22. **No se cumple.**
- **R2 (enriquecimiento):** +1,03, +0,60, +0,50, +0,31, +0,09, −0,07; p = 0,031. **Se cumple.** En el acoplado, la población está en las celdas con luz entre 1,2 y 3,2 veces más de lo que daría el azar (desacoplado: 1,0 a 2,2).
- **Exploratorias:** el ruido no sube (p = 0,98), y los signos sobre avanzar y comer no muestran nada.
- **Lectura, según lo escrito antes de correr:** R2 positiva sola **no prueba anticipación**. Cada letra enciende siempre el mismo lugar, y esos lugares reciben comida una y otra vez. La población puede concentrarse ahí por la historia de la comida (quedarse donde siempre hay) sin leer la luz. R1 nula apoya esa lectura: el genoma no pesa más el sensor de luz. Lo que se observa es que **la población se instala en los lugares donde llega la comida de afuera**, que es una respuesta al mundo, pero no anticipación.
- **Siguiente (diseño):** separar las dos explicaciones con **lugares al azar**, es decir, cada pulso cae en un sitio sorteado con el rng de la simulación. Así la historia no predice nada y solo la luz anuncia la comida. Si R2 y R1 aparecen ahí, es anticipación. Si R2 desaparece, era geografía.

## Versión 5: lugares al azar (prerregistro, escrito antes de correr)
- **Motor:** `estimulos.lugares_al_azar` (por defecto falso). Cada pulso cae en un lugar sorteado con un generador propio, derivado de la semilla y no de la condición: acoplado y desacoplado ven la misma luz en los mismos lugares y pasos. Test: `test_lugares_al_azar_iguales_en_ambas_condiciones`. Las huellas no cambian.
- **Igual que la versión 4,** más `--set estimulos.lugares_al_azar=true`. **Semillas nuevas 61–68.**
- **Comando:**
  `python experiments/fase12/respuesta_estimulos.py --pasos 200000 --semillas 61 62 63 64 65 66 67 68 --cada 500 --procesos 6 --set estimulos.retraso_luz=200 --set estimulos.pasos_por_letra=10 --set estimulos.acople_luz=1.0 --set estimulos.lugares_al_azar=true --salida runs/fase12/luz_azar_v5.json`
- **Reglas, exploratorias y validez:** las mismas. Acá R2 ya no tiene la confusión de la geografía: el lugar no predice nada.
- **Cómo se interpretará:**
  - **R2 positiva:** la población está en la luz cuando se enciende, aunque la luz caiga en cualquier lado. Eso solo pasa si se la busca o se la aprovecha (quedarse al verla): respuesta a la señal.
  - **R1 positiva además:** la evolución lo escribió en el sensor.
  - **R2 negativa:** lo de la versión 4 era geografía.
