# Spec Delta

## ADDED Requirements

### Requirement: Escalada del refugio
Con `depredacion.refugio_final` mayor que 0, el tamaño de refugio vigente SHALL ser `refugio` hasta `escalada_inicio` y subir linealmente hasta `refugio_final` en `escalada_pasos` pasos; MUST usarse ese valor (no necesariamente entero) en la probabilidad de muerte del modo gradual y en la fracción en refugio.

#### Scenario: Mitad de la escalada
- **WHEN** el refugio escala de 2 a 4 entre los pasos 10 y 30
- **THEN** en el paso 20 el refugio vigente es 3

#### Scenario: Par tras la escalada
- **WHEN** el refugio vigente es 3 y se ataca a muchos organismos de pares
- **THEN** muere aproximadamente la mitad de ellos
