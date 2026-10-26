# Visión: hacia dónde podría llevar esta semilla

Este documento recoge las ideas del autor del proyecto sobre las aplicaciones futuras de una tecnología que hoy solo existe como experimento. No es un plan: es un horizonte que orienta las decisiones de diseño. Sí son firmes las salvaguardas del final.

## La idea central
Una inteligencia que **crece** en lugar de entrenarse: emerge de abajo hacia arriba, de agentes simples que se asocian y evolucionan. Está **situada** en un dispositivo y una persona concretos, y **sigue cambiando** a lo largo del tiempo, en simbiosis con quien acompaña. Es lo contrario de un modelo monolítico entrenado una vez y congelado.

## Escenarios
1. **Compañero de vida.** Cuando nace una persona, nace también una instancia de LUCA que crece con ella en un dispositivo. Cuando el hardware se renueva, la población se muda al dispositivo nuevo y abandona el anterior. Puede adaptarse a casi cualquier hardware.
   - *Qué hay hoy:* el simulador ya no depende del hardware, y el genoma es solo datos: una población se guarda en una máquina y se despierta en otra.
2. **Drones o robots autónomos que optimizan trabajos.**
   - *Qué hay hoy:* la robótica evolutiva y la robótica de enjambre (evolucionar en simulación y transferir a robots reales). Las reglas de coordinación por percepción local de las fases 3 a 3d son del tipo que usan los enjambres.
3. **Manifestación física:** cada agente sería una unidad física (en el extremo, un nanobot) que se asocia y evoluciona como en lo digital.
   - *Qué hay hoy:* robots modulares que se ensamblan solos y organismos sintéticos como los *xenobots*. Es el horizonte más lejano y el más delicado.

## Qué tendría que aportar este proyecto como semilla
- Una plataforma abierta, reproducible y portable (`simbio`).
- Principios verificados: las acciones salen del genoma, la percepción es local, nada de modelos preentrenados dentro de los organismos, toda afirmación se compara con un control.
- Un mapa de qué condiciones hacen emerger cada peldaño de organización: asociación, coordinación, ciclo de vida, memoria, división del trabajo. Ver la [síntesis](03-sintesis.md).
- Los pasos intermedios ya anotados en la [hoja de ruta](02-hoja-de-ruta.md):
  - **universos abiertos:** entradas reales grabadas, un archipiélago de universos en distintos dispositivos y un sustrato en un contenedor aislado;
  - **simbiosis humano–organismo.**

## Salvaguardas (firmes)
1. **Acompañar, no competir.** La evolución optimiza sobrevivir, no ayudar. Para que una inteligencia evolutiva acompañe a su humano, el bienestar y las interacciones de esa persona tienen que formar parte de lo que la nutre, como en la domesticación. Si no, nada garantiza que sus intereses coincidan.
2. **Aislamiento.** Lo que evoluciona vive en un entorno aislado (simulador o contenedor sin acceso libre al sistema ni a la red). Puede **recibir** datos del mundo real, pero no actuar fuera de su entorno sin una capa de control humana.
3. **Nada que se replique solo en el mundo físico.** La evolución ocurre en lo virtual. Al mundo físico solo pasan diseños fijos, verificados y sin capacidad de replicarse ni de evolucionar por su cuenta.
4. **Privacidad y consentimiento.** Nunca usar datos genéticos ni biométricos de una persona. El ADN humano no tiene traducción con sentido a este genoma, y es el dato más sensible que existe. Para la identidad única de cada instancia alcanza una semilla aleatoria, con el consentimiento de quien corresponda.
5. **Reproducibilidad.** Aunque cada universo sea distinto, lo que percibe se registra, para que cualquier resultado se pueda repetir y verificar.
