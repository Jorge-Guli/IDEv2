# Spec Delta

## Purpose

Permite que un organismo ajuste su conducta durante su vida según el resultado de sus acciones, sin transmitir lo aprendido por herencia.

## ADDED Requirements

### Requirement: Plasticidad no heredable
Cada organismo SHALL tener ajustes plásticos sobre los pesos de sus genes, que empiezan en cero al nacer y MUST NOT heredarse.

#### Scenario: Hijo sin aprendizaje previo
- **WHEN** un organismo con ajustes plásticos no nulos se divide
- **THEN** el hijo nace con ajustes plásticos en cero

### Requirement: Aprendizaje por refuerzo energético
Tras cada acción, los genes que la impulsaron SHALL ajustarse en proporción a la tasa de aprendizaje heredable y a cuánto mejor o peor fue el cambio de energía respecto del promedio reciente del organismo. Los ajustes MUST estar acotados.

#### Scenario: Acción recompensada se refuerza
- **WHEN** una acción produce una ganancia de energía mayor a la habitual
- **THEN** los genes que la impulsaron aumentan su respuesta ante los mismos sensores

#### Scenario: Aprendizaje desactivado
- **WHEN** la tasa de aprendizaje es cero o el aprendizaje está desactivado
- **THEN** los ajustes plásticos permanecen en cero
