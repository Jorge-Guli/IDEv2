# Spec Delta

## ADDED Requirements

### Requirement: Criterios de éxito de la fase 3
La fase 3 SHALL considerarse validada solo si: (C1) cada condición persiste 60 000 pasos en al menos 7 de 10 semillas; (C2) se cumplen los invariantes de enlaces y la señal queda en [0, 1] en una corrida de verificación con rumbo y señales; (C3) se cumple la reproducibilidad; (C4) el simulador supera 40 pasos/s con ~1500 organismos. Si la coordinación evoluciona es una pregunta exploratoria, con hipótesis prerregistradas que evalúa el propio script.

#### Scenario: Evaluación de la fase 3
- **WHEN** se ejecuta `experiments/fase3/evaluar.py`
- **THEN** se informan los ancestros, los criterios, las hipótesis y los exploratorios de cada condición
