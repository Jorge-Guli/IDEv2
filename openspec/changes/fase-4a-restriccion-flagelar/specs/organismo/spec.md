# Spec Delta

## ADDED Requirements

### Requirement: Restricción flagelar
Con `fisica.refractario_division` = T > 0 y modo "division", tras una división lograda el progenitor y el hijo SHALL quedar T pasos sin poder elegir avanzar. En modo "aleatorio", en cada paso cada organismo SHALL entrar en un período de T pasos con probabilidad 2 × divisiones del paso / población, sin relación con dividirse. El período MUST descontarse un paso por paso.

#### Scenario: Tras dividirse
- **WHEN** con T = 5, un organismo se divide
- **THEN** ni él ni su hijo eligen avanzar en los pasos siguientes hasta que se agota el período

#### Scenario: Desactivada
- **WHEN** T = 0
- **THEN** nadie entra en período refractario y la dinámica es la misma que sin la opción

### Requirement: Contadores de vida
Cada organismo SHALL llevar la cuenta de las veces que eligió avanzar y de sus divisiones logradas a lo largo de su vida.

#### Scenario: Cuenta de avances
- **WHEN** un organismo elige avanzar dos veces
- **THEN** su contador de avances vale 2
