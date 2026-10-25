# Spec Delta

## ADDED Requirements

### Requirement: Puentes citoplasmáticos
Con `asociacion.difusion_energia` = κ > 0, en cada paso la energía de cada organismo SHALL cambiar en κ · Σ_socios (E_j − E_i) / 8, conservando la energía total. La transferencia MUST quedar fuera del aprendizaje, salvo con `difusion_aprende`.

#### Scenario: Conservación
- **WHEN** dos enlazados con 80 y 20 de energía y κ = 0,5 pasan un paso sin costos
- **THEN** suman 100 y el más rico pierde 0,5 · 60 / 8
