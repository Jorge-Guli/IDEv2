# 2026-10-30 · Fase 13: red regulatoria (prerregistro del piloto)

## Pregunta
Si cada célula tiene una red de genes que se encienden y apagan entre sí, con señal por contacto entre células pegadas (peldaños 1 y 2 del desarrollo), ¿la evolución la usa? ¿Aparecen dentro de los grupos células del mismo linaje en estados distintos, es decir, tipos celulares?

## Diseño
- **Universo (versión final): `natural.toml`.** Sin fuerzas diseñadas:
  - clima real de Capitán Bermúdez, que regula el crecimiento de la comida y el costo de vivir;
  - sin depredador externo ni estaciones artificiales;
  - la depredación solo existe si evoluciona: la primitiva `atacar` está disponible para el genoma, pero LUCA no la tiene;
  - el genoma también puede ganar asociarse (movimiento por fuerza, α = 0,5), percibir el rumbo de los socios y usar la red regulatoria.

  Se elige una vez y no se toca (principio 7).
- **Segunda corrección (2026-10-30, a pedido del autor):** las dos versiones anteriores usaban el depredador externo de las fases 2c–3, que aparece de la nada y se come a los sueltos. Es una fuerza diseñada, contraria al principio 7: en la naturaleza la depredación surgió de la propia población cuando escaseó la comida. Se detuvo sin evaluar ninguna medida. Prueba de funcionamiento (2 000 pasos, semilla 1): ~1 300 organismos, y a los 1 000 pasos el 32 % ya tiene el gen de atacar.
- Lo que sigue en esta lista (la corrección de las 11:20) queda como registro de la versión anterior.
- ~~Universo: el de la fase 2c (`depredacion.toml`)~~, con un depredador que solo come sueltos desde el paso 2000. Se le sumaba el movimiento de grupo por fuerza (α = 0,5) adoptado en la fase 3c.
- **Corrección antes de medir (2026-10-30, 11:20):** el primer lanzamiento usó el universo de la fase 3 (`coordinacion.toml`). Ese universo extingue a LUCA (semilla 5 en el paso 864), porque el depredador actúa desde el paso 0. En la fase 3 se usó con poblaciones ya evolucionadas. Se detuvo sin mirar ninguna medida de la red.
  - **Prueba de viabilidad:** 20 000 pasos, red inerte, semillas 1 y 2. En el universo 2c sobreviven las dos variantes de movimiento: con empuje, 852 y 891 organismos y 2–3 % en grupos de 3 o más; con fuerza, 586 y 667 organismos y 5–14 %.
  - Se elige fuerza: es el movimiento adoptado en la fase 3c y forma los grupos de 3 o más donde se mide la diferenciación. Los criterios no cambian.
- **Desde LUCA:** la red empieza con todos sus pesos en 0; LUCA no la usa.
- **Parámetros de la red:** los de fábrica (`tasa = 0,2`, `asimetria = 0`). No se ajustan según el resultado.
- **Condiciones:**
  - **red:** los genes leen la red;
  - **inerte (control):** la red existe, muta y cambia de estado igual, pero los genes no la leen. Lo que muestre es pura deriva.
- **Semillas:** 1–6, emparejadas. **Pasos:** 300 000. Salida `runs/fase13/piloto.json` (script `experiments/fase13/piloto.py`).
- Medición en el último tercio (desde el paso 200 000), promedio de los registros cada 1 000 pasos.

## Criterios (prueba de permutación pareada exacta, una cola)
| | Medida | Cumple si |
|---|---|---|
| **P1, uso** | `con_gen_regulado`: fracción de organismos con un gen que lee la red con peso > 0,5 | red − inerte > 0, p ≤ 0,05 |
| **P2, diferenciación** | desvío del estado regulatorio dentro de los grupos de 3 o más, dividido por el de la población | red − inerte > 0, p ≤ 0,05 |

**Exploratorias** (sin umbral):
- dispersión de roles dentro de los grupos y correlación entre el estado y el rol;
- población y extinciones;
- si evoluciona la depredación (`tiene_atacar`, `usa_atacar`, `frac_depredadores`) y la asociación (`frac_enlazados`, `grupos_de_3_o_mas`).

## Qué significaría cada resultado
- **P1 y P2:** la evolución adopta la red y la usa para diferenciar células dentro del grupo. Es el primer tipo celular, y se sigue a la fase siguiente: el cuerpo como unidad que se reproduce.
- **P1 sin P2:** la red se usa, pero como memoria individual, no para diferenciar.
- **Ninguno:** en este universo la red no paga. Se registra como dato y no se retoca el universo (principio 7). El paso siguiente sería el que la naturaleza dio antes de los tejidos: el cuerpo como unidad de reproducción, que alinea los intereses de las células.

## Resultado (2026-10-30, 14:14): ninguno de los dos criterios se cumple
12 corridas de 300 000 pasos (~5 600–10 400 generaciones), **0 extinciones**. Medido desde el paso 200 000.

| | red | inerte | Resultado |
|---|---|---|---|
| **P1** `con_gen_regulado` | 1,0 en las 6 | 1,0 en las 6 | diferencias 0, p = 1,0: **no cumple** |
| **P2** diferenciación relativa | medible en 2 semillas | medible en 2 semillas | solo 1 par comparable, p = 0,5: **no evaluable** |
| población media | 652–1 047 | 572–1 038 | p = 0,33 |

**Por qué falla P1:** la medida se satura. Los pesos que leen la red mutan en todos los genes activos, y por deriva alguno supera 0,5 enseguida, incluso donde nadie los lee. El umbral se fijó sin ver cuánto deriva el control. Queda como lección: medir el uso contra la deriva del control, no con un umbral absoluto.

**Por qué P2 no se puede evaluar:** casi no hay grupos de 3 o más (≤ 0,6 % de los organismos en 11 de 12 corridas). Sin grupos no hay dónde diferenciarse.

**Exploratorias (sin prerregistrar, solo indicios):**
- **La red se poda.** El peso medio con que los genes leen la red es menor en la red que en el inerte en las 6 semillas (0,34–0,49 contra 0,50–0,61; p = 1/64 en la dirección contraria a la predicha, calculado después de ver los datos). En el inerte los pesos derivan libres; en la red la selección los achica. Leer la red, tal como está, estorba más de lo que sirve.
- **La depredación evoluciona sola** (principio 7 en acción): a los 1 000 pasos la tiene el 61–81 % de los organismos, y a los 20 000, todos. Del 50 al 70 % ha comido a otro y ~11 % ataca en cada paso. Nadie la programó: surgió al escasear la comida.
- **La asociación desaparece.** Los enlazados llegan al 15 % a los 5 000 pasos y caen a 0 en la red; en el inerte se sostienen ~10 %, pero casi todo en una semilla (la 6, con 64 %). Con depredadores por todos lados, pegarse a otro no rinde, o el socio termina siendo comida.
- La población oscila entre ~530 y ~1 700 siguiendo el clima real y la depredación, sin extinguirse.

**Lectura:**
- En este universo, la red regulatoria no paga todavía.
- El cuello de botella de la diferenciación no es la red: es que **no hay cuerpos**. Las células no se quedan juntas, así que no hay dónde ser distintas.
- Es lo previsto en "Ninguno": el paso que sigue es el que la naturaleza dio antes de los tejidos, **el cuerpo como unidad que se reproduce**: la célula se divide, la hija queda pegada y el grupo nace de una sola célula.
- No se toca el universo (principio 7).
