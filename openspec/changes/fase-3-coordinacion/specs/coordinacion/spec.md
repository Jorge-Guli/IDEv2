# Spec Delta

## ADDED Requirements

### Requirement: Percepción del rumbo de los socios
Con `coordinacion.rumbo` activo, cada organismo SHALL percibir, solo a través de sus enlaces válidos, el seno y el coseno medios del ángulo entre el rumbo de cada socio y el propio (seno positivo: el socio apunta hacia el lado al que gira `girar_der`) y la fracción de socios cuya acción del paso anterior fue avanzar. Sin enlaces, los tres sensores MUST valer 0. Con la opción desactivada, MUST valer 0 para todos.

#### Scenario: Socio girado a la derecha
- **WHEN** un organismo con rumbo 0 está enlazado a uno solo con rumbo 1
- **THEN** su sensor de seno vale sin(π/4) y el del socio vale −sin(π/4)

#### Scenario: Empuje del socio
- **WHEN** el único socio de un organismo avanzó en el paso anterior
- **THEN** su sensor de empuje vale 1

### Requirement: Canal de señales
Con `coordinacion.senales` activo, la primitiva `senalar` SHALL estar disponible para la mutación. Sus genes MUST NOT competir por la acción del paso: la señal del organismo es su impulso de `senalar` recortado a [0, 1] (0 sin genes de señal) y cuesta `costo_senal` por unidad y paso. Cada organismo SHALL percibir la señal media de sus enlazados y su propia señal del paso anterior. La señal no se refuerza por aprendizaje.

#### Scenario: La señal no ocupa la acción
- **WHEN** un organismo tiene un gen de `senalar` con sesgo 0,7 y un gen de comer con sesgo 5
- **THEN** come en ese paso, emite una señal tanh(0,7) y sus socios la perciben en el paso siguiente

#### Scenario: Señales desactivadas
- **WHEN** `coordinacion.senales` está desactivado
- **THEN** ningún organismo emite señal y los sensores de señal valen 0

### Requirement: Control barajado
Con `coordinacion.barajar` activo, los valores de los sensores de coordinación activos SHALL reemplazarse por los de otro organismo elegido por una permutación aleatoria del generador de la simulación.

#### Scenario: Misma distribución, sin información
- **WHEN** se barajan los sensores de rumbo
- **THEN** el conjunto de valores percibidos es el mismo, pero no corresponde a los socios propios

### Requirement: Métricas de coordinación
Cada registro SHALL incluir la alineación media del rumbo entre enlazados (coseno), el éxito del empuje colectivo (grupos que se movieron sobre los que intentaron moverse), también para grupos de 3 o más, y la señal media.

#### Scenario: Registro
- **WHEN** termina un intervalo de registro
- **THEN** las métricas incluyen alineación, éxito del empuje y señal media
