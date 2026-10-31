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
**Versión vigente: `natural.toml`.** Clima real y nada de fuerzas diseñadas. La depredación solo existe si evoluciona con `atacar`.

Historia:
- primero se usó el universo de la fase 3, que extinguía a LUCA;
- después, el de la fase 2c;
- los dos tenían un depredador externo programado, una fuerza diseñada que el autor objetó (principio 7). Se descartaron sin evaluar.

### D8. Comer según el tamaño
El piloto de la red en `natural.toml` dio nulo y casi sin grupos. Un diagnóstico mostró por qué: los grupos se formaban, pero cualquier célula mataba a otra de su tamaño en 1–3 ataques. En la naturaleza una célula casi nunca se traga a otra de su tamaño.

Se agregó `ataque.tamano` (daño × r²/(1+r²), con r la razón de tamaños de los grupos):
- es un cambio por fidelidad, aprobado por el autor;
- se decidió **después** de ver el fracaso, y queda declarado así;
- la forma funcional no se ajusta;
- reemplaza a la protección por enlaces.

### D9. Controles pedidos por la revisión
- **`ataque.forma = "suave"`:** sensibilidad a la forma de la curva.
- **`ataque.intragrupo = false`:** sin canibalismo interno.
- **Medidas que no mezclan clones:** `corr_reg_rol_intra` y `parentesco_relativo`.
- Los dos controles son referencias de comparación, no universos.

### D10. Dónde corren los experimentos
Corren en Docker, en el servicio `experimento` con perfil propio: 4 CPU, sin red y con el código montado. Así no se abren ventanas en el escritorio del autor y no dependen de la app. Cada experimento corre entero en una plataforma, porque Linux y Windows dan huellas distintas.

## Risks
- **La red no se recluta, como la memoria en las fases 6–12.** Diferencias con aquello que le dan más chances:
  - muchos pesos continuos (caminos graduales en vez de un gen exacto);
  - la red lee todos los sensores y a las vecinas;
  - su primer peldaño no necesita una memoria previa.

  Si igual no se usa, se registra como dato. El paso siguiente es el que la naturaleza dio antes de los tejidos: el cuerpo como unidad de reproducción.
- **Costo de cómputo:** einsum de (n, 8, 37) por paso. En el piloto de 128², 3 000 pasos tardan ~12 s, del orden de lo anterior.
