# Spec Delta

## ADDED Requirements

### Requirement: Criterios de éxito de la fase 2c
La fase 2c SHALL considerarse validada solo si: (C1) con depredación por tamaño, la población persiste 30 000 pasos en al menos 8 de 10 semillas; (C2) se cumplen los invariantes de enlaces y del refugio en una corrida de verificación; (C3) se cumple la reproducibilidad; (C4) el simulador supera 40 pasos/s con ~1500 organismos. Si la asociación evoluciona es una pregunta exploratoria, con hipótesis prerregistradas.

#### Scenario: Evaluación de la fase 2c
- **WHEN** se ejecuta el script de evaluación de la fase 2c
- **THEN** se informan los criterios y los resultados exploratorios contra sus controles
