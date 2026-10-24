# Spec Delta

## ADDED Requirements

### Requirement: Movimiento de grupos por fuerza
Con `asociacion.movimiento = "fuerza"`, cada grupo conexo con al menos un miembro que elige avanzar SHALL desplazarse una celda en la dirección (de las 8) más alineada con la suma de los vectores unitarios de los rumbos de quienes empujan, con probabilidad min(1, proyección de esa suma sobre la dirección / tamaño^α), si todas las celdas de destino están libres o son del propio grupo. El azar MUST provenir del generador de la simulación. Un rumbo diagonal MUST aportar lo mismo que uno cardinal.

#### Scenario: Un empujador en un trío
- **WHEN** con α = 1, en muchos tríos solo un miembro empuja y el destino está libre
- **THEN** se mueve aproximadamente un tercio de ellos, con el empujador apuntando al norte o al noreste

#### Scenario: Todos empujan
- **WHEN** los tres miembros de un trío empujan en la misma dirección hacia celdas libres
- **THEN** el trío se mueve
