# Design

## Decisions

### D1. Red recurrente, no reglas sueltas
Un tipo celular es un estado estable de una red de genes que se regulan entre sí, no una regla. Por eso los reguladores leen a los otros reguladores (recurrencia), y el estado se integra con una tasa: reg ← (1 − τ)·reg + τ·tanh(R·u + rb), con τ = 0,2. Con autoactivación, un regulador forma un interruptor biestable; con varios, la red tiene varios atractores (Kauffman).

### D2. Señal por contacto entre células pegadas
Los 2 primeros reguladores son visibles para los socios enlazados (media sobre los socios). Es la señal yuxtacrina de Notch–Delta: alcanza con dos pesos (autoactivación e inhibición por la vecina) para que dos hermanas idénticas terminen en estados opuestos, como lo muestra el test `test_inhibicion_lateral_diferencia_a_dos_hermanas`. La información puede llegar más lejos por relevos de vecina en vecina. No hay difusión por el espacio: la percepción sigue siendo local, y el cuerpo es lo único que conecta a las células.

### D3. Los genes de acción leen el estado
Cada gen suma v · reg a su activación, sin tocar los pesos ni la regulación de las fases anteriores. Es la forma más simple de que el mismo genoma haga cosas distintas según el tipo celular.

### D4. Herencia y asimetría
El hijo copia el estado del progenitor (memoria epigenética). Con `asimetria` > 0, recibe además ruido normal: rompe la simetría entre hermanas, como el reparto desigual de determinantes en las células madre. El piloto usa 0, el valor de fábrica: la asimetría puede salir del ruido de los sensores y de la historia de cada célula.

### D5. Nada decidido de antemano
Los pesos de la red empiezan en 0 y mutan con la misma tasa y el mismo tamaño que los genes. No hay costo propio de la red ni premio por diferenciarse: si la red se usa, es porque rinde en el universo elegido.

### D6. Control inerte
Para separar uso de deriva, el control tiene la red funcionando y mutando, con el mismo consumo de azar, pero sin efecto sobre los genes (como `asociacion.inerte`).

### D7. Universo del piloto
Es el de la fase 3, donde los grupos evolucionan solos por un depredador que come grupos chicos. Se elige antes de correr y no se ajusta según el resultado (principio 7).

## Risks
- **La red no se recluta, como la memoria en las fases 6–12.** Diferencias con aquello que le dan más chances:
  - muchos pesos continuos (caminos graduales en vez de un gen exacto);
  - la red lee todos los sensores y a las vecinas;
  - su primer peldaño no necesita una memoria previa.

  Si igual no se usa, se registra como dato. El paso siguiente es el que la naturaleza dio antes de los tejidos: el cuerpo como unidad de reproducción.
- **Costo de cómputo:** einsum de (n, 8, 37) por paso. En el piloto de 128², 3 000 pasos tardan ~12 s, del orden de lo anterior.
