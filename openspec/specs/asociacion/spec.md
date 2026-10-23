# asociacion Specification

## Purpose
Permite que organismos independientes se asocien físicamente, intercambien energía y genes, y formen grupos cuya existencia y estructura dependen de la evolución y no de reglas impuestas.

## Requirements

### Requirement: Enlaces físicos entre vecinos
Un enlace SHALL unir a dos organismos que ocupan celdas vecinas y MUST ser simétrico. Cada organismo MUST poder tener como máximo un enlace por cada una de sus 8 direcciones.

#### Scenario: Unirse con el de enfrente
- **WHEN** un organismo ejecuta unirse y la celda de enfrente está ocupada
- **THEN** ambos quedan enlazados entre sí

#### Scenario: Unirse sin nadie enfrente
- **WHEN** un organismo ejecuta unirse y la celda de enfrente está vacía
- **THEN** no se crea ningún enlace

### Requirement: Ruptura por separación
Un enlace SHALL romperse cuando los organismos dejan de estar en la misma posición relativa o uno de ellos muere; MUST mantenerse si ambos se desplazan en la misma dirección en el mismo paso.

#### Scenario: Uno se aleja
- **WHEN** uno de dos organismos enlazados avanza y el otro no
- **THEN** el enlace desaparece para ambos

#### Scenario: Movimiento conjunto
- **WHEN** dos organismos enlazados avanzan en la misma dirección y ambos se desplazan
- **THEN** el enlace se conserva

#### Scenario: Muerte del enlazado
- **WHEN** un organismo enlazado muere
- **THEN** sus enlazados pierden ese enlace

### Requirement: Soltarse
Un organismo que ejecuta soltarse SHALL romper todos sus enlaces.

#### Scenario: Soltarse
- **WHEN** un organismo con enlaces ejecuta soltarse
- **THEN** queda sin enlaces y sus antiguos enlazados pierden el enlace con él

### Requirement: Costo de los enlaces
Cada enlace SHALL costar a cada uno de sus extremos una cantidad configurable de energía por paso.

#### Scenario: Más enlaces, más costo
- **WHEN** dos organismos idénticos difieren solo en su cantidad de enlaces
- **THEN** el que tiene más enlaces paga más energía por paso

### Requirement: Compartir energía
Un organismo que ejecuta compartir SHALL ceder una fracción configurable de su energía, repartida en partes iguales entre sus enlazados, que reciben esa cantidad multiplicada por una eficiencia configurable y sin superar la energía máxima.

#### Scenario: Reparto con pérdidas
- **WHEN** un organismo con energía E y dos enlazados comparte, con fracción f y eficiencia q
- **THEN** pierde f·E y cada enlazado gana f·E·q/2 (hasta su energía máxima)

#### Scenario: Compartir sin enlaces
- **WHEN** un organismo sin enlaces ejecuta compartir
- **THEN** su energía no cambia salvo el costo de la acción

### Requirement: División unida
Dividirse unido SHALL seguir las mismas reglas que dividirse y, además, MUST dejar al hijo enlazado con su progenitor.

#### Scenario: Hijo enlazado
- **WHEN** un organismo ejecuta dividirse unido con éxito
- **THEN** el hijo aparece en una celda vecina enlazado con el progenitor

### Requirement: Conjugación
Un organismo que ejecuta conjugar SHALL copiar uno de sus genes activos, elegido al azar, en una ranura libre de un enlazado elegido al azar; si el receptor no tiene ranuras libres, no ocurre la transferencia. El costo MUST pagarlo el donante.

#### Scenario: Transferencia de un gen
- **WHEN** un organismo con un enlazado que tiene ranuras libres conjuga
- **THEN** el enlazado gana un gen idéntico a uno del donante

### Requirement: Etiqueta heredable perceptible
Cada organismo SHALL tener una etiqueta heredable sin efecto físico, que muta como el resto del genoma y que sus vecinos pueden percibir solo como similitud con la propia.

#### Scenario: Herencia de la etiqueta
- **WHEN** un organismo se divide sin mutación
- **THEN** el hijo tiene la misma etiqueta

### Requirement: Asociación como capacidad desactivable
Con la asociación desactivada, las primitivas de asociación MUST NOT poder ejecutarse ni aparecer por mutación. Con la conjugación desactivada, solo conjugar queda excluido.

#### Scenario: Asociación desactivada
- **WHEN** la configuración desactiva la asociación
- **THEN** ningún organismo crea enlaces durante toda la corrida

### Requirement: Métricas de organización
Cada corrida SHALL registrar: fracción de organismos enlazados, enlaces medios, tamaño medio (ponderado por organismo) y máximo de los grupos conexos, energía compartida por organismo y paso, transferencias de genes, distancia de etiqueta entre enlazados y entre pares al azar, y la fracción de organismos que reciben mucho más de lo que dan.

#### Scenario: Grupos conexos
- **WHEN** tres organismos forman una cadena A–B–C de enlaces
- **THEN** se cuenta un grupo de tamaño 3
