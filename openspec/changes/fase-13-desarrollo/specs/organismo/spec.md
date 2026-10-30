# Spec Delta

## ADDED Requirements

### Requirement: Red regulatoria
Con `desarrollo.activo`, cada organismo SHALL tener 8 reguladores con estado en [−1, 1]. En cada decisión, el estado MUST actualizarse como reg ← (1 − tasa)·reg + tasa·tanh(R·u + rb). Las entradas u son los reguladores propios, la media de los 2 primeros reguladores de los socios enlazados y los sensores. Cada gen SHALL sumar v·reg a su activación, salvo con `desarrollo.inerte`.

#### Scenario: Mismo genoma, distinto estado
- **WHEN** dos organismos con el mismo genoma y un gen de comer que lee el regulador 3 tienen ese regulador en +1 y en −1
- **THEN** el primero come y el segundo descansa

#### Scenario: Inhibición lateral
- **WHEN** dos células pegadas, con el regulador 0 que se activa a sí mismo (peso +2) y lo inhibe el de la vecina (−3), parten de +0,01 y −0,01
- **THEN** terminan en estados opuestos (> 0,9 y < −0,9)

#### Scenario: Control inerte
- **WHEN** la red está activa e inerte
- **THEN** el estado cambia igual, pero las decisiones no dependen de él

### Requirement: Mutación de la red regulatoria
Los pesos R, rb y v SHALL ser heredables y MUST mutar con la tasa efectiva del organismo, con el mismo tamaño que los pesos de los genes. Con la red apagada, la simulación MUST NOT consumir azar nuevo.

#### Scenario: Red apagada
- **WHEN** se muta un genoma sin la red
- **THEN** R, rb y v quedan en cero y los demás campos mutan igual que con ella

### Requirement: Herencia del estado regulatorio
Al dividirse, el hijo SHALL heredar el estado regulatorio del progenitor. Con `desarrollo.asimetria` > 0, MUST sumarle ruido normal de ese desvío, recortado a [−1, 1].

#### Scenario: Herencia exacta
- **WHEN** un organismo con la red activa, sin asimetría ni mutación, se divide
- **THEN** progenitor e hijo tienen el mismo estado
