# Proposal

## Why

En doce fases, los organismos aprendieron a asociarse en grupos (fase 2c), y casi todos los grupos nacen de una sola célula. Pero nunca aparecieron la división del trabajo, las señales usadas ni la memoria usada para decidir (fases 3 a 12). Las síntesis de las fases 5 y 8 llegaron al mismo diagnóstico: **el cuello de botella es el genoma**. Cada gen es una regla suelta del tipo "si percibo X, hago Y", y no existe el programa que en la naturaleza convierte una célula en un cuerpo.

El autor pidió (2026-10-30) dejar de inventar y copiar lo que la naturaleza ya resolvió: un cigoto, células madre con el ADN completo que se especializan según dónde están y qué les dicen sus vecinas, tejidos, y recién después neuronas. Junto con el principio 7 de la metodología (el universo no se acomoda al organismo), el camino es **ampliar lo que el genoma permite**, no lo que el mundo regala.

Los mecanismos del desarrollo están bien documentados:
- **Redes regulatorias de genes:** los genes se encienden y apagan entre sí; los tipos celulares son estados estables de esa red (Kauffman 1969).
- **Herencia del estado al dividirse** (memoria epigenética) y **división asimétrica** de las células madre.
- **Señales por contacto:** Notch–Delta y la inhibición lateral, que en los embriones eligen qué células serán neuronas.
- **Morfógenos e información posicional** (Turing 1952; Wolpert 1969).
- **Autómatas celulares neuronales:** una sola regla, compartida por todas las células, hace crecer una forma desde una semilla y la regenera (Mordvintsev et al. 2020).
- **El cuerpo como unidad de reproducción,** con línea germinal y cuello de botella unicelular (Michod 2006; Grosberg y Strathmann 2007).
- **Reproducción sexual,** que combina mejoras de linajes distintos.

## What Changes

La fase avanza por peldaños, como la naturaleza. Cada peldaño es una opción apagada por defecto, con tests y huellas sin cambios, y un piloto prerregistrado contra un control.

- **Peldaños 1 y 2 (este cambio, implementados):** red regulatoria (`desarrollo.*`). Cada célula tiene 8 reguladores, un estado en [−1, 1] que es su "tipo celular". Cada regulador sigue a tanh(R · entradas + rb). Las entradas son:
  - los reguladores propios;
  - la media de los 2 primeros reguladores (morfógenos) de los socios enlazados;
  - los sensores.

  Los genes de acción leen el estado (pesos `v`). El hijo hereda el estado, con ruido opcional (división asimétrica). Al inicio todo vale 0 y LUCA se comporta igual que sin la red. Control `desarrollo.inerte`: la red existe y muta, pero los genes no la leen.
- **Peldaño 3 (siguiente):** el cuerpo como unidad que se reproduce. Las células de un cuerpo comparten su destino y solo una línea germinal funda cuerpos nuevos desde una célula.
- **Peldaño 4:** reproducción sexual: dos cuerpos aportan cada uno la mitad del genoma de la célula fundadora.
- **Peldaño 5:** buscar tipos celulares estables y, entre ellos, células mensajeras (primeras neuronas) y redes de ellas.
- **A largo plazo** (fase propia, por el principio 7): un universo más fiel a la realidad:
  - clima con cambio climático y El Niño;
  - las acciones del autor;
  - espacio continuo en 3D con gravedad.

## Capabilities

### Modified Capabilities
- `organismo`: red regulatoria con señal por contacto y herencia del estado.
- `experimentacion`: métricas de uso de la red y de diferenciación dentro de los grupos; piloto de la fase 13.

## Impact

- **Código:** cambian `genoma.py` (campos `R`, `rb` y `v`), `poblacion.py` (estado `reg`), `simulacion.py` (`regular`, lectura en `decidir`, herencia y métricas) y `config.py` (`DesarrolloCfg`).
- **Compatibilidad:** con la red apagada no se consume azar nuevo; las huellas de determinismo no cambian y la suite completa pasa. Los genomas y poblaciones guardados antes se completan con ceros al cargarlos.
- **Costo:** ~300 números más por célula.
