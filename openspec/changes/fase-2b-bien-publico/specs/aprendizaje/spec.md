# Spec Delta

## MODIFIED Requirements

### Requirement: Aprendizaje por refuerzo energético
Tras cada acción, los genes que la impulsaron SHALL ajustarse en proporción a la tasa de aprendizaje heredable y a cuánto mejor o peor fue el cambio de energía respecto del promedio reciente del organismo. Los ajustes MUST estar acotados. Las acciones cuyo valor no se mide en energía propia inmediata (dividirse, dividirse unido, compartir, conjugar, secretar) MUST NOT reforzarse.

#### Scenario: Acción recompensada se refuerza
- **WHEN** una acción produce una ganancia de energía mayor a la habitual
- **THEN** los genes que la impulsaron aumentan su respuesta ante los mismos sensores

#### Scenario: Aprendizaje desactivado
- **WHEN** la tasa de aprendizaje es cero o el aprendizaje está desactivado
- **THEN** los ajustes plásticos permanecen en cero

#### Scenario: Compartir no se castiga
- **WHEN** un organismo comparte y pierde energía
- **THEN** sus genes de compartir no se ajustan por esa pérdida

#### Scenario: Secretar no se castiga
- **WHEN** un organismo secreta y pierde energía
- **THEN** sus genes de secretar no se ajustan por esa pérdida
