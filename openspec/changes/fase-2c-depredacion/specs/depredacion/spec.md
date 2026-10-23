# Spec Delta

## Purpose

Introduce una presión de selección física que depende del tamaño del grupo: el depredador no puede comer organismos que forman parte de grupos grandes. Es la condición documentada experimentalmente para el origen de colonias.

## ADDED Requirements

### Requirement: Ataque del depredador
Con la depredación activa, en cada paso cada organismo vivo SHALL sufrir un ataque con una probabilidad configurable; el azar MUST provenir del generador sembrado de la simulación.

#### Scenario: Sin depredación
- **WHEN** la depredación está desactivada
- **THEN** ningún organismo muere por ataque

### Requirement: Refugio por tamaño
Un ataque SHALL matar al organismo solo si su grupo conexo de enlaces tiene menos miembros que el tamaño de refugio; en modo gradual MUST matar con probabilidad 1 − (tamaño − 1)/(refugio − 1). Quien muere por ataque MUST morir antes de actuar.

#### Scenario: Suelto atacado
- **WHEN** un organismo sin enlaces sufre un ataque
- **THEN** muere en ese paso

#### Scenario: Refugio gradual
- **WHEN** con refugio 4 y modo gradual, se ataca a muchos organismos de grupos de 3
- **THEN** muere aproximadamente un tercio de ellos

#### Scenario: En grupo refugio
- **WHEN** un organismo de un grupo de tamaño mayor o igual al de refugio sufre un ataque
- **THEN** sobrevive

### Requirement: Depredación uniforme como control
En modo uniforme, todo ataque SHALL ser mortal, sin importar el tamaño del grupo.

#### Scenario: Grupo atacado en modo uniforme
- **WHEN** un organismo de un grupo grande sufre un ataque en modo uniforme
- **THEN** muere

### Requirement: Métricas de depredación
Cada corrida con depredación SHALL registrar las muertes por depredación y la fracción de organismos en grupos de tamaño de refugio o mayor.

#### Scenario: Registro
- **WHEN** termina un intervalo de registro con depredación activa
- **THEN** las métricas incluyen las muertes por depredación y la fracción en refugio
