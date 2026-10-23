# Spec Delta

## Purpose

Define cómo se transmite y varía la información hereditaria, incluida la capacidad de aumentar la variación bajo estrés.

## ADDED Requirements

### Requirement: Genoma de genes-regla
El genoma SHALL ser una colección de longitud variable (hasta un máximo configurable) de genes; cada gen MUST asociar una ponderación de los sensores a una primitiva. El genoma MUST incluir rasgos heredables: tasa base de mutación, sensibilidad al estrés y tasa de aprendizaje.

#### Scenario: Genoma inicial
- **WHEN** se siembra la población inicial
- **THEN** cada organismo recibe el genoma mínimo "LUCA" definido en el código del modelo y documentado en el ODD

### Requirement: Operadores de mutación
Al dividirse, el genoma del hijo SHALL poder sufrir: mutación puntual de pesos, cambio de primitiva de un gen, duplicación de un gen, eliminación de un gen, aparición de un gen nuevo aleatorio y mutación de los rasgos heredables. La probabilidad de cada operador MUST escalar con la tasa de mutación efectiva.

#### Scenario: Mutación desactivada
- **WHEN** la mutación está desactivada en la configuración
- **THEN** el hijo es una copia exacta del progenitor

#### Scenario: Duplicación y divergencia
- **WHEN** ocurre una duplicación con espacio libre en el genoma
- **THEN** el hijo tiene un gen más, copia del original, que puede divergir en mutaciones posteriores

### Requirement: Mutagénesis por estrés
Cada organismo SHALL acumular estrés como promedio móvil de su hambre (energía bajo un umbral), sin que dividirse lo altere; nace con estrés cero. La tasa efectiva de su descendencia MUST ser tasa_base × (1 + sensibilidad × estrés), con un tope; la sensibilidad es heredable.

#### Scenario: Más variación con hambre
- **WHEN** dos progenitores idénticos con sensibilidad > 0 difieren en su nivel de estrés
- **THEN** el más estresado produce descendencia con tasa de mutación efectiva mayor

#### Scenario: Dividirse no es hambre
- **WHEN** un organismo bien alimentado se divide y ambas mitades quedan sobre el umbral de hambre
- **THEN** su estrés no aumenta

#### Scenario: Estrés desactivado
- **WHEN** la mutagénesis por estrés está desactivada
- **THEN** la tasa efectiva es igual a la tasa base y la sensibilidad no evoluciona
