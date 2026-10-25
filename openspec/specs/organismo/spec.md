# organismo Specification

## Purpose
Define qué es un organismo: su metabolismo, su percepción local y cómo sus acciones emergen de su genoma bajo una física fija.

## Requirements

### Requirement: Metabolismo
Cada organismo SHALL tener una reserva de energía acotada; en cada paso MUST pagar un costo basal, uno proporcional a sus genes activos y el de su acción, y MUST morir sin actuar si su energía queda en cero o menos.

#### Scenario: Muerte por inanición
- **WHEN** un organismo no obtiene energía durante suficientes pasos
- **THEN** su energía llega a cero y es retirado del mundo

#### Scenario: Sin energía no se actúa
- **WHEN** los costos del paso dejan a un organismo sin energía
- **THEN** muere en ese paso sin comer, moverse ni dividirse

#### Scenario: Genoma grande cuesta más
- **WHEN** dos organismos idénticos difieren solo en la cantidad de genes activos
- **THEN** el de más genes paga más energía por paso

### Requirement: Percepción local
Cada organismo SHALL percibir solo información local: alimento comestible (recurso simple más alimento libre) en su celda y en las celdas al frente y a los costados, recurso complejo en su celda, su propia energía, la ocupación del vecindario, si el frente está bloqueado, su último cambio de energía, ruido, una constante, su cantidad de enlaces, la energía media de sus enlazados, si el de enfrente es un enlazado y la similitud de etiqueta con el de enfrente.

#### Scenario: Sin información global
- **WHEN** cambia el recurso en una celda a más de una celda de distancia
- **THEN** los sensores del organismo no cambian

#### Scenario: Sensores sociales locales
- **WHEN** un organismo no tiene enlaces ni nadie enfrente
- **THEN** sus sensores de enlaces, energía de enlazados, enlazado al frente y similitud de etiqueta valen cero

### Requirement: Acciones expresadas por el genoma
La física SHALL definir un conjunto fijo de primitivas (descansar, avanzar, girar izquierda, girar derecha, girar al azar, comer, dividirse, unirse, soltarse, compartir, dividirse unido, conjugar, secretar). Un organismo MUST poder ejecutar una primitiva distinta de descansar solo si tiene al menos un gen activo que la exprese; la elección en cada paso MUST surgir de sus genes y sensores.

#### Scenario: Sin gen de división no hay reproducción
- **WHEN** un organismo no tiene genes activos asociados a dividirse ni a dividirse unido
- **THEN** nunca se divide, sin importar su energía

#### Scenario: Descanso por defecto
- **WHEN** ningún gen produce un impulso positivo
- **THEN** el organismo descansa ese paso

#### Scenario: Sin gen de unión no hay enlaces propios
- **WHEN** un organismo no tiene genes que expresen unirse ni dividirse unido
- **THEN** nunca inicia un enlace (aunque otros puedan enlazarse con él)

### Requirement: Física de las acciones
Cada primitiva SHALL tener un costo energético configurable; comer MUST transferir recurso de la celda al organismo hasta un máximo por paso y sin superar la energía máxima.

#### Scenario: Comer agota la celda
- **WHEN** un organismo come en una celda con recurso R menor que el máximo por paso
- **THEN** gana R de energía (descontado el costo) y la celda queda en 0

### Requirement: División
Dividirse SHALL requerir una energía mínima y una celda vecina libre; tras pagar el costo, la energía restante MUST repartirse en partes iguales entre progenitor e hijo, que hereda una copia mutada del genoma.

#### Scenario: División exitosa
- **WHEN** un organismo con energía suficiente y un vecino libre se divide
- **THEN** aparece un hijo en una celda vecina, con la mitad de la energía restante y generación +1

#### Scenario: Sin espacio
- **WHEN** todas las celdas vecinas están ocupadas
- **THEN** la división no ocurre y no se cobra su costo

### Requirement: Restricción flagelar
Con `fisica.refractario_division` = T > 0 y modo "division", tras una división lograda el progenitor y el hijo SHALL quedar T pasos sin poder elegir avanzar. En modo "aleatorio", en cada paso cada organismo SHALL entrar en un período de T pasos con probabilidad 2 × divisiones del paso / población, sin relación con dividirse. El período MUST descontarse un paso por paso.

#### Scenario: Tras dividirse
- **WHEN** con T = 5, un organismo se divide
- **THEN** ni él ni su hijo eligen avanzar en los pasos siguientes hasta que se agota el período

#### Scenario: Desactivada
- **WHEN** T = 0
- **THEN** nadie entra en período refractario y la dinámica es la misma que sin la opción

### Requirement: Contadores de vida
Cada organismo SHALL llevar la cuenta de las veces que eligió avanzar y de sus divisiones logradas a lo largo de su vida.

#### Scenario: Cuenta de avances
- **WHEN** un organismo elige avanzar dos veces
- **THEN** su contador de avances vale 2

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
