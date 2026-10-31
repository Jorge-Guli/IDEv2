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

### Requirement: Métricas del cuerpo
Con `desarrollo.activo`, cada registro SHALL incluir el parentesco relativo dentro de los grupos de 3 o más y la correlación entre estado y rol con la media de cada grupo restada. Con `ataque.tamano`, MUST incluir la fracción de ataques dentro del propio grupo.

#### Scenario: Registro con cuerpos
- **WHEN** termina un intervalo de registro con grupos de 3 o más y ataque según tamaño
- **THEN** el historial incluye `parentesco_relativo`, `corr_reg_rol_intra` y `frac_ataques_intragrupo`

### Requirement: Experimentos en contenedor
Los experimentos largos SHALL correr en el servicio `experimento` de Docker, sin red. Cada experimento MUST correr entero en una sola plataforma.

#### Scenario: Lanzamiento de un piloto
- **WHEN** se lanza un piloto de varias horas
- **THEN** corre en un contenedor sin abrir ventanas en el escritorio del autor y guarda su avance en `runs/`
