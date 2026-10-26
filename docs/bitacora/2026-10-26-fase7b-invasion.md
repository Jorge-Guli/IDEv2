# 2026-10-26 · Fase 7b: ¿el mundo de la fase 7 premia una memoria bien usada? (prueba de invasión, exploratoria)

Script: `experiments/fase7/invadir_memoria.py`.
- **Residentes:** la población evolucionada en el piloto de la fase 7 (toxicidad diferida, sin aprendizaje, con memoria).
- **Siembra:** 600 organismos: 60 % residentes, 20 % mutante diseñado a mano y 20 % control marcado (los mismos genes extra, sin conexión).
- **Corrida:** sin mutación ni aprendizaje, memoria con tasa 1, 8 semillas, 20 000 pasos.

## El mutante (cinco genes)
- **memoria_a = 20 · pista:** la pista fija la memoria.
- **Dos genes de comer:** suman ≈ 0 si el tipo de comida coincide con la memoria y ≈ −2 si no (inhiben comer la comida fuera de estación).
- **Dos genes de avanzar:** suman ≈ +2 si el tipo no coincide (irse a buscar el otro).

## Problemas de diseño encontrados y corregidos en el camino
1. **Con solo los genes de comer,** el mutante dejaba de comer la comida mala pero no se iba: giraba en el lugar y moría de hambre. Se agregaron los genes de avanzar.
2. **El mutante arrancaba con la memoria en 0** ("estación B") durante la estación A: evitaba la comida buena y moría antes de su primera pista. Ahora arranca con la memoria de la estación vigente.
3. **Laguna en la física:** al dividirse, el veneno pendiente se quedaba con el progenitor y el hijo nacía limpio. Ahora se reparte como la energía (con test).

## Resultado
El mutante **se extingue en las 8 semillas**, con castigo 0,5 y también con castigo 2,0 (el doble de costo neto por comer tóxico). Con castigo 2,0, en 2 semillas se extinguió la población entera.

Seguimiento detallado (castigo 0,5): el mutante evita el veneno (veneno pendiente ≈ 0) y se concentra en celdas del tipo bueno (96 %), pero **ahí la comida está agotada**, porque todos van a ella. El mutante rechaza la mitad de la comida del mundo y termina con la mitad de la energía del control (10 contra 20).

## Lectura
En este mundo, **ser selectivo no paga**: el costo de renunciar a la mitad de la comida, en un mundo donde la comida escasea, supera al del veneno. Por eso la memoria no evolucionó en la fase 7, y el problema no era la expresividad del genoma. Es la misma lección de la fase 3b: antes de pedirle a la evolución que encuentre algo, hay que verificar que el mundo lo premie.

## Decisión
Rediseñar el mundo para que recordar pague. Condiciones a verificar con una prueba de invasión **antes** de cualquier corrida larga:
- comida suficiente del tipo bueno (por ejemplo, un tipo abundante cada vez);
- un costo del error grande frente al de buscar;
- que la información no se pueda obtener de otra forma.
