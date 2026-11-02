# Spec Delta

## ADDED Requirements

### Requirement: Metabolismo según la actividad
Con `metabolismo.activo`, cada organismo SHALL tener una actividad reciente `a` en [0, 1]. En cada paso, `a` MUST actualizarse como a ← a + inercia · (hizo − a), donde `hizo` vale 1 si la acción elegida no fue descansar y 0 si lo fue. El costo basal de ese paso SHALL ser `costo_basal · (piso + (1 − piso) · a)`, calculado con la actividad previa a esa actualización. El costo por gen y el costo de las acciones MUST NOT cambiar.

#### Scenario: Reposo prolongado
- **WHEN** un organismo con `piso = 0,1` e `inercia = 0,05` descansa 200 pasos seguidos desde a = 1
- **THEN** su actividad queda por debajo de 0,001 y su costo basal por debajo de 0,101 · costo_basal

#### Scenario: Apagado
- **WHEN** `metabolismo.activo` es falso
- **THEN** el costo basal es `costo_basal` en cada paso y la simulación da exactamente los mismos números que antes del cambio

### Requirement: Herencia de la actividad
Al dividirse, la cría SHALL nacer con la actividad del progenitor. La regla MUST valer para la división suelta y para la división unida.

#### Scenario: Cría de un progenitor aquietado
- **WHEN** un organismo con a = 0,05 se divide
- **THEN** su cría nace con a = 0,05

### Requirement: Compatibilidad de lo guardado
Una población o un estado guardados sin el campo de actividad SHALL cargarse con a = 1 para todos los organismos.

#### Scenario: Población vieja
- **WHEN** se carga un `poblacion.npz` anterior a esta fase con el metabolismo activo
- **THEN** todos sus organismos empiezan con actividad 1
