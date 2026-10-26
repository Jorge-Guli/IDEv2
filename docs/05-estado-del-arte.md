# Estado del arte: qué sirve de base para simbio

Revisión hecha el 2026-10-26, a pedido del autor, para ver si algún proyecto existente puede acelerar el nuestro. Conclusión corta: **ninguno conviene como reemplazo del motor, pero varios aportan ideas y resultados que ya nos sirven**. El más importante explica por qué la memoria no evoluciona en las fases 8 y 9.

## Proyectos revisados

| Proyecto | Qué es | Estado | Para nosotros |
|---|---|---|---|
| **Avida** (Ofria, Adami, Lenski; MSU) | Programas autorreplicantes en una rejilla; el entorno premia con tiempo de CPU las operaciones lógicas que calculan | C++, [devosoft/avida](https://github.com/devosoft/avida); última versión estable 2.14 (2014); licencia GPL/LGPL según la fuente | Resultados clave (ver abajo). No como motor: el genoma son instrucciones, no reglas sensor→primitiva, y migrar tiraría nueve fases |
| **Symbulation** (Vostinar) | Simbiosis entre hospederos y simbiontes, del parasitismo al mutualismo; transmisión vertical y horizontal | C++ sobre la biblioteca Empirical (mismo entorno de laboratorio que Avida, no derivado de Avida); [anyaevostinar/SymbulationEmp](https://github.com/anyaevostinar/SymbulationEmp), con documentación | Referencia para el horizonte de simbiosis (H): sus hallazgos sobre la estructura espacial y la transmisión |
| **MABE / MABE2** (Hintze, Bohm, Ofria) | Marco modular de evolución con "cerebros" intercambiables (Markov Brains, redes) | C++; MABE2 en desarrollo | Los **Markov Brains** tienen nodos ocultos binarios que evolucionan memoria con facilidad: una arquitectura de memoria alternativa a la nuestra |
| **JaxLife** (Lu, Beukman, Matthews, Foerster; Oxford, 2024) | Agentes con redes neuronales, en JAX y vectorizado en GPU; aparecen comunicación simple, agricultura y uso de herramientas | Código público ([arXiv 2409.00853](https://arxiv.org/abs/2409.00853)) | Referencia de escala en GPU. Los agentes son redes densas, menos interpretables que nuestros genes |
| **Polyworld** (Yaeger) | Ecología con visión y redes neuronales evolutivas | Histórico | Inspiración; nada que reutilizar |
| **The Bibites** | Juego y simulador popular con cerebros neuronales | No encontré código abierto | Inspiración visual; no es una base científica |
| **Tierra** (Ray, 1990) | Pionero: parásitos e hiperparásitos | Histórico | Ilustra que la competencia sin diseño produce interacciones ecológicas |

## Correcciones al texto que motivó la revisión
- **Symbulation** no deriva de Avida. Está construido sobre Empirical, una biblioteca del mismo laboratorio de origen.
- **MABE** es un marco general de evolución de agentes. No es específicamente un proyecto de transición multicelular.
- **La anécdota de "hacerse los muertos"** (Lehman et al., *The Surprising Creativity of Digital Evolution*, 2020) no involucró un antivirus.
  - Ofria pausaba a cada mutante en un entorno de prueba, para descartar a los que se replicaban más rápido.
  - Los organismos evolucionaron a reconocer las entradas del entorno de prueba y a no replicarse allí.
  - Cuando se aleatorizaron esas entradas, evolucionaron a replicarse rápido solo una parte del tiempo.
  - Es un ejemplo de que la evolución explota cualquier diferencia entre lo que se mide y lo que se premia. Ya lo vivimos: en la fase 7 aparecieron atajos.

## Lo que más nos sirve ahora

### 1. Peldaños premiados (Lenski, Ofria, Pennock y Adami, *Nature* 2003)
- **Resultado:** en Avida, la función compleja EQU evolucionó construyéndose sobre funciones más simples, **pero solo cuando esas funciones también eran premiadas**.
- **Sin premios intermedios:** según las reseñas, cuando solo se premiaba EQU, ninguna población la desarrolló.
- **Matices del mismo trabajo:** ningún paso intermedio en particular fue imprescindible, y hubo mutaciones dañinas al aparecer que después sirvieron de peldaño.
- **Coincide con lo que medimos en la fase 9:**
  - el módulo de memoria completo gana siempre;
  - memoria + avanzar condicionado ya gana;
  - el primer paso (tener una memoria que siga a la pista sin usarla) no se premia, y el gen se pierde en unos miles de pasos.
- **Consecuencia:** el camino existe, pero le falta un primer peldaño premiado.

### 2. La memoria evoluciona solo si da una ventaja grande (Grabowski, Bryson, Dyer, Ofria y Pennock, ALife XII, 2010)
En Avida, el uso de memoria evolucionó solo cuando daba una ventaja significativa. Los organismos encontraron a menudo estrategias sin memoria sorprendentemente buenas, aunque las mejores sí la usaban. Coincide con nuestras fases 6–8: atajos primero, y memoria nunca mientras haya una alternativa más barata.

### 3. Arquitectura de memoria barata (Markov Brains)
En los Markov Brains, la memoria son estados ocultos que las propias compuertas escriben y leen. No hace falta un gen de costo continuo que se integre en cada paso. Nuestra memoria actual es frágil: un sesgo pequeño en el gen de memoria se integra en cada paso y borra lo recordado entre pistas. Una memoria tipo cerrojo (solo cambia ante impulsos fuertes) estaría más cerca de la de los Markov Brains y seguiría siendo física fija.

## Decisión
- **No cambiar de motor.** simbio ya tiene lo que estos proyectos no combinan: genes interpretables que deciden qué primitivas tiene cada organismo, asociación física con enlaces, determinismo y portabilidad CPU/GPU con `xp`, y nueve fases de controles.
- **Incorporar ideas, cada una como experimento con su control:**
  1. **Fase 10 (si la 9 da negativo): un mundo con peldaños.** Un entorno donde el primer paso tenga valor por sí solo; por ejemplo, que una memoria que sigue a la pista ya ayude a moverse antes de condicionar la comida. Control: el mismo mundo sin el peldaño.
  2. **Memoria tipo cerrojo** (zona muerta ante impulsos pequeños), comparada con la actual.
  3. **Validación externa:** reproducir en simbio un resultado cualitativo de Avida, por ejemplo que sin premios intermedios no aparece la función compuesta. Daría credibilidad al motor.
  4. **Horizonte de simbiosis:** leer Symbulation antes de diseñar la fase de simbiosis.

## Fuentes
- Avida: [Wikipedia](https://en.wikipedia.org/wiki/Avida_(software)), [devosoft/avida](https://github.com/devosoft/avida), [fork de coevolución (CSIC)](https://gitlab.com/fortunalab/avida).
- Lenski et al. 2003: [página del laboratorio](https://lenski.mmg.msu.edu/papers/nature2003/index.html), [PDF](https://www.cs.princeton.edu/courses/archive/fall24/cos597C/bib/598-2017/adami03Nature.pdf).
- Grabowski et al. 2010: [publicaciones de L. Grabowski](https://people.potsdam.edu/grabowlm/publications.html).
- Symbulation: [documentación](https://symbulation.readthedocs.io/), [código](https://github.com/anyaevostinar/SymbulationEmp), [Vostinar et al. 2021, *Symbiosis in Digital Evolution*](https://doaj.org/article/c23707a4c7da47048aef4283e6879c15).
- MABE: [enciclopedia ALife](https://alife.org/encyclopedia/software-platforms/mabe/), [MABE2](https://mabe2.readthedocs.io/en/latest/modules/00_module_overview.html), [comparación de sustratos con memoria](https://arxiv.org/pdf/1804.01660).
- JaxLife: [arXiv 2409.00853](https://arxiv.org/html/2409.00853v1).
- La anécdota de Ofria: Lehman et al., *The Surprising Creativity of Digital Evolution*, Artificial Life 26(2), 2020 (citada de memoria; no pude abrir el texto en esta sesión).
