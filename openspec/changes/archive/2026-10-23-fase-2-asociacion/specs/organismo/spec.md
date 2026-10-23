# Spec Delta

## MODIFIED Requirements

### Requirement: Percepción local
Cada organismo SHALL percibir solo información local: recurso en su celda y en las celdas al frente y a los costados, su propia energía, la ocupación del vecindario, si el frente está bloqueado, su último cambio de energía, ruido, una constante, su cantidad de enlaces, la energía media de sus enlazados, si el de enfrente es un enlazado y la similitud de etiqueta con el de enfrente.

#### Scenario: Sin información global
- **WHEN** cambia el recurso en una celda a más de una celda de distancia
- **THEN** los sensores del organismo no cambian

#### Scenario: Sensores sociales locales
- **WHEN** un organismo no tiene enlaces ni nadie enfrente
- **THEN** sus sensores de enlaces, energía de enlazados, enlazado al frente y similitud de etiqueta valen cero

### Requirement: Acciones expresadas por el genoma
La física SHALL definir un conjunto fijo de primitivas (descansar, avanzar, girar izquierda, girar derecha, girar al azar, comer, dividirse, unirse, soltarse, compartir, dividirse unido, conjugar). Un organismo MUST poder ejecutar una primitiva distinta de descansar solo si tiene al menos un gen activo que la exprese; la elección en cada paso MUST surgir de sus genes y sensores.

#### Scenario: Sin gen de división no hay reproducción
- **WHEN** un organismo no tiene genes activos asociados a dividirse ni a dividirse unido
- **THEN** nunca se divide, sin importar su energía

#### Scenario: Descanso por defecto
- **WHEN** ningún gen produce un impulso positivo
- **THEN** el organismo descansa ese paso

#### Scenario: Sin gen de unión no hay enlaces propios
- **WHEN** un organismo no tiene genes que expresen unirse ni dividirse unido
- **THEN** nunca inicia un enlace (aunque otros puedan enlazarse con él)
