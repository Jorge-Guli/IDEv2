# Spec Delta

## ADDED Requirements

### Requirement: Métricas del desarrollo
Con `desarrollo.activo`, cada registro SHALL incluir:
- la fracción de organismos con un gen que lee la red con peso mayor que 0,5;
- el peso medio con que los genes la leen;
- el estado medio en valor absoluto;
- el desvío del estado dentro de los grupos de 3 o más y en la población;
- la mayor correlación, en valor absoluto, entre un regulador y el índice de rol.

#### Scenario: Registro con la red
- **WHEN** termina un intervalo de registro con la red activa
- **THEN** el historial incluye las métricas de uso y de diferenciación
