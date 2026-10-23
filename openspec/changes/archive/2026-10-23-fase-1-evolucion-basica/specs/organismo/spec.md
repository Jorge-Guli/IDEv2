# Spec Delta

## Purpose

Define qué es un organismo: su metabolismo, su percepción local y cómo sus acciones emergen de su genoma bajo una física fija.

## ADDED Requirements

### Requirement: Metabolismo
Cada organismo SHALL tener una reserva de energía acotada; en cada paso MUST pagar un costo basal, uno proporcional a sus genes activos y el de su acción, y MUST morir sin actuar si su energía queda en cero o menos.

#### Scenario: Muerte por inanición
- **WHEN** un organismo no obtiene energía durante suficientes pasos
- **THEN** su energía llega a cero y es retirado del mundo

#### Scenario: Sin energía no se actúa
- **WHEN** los costos del paso dejan a un organismo sin energía
- **THEN** muere en ese paso sin comer, moverse ni dividirse

#### Scenario: Genoma grande cuesta más
- **WHEN** dos organismos idénticos difieren solo en la cantidad de genes activos
- **THEN** el de más genes paga más energía por paso

### Requirement: Percepción local
Cada organismo SHALL percibir solo información local: recurso en su celda y en las celdas al frente y a los costados, su propia energía, la ocupación del vecindario, si el frente está bloqueado, su último cambio de energía, ruido y una constante.

#### Scenario: Sin información global
- **WHEN** cambia el recurso en una celda a más de una celda de distancia
- **THEN** los sensores del organismo no cambian

### Requirement: Acciones expresadas por el genoma
La física SHALL definir un conjunto fijo de primitivas (descansar, avanzar, girar izquierda, girar derecha, girar al azar, comer, dividirse). Un organismo MUST poder ejecutar una primitiva distinta de descansar solo si tiene al menos un gen activo que la exprese; la elección en cada paso MUST surgir de sus genes y sensores.

#### Scenario: Sin gen de división no hay reproducción
- **WHEN** un organismo no tiene genes activos asociados a dividirse
- **THEN** nunca se divide, sin importar su energía

#### Scenario: Descanso por defecto
- **WHEN** ningún gen produce un impulso positivo
- **THEN** el organismo descansa ese paso

### Requirement: Física de las acciones
Cada primitiva SHALL tener un costo energético configurable; comer MUST transferir recurso de la celda al organismo hasta un máximo por paso y sin superar la energía máxima.

#### Scenario: Comer agota la celda
- **WHEN** un organismo come en una celda con recurso R menor que el máximo por paso
- **THEN** gana R de energía (descontado el costo) y la celda queda en 0

### Requirement: División
Dividirse SHALL requerir una energía mínima y una celda vecina libre; tras pagar el costo, la energía restante MUST repartirse en partes iguales entre progenitor e hijo, que hereda una copia mutada del genoma.

#### Scenario: División exitosa
- **WHEN** un organismo con energía suficiente y un vecino libre se divide
- **THEN** aparece un hijo en una celda vecina, con la mitad de la energía restante y generación +1

#### Scenario: Sin espacio
- **WHEN** todas las celdas vecinas están ocupadas
- **THEN** la división no ocurre y no se cobra su costo
