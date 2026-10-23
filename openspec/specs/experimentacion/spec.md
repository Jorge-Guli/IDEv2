# experimentacion Specification

## Purpose
Garantiza que los experimentos sean reproducibles, medibles y comparables contra controles, y que puedan ejecutarse a mayor escala fuera del entorno de desarrollo.

## Requirements

### Requirement: Reproducibilidad
Una corrida SHALL estar determinada por su configuración y su semilla.

#### Scenario: Misma semilla
- **WHEN** se ejecuta dos veces la misma configuración con la misma semilla
- **THEN** las métricas registradas son idénticas

### Requirement: Configuración en archivo
Todos los parámetros del mundo, la física, la herencia y el aprendizaje SHALL poder fijarse en un archivo de configuración, con interruptores para desactivar mutación, mutagénesis por estrés y aprendizaje, y un modo de estrés barajado como control.

#### Scenario: Control de estrés barajado
- **WHEN** el modo de estrés es "barajado"
- **THEN** cada hijo muta con el estrés de un organismo elegido al azar, conservando la distribución de tasas pero no su vínculo con el hambre del progenitor

#### Scenario: Control sin aprendizaje
- **WHEN** la configuración desactiva el aprendizaje
- **THEN** la corrida se ejecuta con tasa de aprendizaje efectiva cero para todos los organismos

### Requirement: Métricas y registros
Cada corrida SHALL registrar periódicamente métricas de población, energía, nacimientos, muertes, tamaño del genoma, presencia y uso de cada primitiva, rasgos heredables, estrés y generación, y SHALL guardar la población final y gráficos resumen.

#### Scenario: Salida de una corrida
- **WHEN** termina una corrida
- **THEN** su carpeta contiene la configuración usada, las métricas en CSV, la población final y gráficos

### Requirement: Competencia entre poblaciones
El sistema SHALL poder sembrar un mundo con dos poblaciones guardadas en proporciones iguales y medir la fracción de cada una tras T pasos.

#### Scenario: Evolucionados contra LUCA
- **WHEN** se enfrentan una población evolucionada y LUCA sin mutación
- **THEN** se reporta la fracción final de descendientes de cada una, en un mapa distinto del de la evolución

### Requirement: Criterios de éxito de la fase
La fase 1 SHALL considerarse validada solo si: (C1) la población persiste 20 000 pasos en al menos 4 de 5 semillas; (C2) la población evolucionada supera el 80 % frente a LUCA en al menos 4 de 5 competencias; (C3) se cumple la reproducibilidad; (C4) el simulador supera 50 pasos/s con ~1500 organismos.

#### Scenario: Evaluación de criterios
- **WHEN** se ejecuta el script de evaluación de la fase
- **THEN** se informa cada criterio como aprobado o no, con sus números
