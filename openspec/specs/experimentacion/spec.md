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
Todos los parámetros del mundo, la física, la herencia, el aprendizaje y la asociación SHALL poder fijarse en un archivo de configuración, con interruptores para desactivar mutación, mutagénesis por estrés, aprendizaje, asociación y conjugación, y un modo de estrés barajado como control.

#### Scenario: Control de estrés barajado
- **WHEN** el modo de estrés es "barajado"
- **THEN** cada hijo muta con el estrés de un organismo elegido al azar, conservando la distribución de tasas pero no su vínculo con el hambre del progenitor

#### Scenario: Control sin aprendizaje
- **WHEN** la configuración desactiva el aprendizaje
- **THEN** la corrida se ejecuta con tasa de aprendizaje efectiva cero para todos los organismos

#### Scenario: Control de compartir sin beneficio
- **WHEN** la eficiencia de compartir es cero
- **THEN** compartir solo destruye energía del donante y ningún enlazado recibe nada

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

### Requirement: Dispositivo de cálculo automático
El simulador SHALL usar una GPU NVIDIA si está disponible y CPU en caso contrario, sin cambios en la configuración del experimento; MUST permitir forzar el dispositivo y registrar el usado. La aleatoriedad MUST generarse en CPU para que ambos dispositivos consuman la misma secuencia.

#### Scenario: Equipo sin GPU
- **WHEN** se ejecuta una corrida en un equipo sin GPU utilizable con dispositivo automático
- **THEN** la corrida se ejecuta en CPU y su resumen indica "cpu"

#### Scenario: GPU pedida sin GPU
- **WHEN** se fuerza el dispositivo GPU en un equipo sin GPU utilizable
- **THEN** la ejecución termina con un mensaje que explica cómo habilitarla

#### Scenario: Determinismo por dispositivo
- **WHEN** se ejecuta dos veces la misma configuración y semilla en el mismo tipo de dispositivo
- **THEN** los resultados son idénticos

### Requirement: Criterios de éxito de la fase 2
La fase 2 SHALL considerarse validada solo si: (C1) con asociación, la población persiste 30 000 pasos en al menos 4 de 5 semillas, en entorno constante y variable; (C2) se cumplen los invariantes de enlaces durante una corrida de verificación; (C3) se cumple la reproducibilidad; (C4) el simulador supera 40 pasos/s con ~1500 organismos. Que la asociación evolucione o no es una pregunta exploratoria, no un criterio.

#### Scenario: Evaluación de criterios de la fase 2
- **WHEN** se ejecuta el script de evaluación de la fase 2
- **THEN** se informa cada criterio como aprobado o no, con sus números, junto con los resultados exploratorios

### Requirement: Criterios de éxito de la fase 2b
La fase 2b SHALL considerarse validada solo si: (C1) con el bien público activo, la población persiste 30 000 pasos en al menos 4 de 5 semillas; (C2) la digestión conserva la materia (complejo perdido = libre ganado / rendimiento) en una corrida de verificación; (C3) se cumple la reproducibilidad; (C4) el simulador supera 40 pasos/s con ~1500 organismos. Si evolucionan la secreción y la asociación es una pregunta exploratoria.

#### Scenario: Evaluación de la fase 2b
- **WHEN** se ejecuta el script de evaluación de la fase 2b
- **THEN** se informa cada criterio y los resultados exploratorios contra sus controles

### Requirement: Criterios de éxito de la fase 2c
La fase 2c SHALL considerarse validada solo si: (C1) con depredación por tamaño, la población persiste 30 000 pasos en al menos 8 de 10 semillas; (C2) se cumplen los invariantes de enlaces y del refugio en una corrida de verificación; (C3) se cumple la reproducibilidad; (C4) el simulador supera 40 pasos/s con ~1500 organismos. Si la asociación evoluciona es una pregunta exploratoria, con hipótesis prerregistradas.

#### Scenario: Evaluación de la fase 2c
- **WHEN** se ejecuta el script de evaluación de la fase 2c
- **THEN** se informan los criterios y los resultados exploratorios contra sus controles

### Requirement: Criterios de éxito de la fase 3
La fase 3 SHALL considerarse validada solo si: (C1) cada condición persiste 60 000 pasos en al menos 7 de 10 semillas; (C2) se cumplen los invariantes de enlaces y la señal queda en [0, 1] en una corrida de verificación con rumbo y señales; (C3) se cumple la reproducibilidad; (C4) el simulador supera 40 pasos/s con ~1500 organismos. Si la coordinación evoluciona es una pregunta exploratoria, con hipótesis prerregistradas que evalúa el propio script.

#### Scenario: Evaluación de la fase 3
- **WHEN** se ejecuta `experiments/fase3/evaluar.py`
- **THEN** se informan los ancestros, los criterios, las hipótesis y los exploratorios de cada condición

### Requirement: Evaluación de la fase 3c
La evaluación de la fase 3c SHALL cruzar la regla de movimiento (empuje, fuerza con α = 1, fuerza con α = 0,5) con la percepción (ninguna, rumbo y señales, barajada), con un ancestro por semilla y semillas que no se usaron en pilotos, y SHALL aplicar las reglas del prerregistro en el propio script. La alineación MUST calcularse solo en corridas con al menos 20 pares enlazados por registro.

#### Scenario: Evaluación de la fase 3c
- **WHEN** se ejecuta `experiments/fase3c/evaluar.py`
- **THEN** se informan los ancestros, la persistencia, las hipótesis y los exploratorios de las nueve condiciones

### Requirement: Réplica de la fase 3c
Cuando se corren las tres percepciones con α = 0,5, el script SHALL calcular las reglas de la réplica: régimen con grupos (fracción ≥ 0,2 en grupos de 3 o más) de `ambos` contra `barajado` con Fisher exacto de una cola (R1), tamaño medio dentro del régimen (R2) y `barajado` contra `base` con dos colas (R3).

#### Scenario: Réplica
- **WHEN** se ejecuta la evaluación de la fase 3c con `fuerza05_base`, `fuerza05_ambos` y `fuerza05_barajado`
- **THEN** el informe incluye R1, R2 y R3
