# Spec Delta

## ADDED Requirements

### Requirement: Métricas de roles y memoria
Cada registro SHALL incluir la dispersión del índice de rol, (uso de comer − uso de avanzar) / (suma), en los grupos de 3 o más y en la población. Con memoria activa, MUST incluir además la memoria media, su dispersión dentro de los grupos y su correlación con el rol.

#### Scenario: Registro con memoria
- **WHEN** termina un intervalo de registro con memoria activa
- **THEN** el historial incluye las métricas de roles y de memoria
