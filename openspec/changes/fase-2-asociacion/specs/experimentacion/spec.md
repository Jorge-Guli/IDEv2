# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

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
