# 2026-10-24 · Fase 2c: depredación limitada por tamaño, resultados

Hipótesis y reglas prerregistradas en [`2026-10-23-fase2c-prerregistro.md`](2026-10-23-fase2c-prerregistro.md) (versión 2 y addendum). Las hipótesis las evalúa el propio script (`experiments/fase2c/evaluar.py`, `evaluar_hipotesis`). Esta bitácora fue **corregida tras una revisión científica de la interpretación**: la versión anterior exageraba varias afirmaciones (ver "Correcciones" al final).

## Configuración
- `experiments/configs/depredacion.toml`: física base con asociación y movimiento de grupos por empuje.
- Depredador: ataque con probabilidad 0,015 por organismo y paso. El ataque mata con probabilidad 1 − (tamaño − 1)/(refugio − 1), con refugio 2: los sueltos mueren y los grupos de 2 o más quedan a salvo. Aclimatación de 2000 pasos.
- **Núcleo** (aparición brusca): semillas 11–20. Informe: [`2026-10-24-fase2c-nucleo-informe.json`](2026-10-24-fase2c-nucleo-informe.json).
- **Rampa** (la intensidad sube durante 8000 pasos): semillas 31–40. Informe: [`2026-10-24-fase2c-rampa-informe.json`](2026-10-24-fase2c-rampa-informe.json).
  - El valor 8000 se eligió sin pilotos y no se probó ningún otro.
  - El C1 de ese informe dice "0/10" por un error del script, ya corregido: contaba solo la condición `refugio`, que no se corrió en la rampa. El dato correcto es 10/10.
- **Variantes probadas en total en esta fase**, para dimensionar el riesgo de buscar hasta encontrar:
  - intensidades 0,002 / 0,005 / 0,01 / 0,015 / 0,02 en pilotos de 2 semillas;
  - refugios 2, 3 y 4, abrupto y gradual;
  - la versión 1 (anulada), la versión 2 (núcleo) y la rampa.

  Con 0,02 todo se extingue y con 0,01 o menos no hay efecto: **la ventana de intensidades viable es angosta**.
- **Semillas 21–30**, corridas en el equipo local (RTX 5060 Ti; 257 pasos/s): todas las condiciones, incluido el barrido de dosis (P4), refugio 3, sin división unida y la réplica de la rampa. Informe: [`2026-10-24-fase2c-semillas-21-30-informe.json`](2026-10-24-fase2c-semillas-21-30-informe.json).

## Criterios
- C1: núcleo 6/10, ❌; rampa 10/10, ✅. Semillas 21–30: refugio 9/10, p0125 9/10, p0175 9/10, sin división unida 8/10, refugio 3 8/10, rampa 10/10, ✅.
- C2, invariantes de enlaces: 0 violaciones en 415 000 enlaces revisados. ✅ El chequeo "nadie en un grupo refugio muere por ataque" es una prueba de código: con refugio 2 se cumple por construcción.
- C3, reproducibilidad: ✅. La prueba original no alcanzaba al depredador (corría 1500 pasos con el depredador desde el paso 2000). Se corrigió para que actúe dentro de la prueba, y el determinismo también se verificó aparte.
- C4: 70 pasos/s con 1394 organismos aquí; 257 en el equipo local. ✅
- C2 y C3 también aprobados en el equipo local.

## Hipótesis

| # | Estatus | Resultado (semillas 11–20 / 31–40 + réplica 21–30) |
|---|---|---|
| **P1** (brusco) | Prerregistrada (versión 2) | ❌ **No cumplida.** Núcleo: sobreviven 6/10, > 0,5 en 4/6. Réplica: sobreviven 9/10, > 0,5 en 7/9 (0,778, bajo el 80 %). **Combinado: sobreviven 15/20, > 0,5 en 11/15 (73 %)**, media 0,67. |
| P2 | Prerregistrada | ✅ Depredador uniforme: ~0,2 % en refugio en todas las sobrevivientes (combinado 11/20 sobreviven con brusco; 20/20 con rampa). |
| P3 | Prerregistrada | ✅ Protección aleatoria: ~0,2–0,3 % (20/20 en ambos). Lectura acotada: ver el punto 2 abajo. |
| **P1-rampa** | **Hipótesis nueva**, formulada después de que P1 fallara, prerregistrada antes de correr y con semillas nuevas | ✅ **Replicada.** Semillas 31–40: 10/10 sobreviven, 9/10 > 0,5. Semillas 21–30: 10/10 sobreviven, 9/10 > 0,5 (media 0,79). **Combinado: 20/20 sobreviven, 18/20 > 0,5 (90 %)**, media 0,78. |
| P4 | Prerregistrada (dosis; solo semillas 21–30) | ⚠️ **Parcial.** Intensidad 0,0175: ✅ 9/9 sobrevivientes > 0,5 (media 0,90; la asociación cruza el 50 % entre los pasos 2400 y 4200 en todas). Intensidad 0,0125: ❌ 7/9 (media 0,68; una semilla sin grupos, 0,005, y otra en 0,32). |

Intervalos: con 18/20 el intervalo binomial aproximado de P1-rampa es 68–99 %; con 11/15, el de P1 brusco es 45–92 %. El contraste con los controles (0,78 contra 0,002–0,003, pareado con los mismos sorteos del depredador) sigue sin problema de ruido.

**Exploratorios de las semillas 21–30**

| Condición | Sobreviven | > 0,5 | En refugio (media) | Lectura |
|---|---|---|---|---|
| refugio 3 (un par queda protegido solo a medias) | 8/10 | 0/8 | 0,001 | **No evoluciona.** Si un par solo reduce el riesgo a la mitad, no alcanza para pagar los costos de estar unido |
| sin división unida (solo unirse crea enlaces) | 8/10 | 0/8 | 0,15 | La unión activa aparece (gen en ~30–50 % de la población en 5 semillas) pero protege poco. Los enlazados **no son parientes**: distancia de etiqueta 0,155, igual que al azar (0,134) |
| población media al final | | | | sin depredador 1168, aleatorio 1047, rampa 857, refugio 787, uniforme 411 |

![mundo con depredador gradual: casi todos en pares](img/2026-10-24-fase2c-rampa-mundo.png)
![métricas](img/2026-10-24-fase2c-rampa-metricas.png)

## Lo que muestran los datos
1. **Con un depredador limitado por tamaño que aparece gradualmente, a intensidad 0,015, la asociación evoluciona sola desde LUCA** (P1-rampa, replicada con 20 semillas). Es la primera condición del proyecto en la que asociarse se impone. Con aparición brusca la prueba prerregistrada falló (73 % contra el 80 % exigido). La robustez a la dosis es **parcial**: a 0,0175 la asociación aparece en todas las semillas y rápido; a 0,0125, en el 78 %. La robustez al valor de la rampa no se probó.
2. **Lo que se puede afirmar sobre la causa.** La protección tiene que **depender de estar unido**:
   - la mortalidad alta por sí sola no basta: el depredador uniforme, con la misma tasa de ataque y los mismos sorteos, no produce grupos (P2);
   - una protección que no depende de los enlaces tampoco: el control aleatorio no produce grupos (P3).
   
   **El control aleatorio no iguala la protección.** Mientras se decide la selección, `refugio` sufre una depredación parecida a la de `uniforme`, y mucho mayor que la de `aleatorio`. Muertes por depredación por cada mil organismos-paso (rampa, 10 semillas):

   | Pasos | refugio | aleatorio | uniforme |
   |---|---|---|---|
   | 2000–6000 | 2,8–3,4 | 0,36–0,38 | 3,1–3,5 |
   | 6000–10 000 | 1,6–10,7 | 1,1 | 11,0–11,6 |
   | 22 500–30 000 | 0,6–9,9 (mediana ~3,7) | 1,5 | ~15 |

   Por eso la población de `aleatorio` (~950) se parece a la de una población sin depredador. Un control que iguale la mortalidad realizada (muertes al azar en la misma cantidad que en `refugio`) queda pendiente.
3. **Los enlazados son parientes cercanos.** La distancia de etiqueta entre enlazados es 0,015, contra 0,12 entre pares al azar, y en 9 de 10 semillas la división unida está en ≥ 99 % de la población. La etiqueta muta de forma independiente del resto del genoma, así que esto indica parentesco reciente, no que sean clones.
4. **Dos rutas hacia los grupos. Primero se vio en una semilla, verificada con el origen de los enlaces:** en la semilla 32, los grupos se forman por **unión activa** con vecinos y no por división unida. Se repitió la corrida con un contador del origen de cada enlace (la misma semilla reproduce la trayectoria):

   | Semilla | Enlaces por unión activa (último cuarto) | Por división unida | En refugio (final) |
   |---|---|---|---|
   | 31 (típica) | 90 (1,5 %) | 5809 (98,5 %) | 0,96 |
   | 32 | **7732 (98,6 %)** | 107 (1,4 %) | 0,40 |

   En la 32, la división unida llegó al 50 % hacia el paso 6000 y después se perdió.

   **En las semillas 21–30 la segunda ruta reaparece.** Aquí no se corrió el contador de origen; la ruta se infiere del genoma (gen de unirse en la mayoría y dividirse unido casi ausente):

   | Condición y semilla | Con gen de unirse | Con dividirse unido | En refugio |
   |---|---|---|---|
   | refugio, 28 | 29 % | 4 % | 0,26 |
   | p0125, 26 | 82 % | 1 % | 0,32 |
   | p0125, 28 | 80 % | 1 % | 0,53 |
   | rampa, 26 | 70 % | 29 % | 0,49 |

   En total, la ruta por unión activa domina en **5 de las 53 poblaciones sobrevivientes** con refugio 2 y división unida disponible (incluida la 32; en las semillas 11–20 no se revisó), y **siempre protege menos** (0,26–0,53, contra ~0,6–0,96 de la ruta por división unida). Parece más frecuente con el depredador más débil (2 de 9 en p0125, 0 de 9 en p0175), pero son pocos casos. La condición sin división unida confirma que esta ruta sola rinde poco (media 0,15) y que forma grupos de no parientes.
5. **Los grupos son mayormente pares** (tamaño medio 1,8 en la rampa, con máximos de 6 a 10 y ~5 % en grupos de 3 o más). Con refugio 2, un grupo más grande no protege más.
6. **La transición varía entre semillas.** En la rampa, la fracción de enlazados superó el 50 % entre los pasos 6000 y 21 200. Con aparición brusca, entre 2800 y 4600 en 5 de las sobrevivientes; la semilla 19 recién en el 24 400 y la 15 nunca.

## Interpretación (prudente)
- El resultado es análogo al de Boraas et al. (1998): un depredador limitado por tamaño favorece que las células hijas queden unidas. En la simulación, eso ocurre **con aparición gradual del depredador y en una ventana angosta de intensidades**.
- **Lo que hace falta para que el grupo se imponga**, según los controles y variantes: (a) que la protección dependa de estar unido (P2, P3); (b) que sea fuerte ya para un par (con refugio 3 no evoluciona nada); (c) una intensidad dentro de una ventana (0,0125–0,0175 funciona, con más éxito arriba; 0,02 extingue; ≤ 0,01 no tiene efecto); (d) mejor si el depredador llega de a poco; y (e) la división unida, que da grupos de parientes y mucha más protección que la unión activa.
- Lo emergente es **mínimo**: mayormente pares de parientes, sin división del trabajo ni coordinación compleja. Es el **primer escalón** de la transición que plantea la hipótesis. El grupo existe y paga, pero todavía no es un individuo.

## Veredicto de la fase
La fase se **cierra**. Pregunta de la fase: ¿un beneficio que depende del tamaño físico del grupo hace evolucionar la asociación desde LUCA? **Sí, con condiciones**: depredador gradual (P1-rampa, 18/20) o algo más intenso (0,0175, 9/9); no con aparición brusca a 0,015 (P1, 11/15, prerregistrada y no cumplida). Los controles descartan que baste la mortalidad o una protección cualquiera.

## Pendientes (no bloquean el cierre)
- Control de mortalidad igualada (muertes al azar en la misma cantidad que en `refugio`).
- Robustez a otro valor de rampa.
- Contador de origen de enlaces en las semillas 21–30 de la segunda ruta (hoy inferida del genoma).

## Correcciones respecto de la primera versión de esta bitácora
- Se afirmaba que el control aleatorio daba "protección de magnitud parecida": es falso (ver la tabla).
- "Dos caminos evolutivos, como en la biología" se rebajó a observación exploratoria de una semilla, y se quitó la analogía con *Volvox* y *Dictyostelium*. Después se verificó directamente con el origen de los enlaces que la semilla 32 usa unión activa.
- "Grupos clonales" pasó a "parientes cercanos".
- La rampa se presenta como hipótesis nueva, no como prueba de que P1 fallara solo por las extinciones.
- Se corrigieron números: la transición con aparición brusca no siempre fue entre los pasos 2800 y 4600; el grupo de 19 era del núcleo, no de la rampa; una extinción ocurrió en el paso 7544, no "justo después" de que apareciera el depredador.
