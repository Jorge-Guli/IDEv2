# Spec Delta

## Purpose

Define el espacio físico donde viven los organismos y la disponibilidad de recursos que impone la presión de supervivencia.

## ADDED Requirements

### Requirement: Mundo espacial toroidal
El mundo SHALL ser una grilla 2D de tamaño configurable con bordes toroidales; cada celda MUST contener como máximo un organismo.

#### Scenario: Movimiento a través del borde
- **WHEN** un organismo en la última columna avanza hacia el este
- **THEN** aparece en la primera columna de la misma fila

#### Scenario: Celda ocupada
- **WHEN** un organismo intenta entrar en una celda ocupada
- **THEN** el movimiento no ocurre y el organismo permanece en su celda

### Requirement: Recursos que se regeneran
Cada celda SHALL tener un nivel de recurso no negativo que se regenera hacia su capacidad local a una tasa configurable, sin superarla.

#### Scenario: Regeneración tras consumo
- **WHEN** una celda con capacidad K queda en 0 y nadie la consume
- **THEN** su recurso crece en cada paso y nunca supera K

### Requirement: Heterogeneidad espacial
La capacidad de recurso SHALL distribuirse en parches espacialmente correlacionados, generados de forma reproducible a partir de la semilla.

#### Scenario: Parches reproducibles
- **WHEN** se crea el mundo dos veces con la misma configuración y semilla
- **THEN** los mapas de capacidad son idénticos

### Requirement: Variabilidad temporal
El entorno SHALL soportar estacionalidad (oscilación periódica de la capacidad) y cambios abruptos programados (regenerar el mapa de parches en un paso dado).

#### Scenario: Estación de escasez
- **WHEN** la amplitud estacional es A > 0
- **THEN** la capacidad efectiva oscila entre K·(1−A) y K·(1+A) con el período configurado

#### Scenario: Cambio abrupto
- **WHEN** se configura un cambio de entorno en el paso T
- **THEN** a partir de T el mapa de capacidad es distinto del anterior
