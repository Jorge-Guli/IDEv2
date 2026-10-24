# Design

## Decisions

### D1. La restricción afecta a avanzar, no a ser movido
Una célula sin flagelos no empuja, pero si está en un grupo, el grupo la arrastra. Es el argumento de *Volvox*: la colonia conserva la motilidad gracias a las células que no se están dividiendo. Un suelto que se divide, en cambio, queda inmóvil.

### D2. Control con la misma inmovilidad
El modo aleatorio reproduce la frecuencia de períodos refractarios del paso, de modo que el costo de inmovilidad es el mismo. Lo único que cambia es que no está ligado a dividirse. Las métricas de especialización tienen una línea de base alta por razones mecánicas: las células del borde tienen espacio para dividirse, y dividirse ocupa pasos. Por eso la comparación principal es contra este control, no contra "sin".

### D3. Valor de T
- T = 50 extinguió a la población en el piloto.
- Se evalúan T = 10 y T = 20.

## Risks
- [Métricas ruidosas: pocas divisiones por miembro] → comparaciones pareadas por semilla, contra el control aleatorio.
- [El efecto puede ser chico en 60 000 pasos] → el prerregistro lo anticipa.
