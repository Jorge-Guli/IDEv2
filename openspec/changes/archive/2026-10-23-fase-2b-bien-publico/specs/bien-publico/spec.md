# Spec Delta

## Purpose

Introduce un bien público físico: un alimento que solo existe si alguien paga por producir la enzima que lo libera, y que queda disponible para todos los vecinos, cooperadores o no.

## ADDED Requirements

### Requirement: Recurso complejo
Con el bien público activo, cada celda SHALL tener un recurso complejo que se regenera hacia su capacidad, en un mapa de parches propio y reproducible; MUST NOT poder comerse directamente.

#### Scenario: No comestible
- **WHEN** un organismo come en una celda con recurso complejo y sin recurso simple ni alimento libre
- **THEN** no gana energía y el recurso complejo no cambia por esa acción

### Requirement: Secretar enzima
Un organismo que ejecuta secretar SHALL pagar un costo configurable y agregar una cantidad configurable de enzima a su celda.

#### Scenario: Secreción
- **WHEN** un organismo con energía suficiente secreta
- **THEN** la enzima de su celda aumenta y su energía baja en el costo de secretar

### Requirement: Difusión y degradación de la enzima
En cada paso, la enzima SHALL difundirse una fracción configurable a las 8 celdas vecinas y degradarse una fracción configurable; la difusión MUST conservar la cantidad total antes de la degradación.

#### Scenario: Degradación
- **WHEN** nadie secreta durante muchos pasos
- **THEN** la enzima total tiende a cero

### Requirement: Digestión
En cada celda, la enzima SHALL convertir recurso complejo en alimento libre a razón de C·(1 − exp(−k·Z)), donde C es el recurso complejo, Z la enzima y k una tasa configurable; el recurso complejo convertido MUST pasar íntegro a alimento libre, multiplicado por un rendimiento configurable.

#### Scenario: Sin enzima no hay digestión
- **WHEN** una celda tiene recurso complejo y no tiene enzima
- **THEN** no se produce alimento libre en ella

#### Scenario: Conservación
- **WHEN** se digiere una cantidad d de recurso complejo con rendimiento r
- **THEN** el recurso complejo baja d y el alimento libre sube r·d

### Requirement: Alimento libre compartido
El alimento libre SHALL difundirse y degradarse como la enzima, y cualquier organismo que coma en su celda MUST poder comerlo, después del recurso simple y dentro de la misma toma máxima.

#### Scenario: El aprovechado también come
- **WHEN** un organismo sin genes de secretar come en una celda con alimento libre producido por otro
- **THEN** gana esa energía

### Requirement: Bien público desactivable
Con el bien público desactivado, secretar MUST NOT poder ejecutarse ni aparecer por mutación, y los campos nuevos MUST permanecer en cero. Con la secreción inerte, secretar SHALL costar sin producir enzima.

#### Scenario: Secreción inerte
- **WHEN** la secreción es inerte y un organismo secreta
- **THEN** paga el costo y la enzima no cambia
