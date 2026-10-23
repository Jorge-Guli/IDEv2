# Spec Delta

## MODIFIED Requirements

### Requirement: Genoma de genes-regla
El genoma SHALL ser una colección de longitud variable (hasta un máximo configurable) de genes; cada gen MUST asociar una ponderación de los sensores a una primitiva. El genoma MUST incluir rasgos heredables (tasa base de mutación, sensibilidad al estrés, tasa de aprendizaje) y una etiqueta perceptible.

#### Scenario: Genoma inicial
- **WHEN** se siembra la población inicial
- **THEN** cada organismo recibe el genoma mínimo "LUCA" definido en el código del modelo y documentado en el ODD, sin genes de asociación

#### Scenario: Etiqueta inicial
- **WHEN** se siembra la población inicial
- **THEN** cada organismo recibe una etiqueta al azar, de modo que la similitud inicial no indica parentesco
