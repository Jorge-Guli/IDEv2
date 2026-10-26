# Universo vivo: evolución constante, estimulada por la realidad

Documento de diseño, escrito el 2026-10-26 a partir de la propuesta del autor. Reemplaza y amplía la línea "U, universos abiertos" de la [hoja de ruta](02-hoja-de-ruta.md).

## La idea del autor
> "No le demos un universo definido y finito. Ponlo a correr en un contenedor Docker, que no salga de ahí pero que se mueva libremente dentro. Poder darle información, datos precisos; una interfaz para interactuar, un chat para hablarle a ver qué pasa; a futuro, audio y video: estimularlo con la realidad. Abrir más de un Docker, que se comuniquen entre ellos, y ver qué pasa de esas interacciones."

## Por qué tiene sentido (lo que aprendimos en las fases 1–11)
- **La prueba y error ya la hace el sistema solo.** Dentro de cada corrida, la evolución muta, prueba y selecciona sin intervención: así aparecieron los grupos (2c) y se sostuvo la memoria (10).
- **El límite es otro: en un mundo con reglas fijas, la evolución se estanca.**
  - En unos cientos de generaciones encuentra una buena solución y deja de innovar (fases 6–11: acierto plano durante miles de generaciones).
  - Además, la selección **baja la tasa de mutación** cuando el mundo es estable: de 0,02 a 0,0005 (revisión de las fases 9–11). El sistema se vuelve conservador, justo lo contrario de lo que buscamos.
- **Es uno de los grandes problemas abiertos de la vida artificial,** la *evolución abierta* (open-ended evolution): Tierra y Avida también se estancan. En la Tierra real, la innovación no se detiene porque:
  1. **el ambiente lo forman otros seres vivos que también evolucionan** (la "Reina Roja": cada mejora de la presa presiona al depredador, y viceversa);
  2. **el ambiente cambia,** y cada solución nueva crea nichos nuevos.
- **En nuestro mundo, el depredador y las estaciones son reglas escritas a mano:** una vez resueltas, no queda presión.

## Qué aporta cada parte de la propuesta

### 1. El contenedor entero como universo, sin el corral del plano 2D
Hay dos caminos:
- **(a) Un mundo simulado más rico (primero):**
  - un espacio que crece y se ramifica (una red de lugares conectados, o 3D) en lugar de un plano fijo;
  - recursos y regiones que aparecen, desaparecen y cambian;
  - reaprovecha todo lo construido.
- **(b) Organismos como programas que compiten por la CPU y la memoria del contenedor, como Tierra (después, como investigación aparte):**
  - corren dentro de un intérprete propio, nunca como código nativo, así que no pueden escaparse ni dañar nada, y siguen siendo reproducibles;
  - advertencia: el contenedor no tiene estructura que los organismos puedan aprovechar (memoria y CPU son terreno plano). Tierra mostró que ahí aparecen parásitos rápido, pero después se estanca. **La riqueza viene de la información y de las interacciones, no del espacio.**

### 2. Estimularlo con la realidad: datos, chat, audio, video
**Aclaración importante:** los organismos **no van a entender ni contestar en lenguaje** por mucho tiempo. Lo que sí se puede hacer es convertir cada estímulo en un **campo sensorial dentro de su mundo**, percibido localmente:

| Estímulo | Cómo entra al mundo |
|---|---|
| **Datos con estructura** (clima, ciclo día/noche, consumo, tráfico) | Regulan recursos y señales. Sus patrones reales (ciclos, frentes que avisan con horas, ritmos semanales) **premian recordar y anticipar**. Es lo más valioso, y va primero |
| **Texto (chat)** | Cada mensaje se vuelve un patrón de señales que recorre el mundo (letras distintas, ondas distintas) |
| **Audio** | Las frecuencias se vuelven un "sonido ambiente" local |
| **Video** | La imagen, reducida, se proyecta sobre el mundo como luz |

- **Regla aprendida en todo el proyecto:** un estímulo que no importa para sobrevivir **se ignora**. Para que haya respuesta, el estímulo tiene que estar acoplado a algo: que la luz del video haga crecer comida, o que ciertos patrones de voz anticipen algo.
- Entonces evolucionan a responder, y la respuesta se ve como cambios de conducta y de población en la interfaz. Se parece más a un **terrario donde se pueden encender luces y hacer sonidos** que a un chat, pero la respuesta es real y es de ellos.
- **"Alimentarse de internet"** se entiende así: series de datos con patrones, traducidas a recursos y señales. Convertir bytes arbitrarios en comida sería solo ruido; está estudiado que el ruido sin estructura produce organismos "todoterreno" mediocres, no inteligencia.

### 3. Varios universos que se comunican (archipiélago)
- Es el **modelo de islas** de la biología evolutiva: varios universos evolucionan por separado e intercambian organismos de vez en cuando (migración). Producen más diversidad e innovación que un universo grande.
- Cada isla puede tener física distinta (una con clima real, otra con los estímulos del autor, otra más dura). Los migrantes llevan lo aprendido de un mundo a otro.

### 4. Lo que más empuja la evolución abierta: que el ambiente sean otros organismos
Que la **depredación salga del genoma** (una primitiva para atacar y comerse a otro, con costos físicos) en lugar de un depredador fijo, produce carreras armamentistas que no terminan. Combinado con datos reales, da un universo que no deja de plantear problemas nuevos.

## Límites (las condiciones de trabajo de [04-vision.md](04-vision.md) siguen vigentes)
"Sin límites" significa **sin el corral del plano 2D, no sin seguridad**. El contenedor es la frontera:
- **Los organismos nunca tocan internet ni el equipo.** Un proceso aparte trae los datos externos en solo lectura y los deja en una carpeta; la simulación lee de ahí.
- **La red del contenedor** solo permite el canal entre universos (migración) y la interfaz local. No hay salida a internet desde la simulación.
- **Todo lo que entra se graba:** datos, mensajes, audio, video. Así cualquier corrida se puede repetir exactamente (regla de determinismo y reproducibilidad).
- **Darles a los organismos acceso real a la red o al sistema no les sirve hoy para nada** (son reglas simples), y más adelante sería justamente el riesgo que se discutió en la visión.

## Plan por etapas
Cada etapa trae su control, como siempre. Por ejemplo, estímulos reales contra los mismos estímulos mezclados al azar: si los organismos responden igual, responden a la cantidad, no a los patrones.

| Etapa | Qué | Control principal |
|---|---|---|
| **0** | Prueba corta pendiente de la fase 11: repetir la parte A con la tasa de mutación reiniciada, para saber si el colapso de μ explica el negativo | La misma corrida con μ evolucionado |
| **1** | **Modo continuo:** corre días o semanas, guarda su estado cada tanto, retoma tras un apagado. Imagen Docker | Determinismo: retomar desde un guardado da lo mismo que no haber cortado |
| **2** | **Datos reales:** clima histórico (años de datos, para que pasen muchas generaciones rápido) y después en vivo, grabado | Clima real contra el mismo clima con los días mezclados |
| **3** | **Interfaz web local:** ver el universo en vivo; caja de chat y carga de datos conectadas a un canal sensorial; después audio y video | Estímulo acoplado contra estímulo sin consecuencias |
| **4** | **Depredación evolucionada** (organismos que se comen entre sí) | Depredador fijo |
| **5** | **Archipiélago:** varios contenedores con migración | Islas aisladas |
| **6** | (Investigación) Sustrato tipo Tierra dentro del contenedor | — |

## Qué esperar, con honestidad
- **Lo probable en meses:** poblaciones que siguen ritmos reales y anticipan cambios, ecosistemas con depredadores y presas que coevolucionan, y respuestas medibles a los estímulos que importan para su supervivencia.
- **Lo que no hay que esperar pronto:** conversación. Entre "responder a un patrón de luz" y "entender lenguaje" hay el mismo camino que entre una bacteria y un mamífero.
- **Lo que hace a esto una semilla, como quiere el autor:** que el universo nunca deje de plantear problemas, y que cada paso se pueda verificar.
