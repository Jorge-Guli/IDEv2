# 2026-10-26 · Fase 10: peldaños para la memoria, prerregistro

Escrito antes de correr. Antecedentes: [fase 9](2026-10-26-fase9-evaluacion.md) y [estado del arte](../05-estado-del-arte.md). En la fase 9, el camino hacia la memoria existía, pero su primer paso no se premiaba: una memoria que sigue a la pista no da nada mientras nadie la usa, y se pierde. En Avida, una función compleja evoluciona solo si sus peldaños también se premian (Lenski et al. 2003).

## Cambios en la física (fijos e iguales para todos; apagados por defecto)
- **Memoria tipo cerrojo** (`memoria.umbral = 0,5`): los impulsos de memoria chicos no la mueven.
- **Rampa de la pista** (`estaciones.p_pista_inicial`, `rampa_pista`): la pista empieza frecuente y se vuelve rara.
- **Digestión inducible** (`estaciones.induccion = 0,25`):
  - un estado digestivo d sigue a la memoria A con inercia (`inercia_digestion = 100` pasos): d ← d + (m_A − d)/100;
  - lo absorbido de la comida de tipo t (nutrientes y veneno) se multiplica por 1 + 0,25·(2d − 1)·t;
  - una memoria que sostiene la estación digiere mejor la comida buena y absorbe menos veneno de la mala. Es un premio de primer orden para el primer peldaño;
  - el genoma sigue decidiendo si la memoria se escribe y cómo;
  - idea sugerida por una revisión externa ("utilidad metabólica directa del estado interno").

Con todo apagado, las huellas de referencia no cambian.

## Pilotos (semillas 1001–1002, 150 000 pasos; no entran en la evaluación)
1. **Cerrojo, rampa y ambos juntos:** sin efecto. El gen de memoria se pierde y el acierto queda en 0,52–0,55, como en la fase 9.
2. **¿La inducción premia el primer peldaño?** Competencia del gen de memoria solo (memoria A ← pista) contra LUCA con el mismo gen en cero:
   - con inducción 0,25 gana en 7/7 semillas con sobrevivientes, y con 0,5 en 8/8;
   - sin inducción, 2/5 (azar). **Sí.**
3. **Primer atajo (inducción sin inercia):**
   - la memoria evolucionó escrita con el tipo de comida de la celda: "prepara" la digestión de lo que tiene debajo, sin recordar nada;
   - **se mantuvo también con la pista aleatoria y desde LUCA.** Se agregó la inercia digestiva;
   - con inercia, el atajo todavía le gana a un control sin memoria (ventaja chica, amplificada en la competencia). En un **duelo directo** (memoria de pista contra memoria de tipo), la de pista gana en 7/7 (inercia 100) y 6/6 (inercia 500).
4. **Piloto evolutivo con inducción e inercia 100:**
   - en `sem_induccion`, semilla 1001, **la memoria sigue a la estación durante toda la corrida.** El seguimiento vale 0,46, el gen tiene peso 20 sobre la pista y −0,15 sobre el tipo de comida, y lo lleva el 89 % de la población. Es la primera memoria funcional que se sostiene en el proyecto;
   - el acierto no subió (0,525): todavía no se usa para decidir qué comer;
   - en la semilla 1002 se perdió;
   - desde LUCA y con la pista aleatoria evolucionó el atajo del tipo de comida.

## Diseño
- `python experiments/fase10/evaluar.py`.
- **Mundo:** el de la fase 9 (mosaico, castigo 0,2, toxicidad diferida con rampa de 30 000 pasos, pista 0,01, estaciones de 2000 pasos, sin aprendizaje, regulación condicionada), con cerrojo en todas las condiciones.
- **Duración:** 300 000 pasos; semillas nuevas 181–188.
- **Condiciones:**
  - `sem_induccion`: LUCA + gen de memoria conectado a la pista, con inducción;
  - `ruido_induccion`: igual, con la pista aleatoria (control: la memoria no puede seguir a la estación);
  - `luca_induccion`: LUCA puro, con inducción;
  - `sem_cerrojo`: como `sem_induccion`, sin inducción (control del peldaño).

## Hipótesis y reglas (las calcula el script)
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| **P1** | Con un peldaño premiado, la memoria se sostiene y sigue a la estación | seguimiento de `sem_induccion` > 0,3 en ≥ 4 de 8 | Moderada (1 de 2 en el piloto) |
| P2 | Ese seguimiento viene de la pista | seguimiento `sem_induccion` > `ruido_induccion`, pareada, p < 0,05 | Moderada |
| P5 | Y requiere el peldaño | seguimiento `sem_induccion` > `sem_cerrojo`, pareada, p < 0,05 | Moderada |
| **P3** | La memoria se usa para decidir (segundo peldaño: conducta condicionada) | acierto `sem_induccion` > `ruido_induccion`, pareada, p < 0,05 | Baja |
| P4 | Uso fuerte | acierto de `sem_induccion` > 0,6 en ≥ 4 de 8 | Baja |
| P6 | Todo desde LUCA | seguimiento de `luca_induccion` > 0,3 en ≥ 4 de 8 | Baja (en el piloto ganó el atajo) |

Notas:
- El acierto mide la comida elegida (buena o mala), no lo que se absorbe. La inducción por sí sola no lo cambia, así que una subida del acierto exige conducta.
- El seguimiento es la covarianza entre la memoria y la estación en la ventana final (corregida en la fase 9).

## Cómo se interpretará
- **P1, P2 y P5:** **un peldaño premiado basta para que la memoria evolucione y se sostenga**, como predice Lenski et al. (2003). Es la primera memoria evolucionada del proyecto.
- **P3:** además se recluta para la conducta, una cognición mínima: decidir con información que ya no está presente. Seguiría la ablación (fijar la memoria y medir la caída del acierto).
- **P1 sin P3:** la memoria existe, pero el segundo peldaño (conducta condicionada) no se cruza en ~2000 generaciones. Seguiría verificar con competencias si ese peldaño ya se premia, con la memoria presente.
- **Negativo en P1:** el premio metabólico no alcanza contra la deriva y el costo en poblaciones que evolucionan, aunque gane en competencias. Habría que revisar la intensidad (0,5) o la inercia.
