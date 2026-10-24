# Spec Delta

## ADDED Requirements

### Requirement: Evaluación de la fase 3c
La evaluación de la fase 3c SHALL cruzar la regla de movimiento (empuje, fuerza con α = 1, fuerza con α = 0,5) con la percepción (ninguna, rumbo y señales, barajada), con un ancestro por semilla y semillas que no se usaron en pilotos, y SHALL aplicar las reglas del prerregistro en el propio script. La alineación MUST calcularse solo en corridas con al menos 20 pares enlazados por registro.

#### Scenario: Evaluación de la fase 3c
- **WHEN** se ejecuta `experiments/fase3c/evaluar.py`
- **THEN** se informan los ancestros, la persistencia, las hipótesis y los exploratorios de las nueve condiciones
