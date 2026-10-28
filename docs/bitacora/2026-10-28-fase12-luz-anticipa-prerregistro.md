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
