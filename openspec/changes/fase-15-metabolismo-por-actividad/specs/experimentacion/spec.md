# Spec Delta

## ADDED Requirements

### Requirement: Métricas del letargo
Con `metabolismo.activo`, cada registro SHALL incluir:
- la actividad media;
- la fracción de organismos en letargo (a < 0,2);
- la fracción de nacimientos del intervalo con a < 0,2 al nacer.

#### Scenario: Registro con metabolismo
- **WHEN** termina un intervalo de registro con el metabolismo activo
- **THEN** el historial incluye `actividad_media`, `frac_letargo` y `frac_nacen_quietos`

### Requirement: Reproducción de la serie del equipo
El experimento de la fase 15 SHALL alimentar `cpu_libre` desde los registros grabados de los niveles docker y pc, multiplicados como en el universo natural. Cada muestra de 10 s MUST durar 500 pasos. El punto de partida dentro de la serie SHALL salir del generador de la semilla. Con la misma semilla y los mismos registros, la corrida MUST dar los mismos números.

#### Scenario: Tres mundos físicos
- **WHEN** se corre una semilla con la serie real, con su promedio quieto y con la serie barajada por muestras
- **THEN** las tres usan la misma distribución de valores; solo cambia el orden (real o barajada) o desaparece la variación (quieto)
