# Spec Delta

## ADDED Requirements

### Requirement: Maquinaria por uso
Cada organismo SHALL llevar un promedio móvil del uso de comer y de avanzar. Con `fisica.maquinaria_gamma` = γ > 0, la eficiencia de una acción MUST ser min(máximo, (uso / referencia)^γ): al comer, multiplica la energía obtenida por unidad de recurso; al avanzar, el peso del empuje en el grupo y la probabilidad de avanzar de un suelto. El hijo SHALL heredar el uso de su progenitor.

#### Scenario: Especialista en comer
- **WHEN** dos organismos toman la misma cantidad de recurso y uno tiene más uso de comer
- **THEN** ese obtiene más energía, y el recurso de la celda baja lo mismo en los dos

### Requirement: Memoria interna
Con `memoria.activa`, cada organismo SHALL tener dos variables de memoria en [0, 1]. Los genes de `memoria_a` y `memoria_b` MUST NOT competir por la acción del paso: cada variable cambia en `tasa` × impulso de su primitiva, recortada a [0, 1]. El organismo SHALL percibir su memoria con dos sensores, y el hijo MUST heredar la memoria del progenitor.

#### Scenario: Persistencia
- **WHEN** un organismo no tiene genes de memoria
- **THEN** su memoria no cambia

#### Scenario: Interruptor biestable
- **WHEN** un gen de memoria se refuerza con la propia memoria (sesgo −2, peso +4)
- **THEN** organismos que parten de 0,55 y 0,45 terminan en 1 y en 0
