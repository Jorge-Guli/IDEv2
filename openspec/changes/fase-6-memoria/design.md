# Design

## Decisions

### D1. Maquinaria sobre el rendimiento
En la primera versión, la eficiencia multiplicaba la toma máxima y no tenía efecto: el 96 % de las veces la toma estaba limitada por el recurso de la celda. Multiplicar el rendimiento (energía por recurso) hace que la especialización rinda.

### D2. Memoria como integrador
La memoria suma el impulso de sus genes; sin genes, no cambia. Así puede sostener un estado indefinidamente, y un gen que la lee y la refuerza crea un interruptor biestable. Es lo mínimo para que dos clones con el mismo genoma sostengan estados distintos.

### D3. Herencia de la memoria
El hijo hereda la memoria del progenitor. No se implementa división asimétrica: si hace falta, la asimetría puede salir de la experiencia distinta de cada uno después de dividirse.

### D4. Tiempo evolutivo
Las fases anteriores corrían ~250–500 generaciones. Las corridas largas de la fase 6 llegan a ~1000–1500, en el equipo local.

## Risks
- [Seguir sin señal] → se informa como negativo; el siguiente paso sería atenuar el conflicto entre niveles (que empujar rinda a quien empuja) o una regulación genética más rica.
