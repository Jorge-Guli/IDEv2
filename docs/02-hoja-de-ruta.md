# Hoja de ruta viva

Este documento es **el camino que sigue el proyecto, en orden**, con el porqué de cada paso y qué resultado haría cambiar de rumbo. Se actualiza en cada decisión; el registro de decisiones al final muestra cómo y por qué cambió. La tabla resumida de fases está en [`01-metodologia.md`](01-metodologia.md#3-hoja-de-ruta); el detalle de cada fase cerrada, en `openspec/changes/archive/`, y sus resultados, en [`bitacora/`](bitacora/).

## Dónde estamos

| # | Paso | Estado | Resultado principal |
|---|---|---|---|
| 1 | Evolución básica | ✅ cerrada | La base evoluciona y se adapta; la evolución "inventó" el giro ([bitácora](bitacora/2026-10-23-fase1-evaluacion.md)) |
| 2 | Asociación (unirse, compartir, dividirse unido, conjugar) | ✅ cerrada | Poder asociarse **no alcanza**: no rinde y la selección la purga. Si rinde, hay una transición abrupta ([bitácora](bitacora/2026-10-23-fase2-evaluacion.md)) |
| E | Sembrar la asociación | ✅ hecho | La asociación es **inestable**: aunque esté, la división común reaparece en menos de 1000 pasos ([bitácora](bitacora/2026-10-23-experimento-E-sembrar.md)) |
| 2b | Bien público: enzimas y recurso complejo | ✅ cerrada | Hay dilema: con bien privado la secreción evoluciona sola; con bien público, no. Pero **asociarse no la rescata**: el parentesco espacial (hijos al lado) ya cumple esa función ([bitácora](bitacora/2026-10-23-fase2b-evaluacion.md)) |
| 2c | Depredación limitada por tamaño | ✅ cerrada | **La asociación evoluciona sola desde LUCA** cuando el depredador solo puede comer sueltos y llega de a poco: 20/20 sobreviven y 18/20 viven mayormente en pares de parientes. No aparece con depredador uniforme ni con protección aleatoria. Con aparición brusca la prueba prerregistrada falló (11/15); a intensidad 0,0175 funciona en 9/9 y a 0,0125 en 7/9. Si un par solo queda protegido a medias, no evoluciona ([bitácora](bitacora/2026-10-24-fase2c-evaluacion.md)) |
| 3 | Coordinación del grupo (percepción del rumbo de los socios, señales) | ✅ cerrada | **La evolución alinea, pero no sincroniza.** Con percepción del rumbo, la alineación entre socios evoluciona (9/10), pero los grupos no crecen (0/10). Las señales no despegan. Con movimiento fácil, los grupos crecen (10/10): el techo es el movimiento del grupo. El genoma actual podría sincronizar un trío sin memoria ([bitácora](bitacora/2026-10-24-fase3-evaluacion.md)) |
| 3b | Prueba de invasión: ¿la física premia a un trío coordinado? | ✅ hecha | **Casi no.** "Seguir al que empuja" da una ventaja débil solo cuando el depredador exige tríos (presente al final en 4/10 semillas contra 0/10 con refugio 2); no invade de forma confiable. Alinearse es perjudicial: girar cuesta pasos. El valle está en la regla de movimiento ([bitácora](bitacora/2026-10-24-fase3b-evaluacion.md)) |
| 3c | Movimiento por fuerza (decisión de modelo) | ✅ cerrada | Con "fuerza" y α = 0,5, **la percepción de los socios aumenta la fracción en grupos de 3 o más** (réplica con 20 semillas nuevas: 16/20 contra 7/20 barajado; prueba pareada p ≈ 0,002). Con "empuje", 0/30. Se adopta "fuerza" con α = 0,5. Falta probar que el mecanismo sea la coordinación ([bitácora](bitacora/2026-10-24-fase3c-replica-evaluacion.md)) |
| 3d | Ablación y sensibilidad | ✅ hecha | La información sobre el rumbo **actúa en vida**: sin ella, los mismos genomas forman menos grupos (p = 0,002) y sostienen un 9 % menos de organismos. La alineación es **heredada** (no aprendida). Todo el efecto es del rumbo: las señales nunca se emitieron. Se repite con α = 1/3 y, débil, con α = 0,75 ([bitácora](bitacora/2026-10-24-fase3d-evaluacion.md)) |
| 4a | Restricción flagelar (dividirse impide empujar un tiempo) | ✅ cerrada | Frente a un control con la misma inmovilidad al azar, deja **cambios heredables**: el doble de grupos de 3 o más y miembros que no se reproducen aunque tienen espacio y energía (jardín común; modelo nulo en una población). **No hay complementariedad:** los no reproductores no empujan más; es supresión reproductiva, no división del trabajo ([4a](bitacora/2026-10-25-fase4a-evaluacion.md), [4b](bitacora/2026-10-25-fase4b-evaluacion.md)) |
| 4c | Modelo nulo en 20 poblaciones, control de costo privado, réplica | ✅ hecha | **Corrige a la 4b:** no hay sesgo reproductivo más allá del azar (el del piloto era de una sola población); lo que se seleccionó es dividirse menos. **Se replica que la restricción favorece los grupos** frente a no tenerla y frente a un costo de dividirse (p ≤ 0,008); frente a la inmovilidad al azar, p = 0,08. Sin división del trabajo ([bitácora](bitacora/2026-10-25-fase4c-evaluacion.md)) |
| 5 | Retornos crecientes a la especialización y energía compartida | ⏸ explorada | **Sin división del trabajo** en ninguna combinación (pilotos): la maquinaria por uso corre a todos hacia comer. El diagnóstico apunta a un conflicto entre niveles (el aprendizaje individual premia comer), a la falta de estados internos estables y a poco tiempo evolutivo (~250 generaciones) ([exploración](bitacora/2026-10-25-fase5-exploracion.md)) |
| 6 | Memoria interna (paso C) y corridas largas (paso D) | ✅ cerrada | **La memoria nunca se usó** en 940–2750 generaciones; sin diferenciación. En corridas largas, con retornos crecientes, los grupos se pierden en 3 de 5 semillas. Una estrategia reactiva alcanza en este mundo ([bitácora](bitacora/2026-10-25-fase6-evaluacion.md)) |
| 7 | Un mundo que exija memoria (estaciones, pista, toxicidad diferida) | ✅ cerrada | **La memoria de la pista no evolucionó** (~1000 generaciones). Los organismos encontraron atajos: aprender en vida, probar y retirarse, selección espacial. Para usar la pista hace falta una regla no lineal que el genoma no encuentra. En el control, la memoria se fijó integrando experiencia (2/6) ([exploración](bitacora/2026-10-25-fase7-exploracion.md), [resultados](bitacora/2026-10-26-fase7-evaluacion.md)) |
| 7b | ¿El mundo de la fase 7 premia la memoria? (invasión y competencias) | ✅ hecha | Sí, pero poco: un LUCA con memoria le gana a LUCA (8/8), y una población evolucionada sin memoria le gana a él (8/8). La memoria es un extra marginal, no algo esencial ([bitácora](bitacora/2026-10-26-fase7b-invasion.md)) |
| 8 | Un mundo donde la memoria sea esencial (mosaico fino) | ✅ cerrada | **La memoria no evolucionó en ~3000 generaciones** aunque es la única forma de pasar del azar y paga mucho: el límite es el genoma (cinco genes coordinados), no el mundo ([bitácora](bitacora/2026-10-26-fase8-evaluacion.md)) |
| 9 | Regulación genética condicionada (genes que se expresan según el estado interno) | ✅ cerrada | **La memoria sigue sin evolucionar** (~1800 generaciones, 8 semillas), aun sembrando el gen de memoria. El módulo regulado gana siempre si se arma a mano, y existe un camino gradual, pero su primer peldaño (una memoria sin uso) no se premia y se borra por deriva. Los genes condicionados se difunden como interruptores heredables ([prerregistro](bitacora/2026-10-26-fase9-prerregistro.md), [evaluación](bitacora/2026-10-26-fase9-evaluacion.md), [estado del arte](05-estado-del-arte.md)) |
| 10 | Peldaños para la memoria: cerrojo, rampa de la pista, digestión inducible | ✅ cerrada | **Primera memoria sostenida por selección:** con digestión inducible (con inercia, para bloquear el atajo de "recordar" el tipo de la celda) y cerrojo, un gen de memoria **sembrado** se retiene ~1350–2000 generaciones en 6 de 8 semillas, y la memoria coincide con la estación en el 96–99,6 % de los organismos (0/8 sin inducción, p = 0,008). No evoluciona desde LUCA, no se demostró contra el control sin información, y no se usa para decidir. Revisión independiente incorporada ([prerregistro](bitacora/2026-10-26-fase10-prerregistro.md), [evaluación](bitacora/2026-10-26-fase10-evaluacion.md)) |
| 11 | Modulación por el estado interno (y decisión estocástica) | ✅ cerrada | La memoria se mantiene ~2000 generaciones más, pero **no se recluta para decidir**, ni con modulación ni con softmax. Explicación alternativa de la revisión: la **tasa de mutación había colapsado** de 0,02 a ~0,0006 (en un mundo estable, la selección la baja). La saturación general de los genes no se confirmó ([prerregistro](bitacora/2026-10-26-fase11-prerregistro.md), [evaluación](bitacora/2026-10-26-fase11-evaluacion.md)) |
| 12 | **Universo vivo:** modo continuo, datos reales, interfaz para estimularlo, depredación evolucionada, archipiélago | ▶ siguiente | Que el ambiente no deje de cambiar ([diseño](06-universo-vivo.md)) |
| S | **Salvaguardas evolutivas** (pregunta del usuario) | idea | ¿Cuánto dura una salvaguarda? Comparar un interruptor de muerte escrito en el genoma con una dependencia física (replicarse requiere un recurso que solo da el anfitrión), midiendo cuánto tardan en aparecer mutantes que escapan. Predicción: la genética se rompe y la física no |
| H | **Horizonte: simbiosis humano–organismo** (visión del usuario) | horizonte | Una inteligencia que crece con su usuario en su dispositivo, en lugar de un modelo entrenado y congelado. Para que acompañe y no compita, el bienestar o las interacciones del usuario tendrían que ser parte del ambiente que nutre a los organismos (como en la domesticación). Siempre en modo solo lectura y dentro de un entorno aislado |
| U | **Universos abiertos** (propuesta del usuario) | → fase 12 | Desarrollado en [06-universo-vivo.md](06-universo-vivo.md) |

## El camino, en orden

### Paso E: ¿la asociación es inestable o solo difícil de descubrir?
**Experimento:** empezar con organismos "coloniales" (se dividen quedando unidos y comparten con el socio hambriento) y medir si la evolución conserva o pierde esos genes, contra los mismos controles de la fase 2.
- **Si se pierde** (lo esperado): el problema es que no rinde → seguir con 2b, que cambia lo que rinde.
- **Si se conserva**: el problema era descubrirla → priorizar el paso D (más tiempo evolutivo) y el C (genoma más expresivo) antes que la ecología.

### Paso 2b: bien público (enzimas y recurso complejo)
**Por qué esta condición primero.** Es el caso mejor documentado en la biología de cómo la cooperación favorece la agrupación. Las levaduras que digieren sacarosa liberan una enzima (invertasa) al medio; el alimento que producen queda disponible **para cualquiera cerca**, incluidos los que no la fabrican (aprovechados). Las que crecen en grupos clonales retienen más del beneficio, y esa es una de las explicaciones propuestas para el paso a la multicelularidad (Gore et al. 2009; Koschwanez et al. 2011).

**Física nueva** (ninguna regla premia la asociación):
- Un **recurso complejo**, abundante, que nadie puede comer directamente.
- Una primitiva **secretar** (costosa), que libera enzima en la propia celda. La enzima se difunde un poco y se degrada.
- La enzima **convierte recurso complejo en recurso simple**, que puede comer cualquiera.
- El recurso simple directo se vuelve escaso, para que el complejo importe.

**Preguntas:**
1. ¿Evoluciona la secreción?
2. ¿Aparecen aprovechados que no secretan?
3. ¿La asociación (grupos clonales, adhesión) pasa a rendir porque retiene el bien público entre parientes?

**Controles:** secreción desactivada (el recurso complejo queda inutilizable), asociación desactivada o inerte, y el control positivo de la fase 2.

**Qué haría cambiar de rumbo:**
- La secreción evoluciona pero la asociación no → probar con una enzima de difusión más local o más larga, o pasar a la condición de depredación.
- Nada de esto evoluciona → revisar la expresividad del genoma (paso C).
- **La asociación rinde → paso 3.**

### Pasos siguientes (tentativos; dependen de 2b)
| Orden | Paso | Cuándo |
|---|---|---|
| 3 | **El colectivo como individuo**: reproducción del grupo (fragmentación o brote), especialización y dependencia | si en 2b la asociación se sostiene |
| B | **Comunicación**: señales y memoria interna | si los grupos existen pero no se coordinan (por ejemplo, no pueden moverse juntos) |
| C | **Genoma más expresivo**: regulación entre genes y estados internos | si el límite es descubrir combinaciones de conductas |
| D | **Escala**: optimización y corridas largas en GPU | en paralelo, cuando un experimento lo necesite |
| F | **Herramientas de observación**: visor en vivo, genealogías | en paralelo, cuando haga falta entender un fenómeno |
| 2c | Otras ecologías (depredación, parches efímeros) | si el bien público no alcanza, o para comprobar si el resultado se generaliza |
| 4–6 | Comunicación compleja, asociación entre colectivos, problemas que exijan anticipación | más adelante |
| — | Mundo 3D | solo si una fase lo justifica |

## Registro de decisiones
| Fecha | Decisión | Por qué |
|---|---|---|
| 2026-10-23 | Usar OpenSpec + ODD + criterios numéricos por fase | Ver `01-metodologia.md` |
| 2026-10-23 | Agregar adhesión y movimiento de grupo a la fase 2 | La revisión mostró que la física inicial hacía imposible sostener un grupo |
| 2026-10-23 | Cerrar la fase 2 con resultado "la asociación no rinde" e insertar la fase 2b antes de la 3 | Los controles (inerte, sin beneficio, positivo) descartan bug, falta de detección y sesgo mutacional |
| 2026-10-23 | Hacer primero el experimento E (sembrar) | Es barato y decide entre "inestable" y "difícil de descubrir", que llevan a caminos distintos |
| 2026-10-23 | En 2b, empezar por el bien público (enzimas) | Es el mecanismo más documentado y abre a la vez cooperación, aprovechados y agrupación clonal |
| 2026-10-23 | Recalibrar el bien público antes de evaluarlo | La revisión mostró que secretar rendía de 50 a 150 veces su costo: no había dilema |
| 2026-10-23 | Agregar el movimiento por empuje colectivo (opcional) | Las colonias morían inmóviles; en biología, las colonias se mueven por la suma de los empujes de sus células |
| 2026-10-23 | Repetir H2 y H3 con un genoma secretor viable | El primero secretaba en exceso y colapsaba con o sin colonias: confundía el resultado |
| 2026-10-24 | Rediseñar 2c tras la revisión (semillas nuevas, aclimatación, control aleatorio, hipótesis en el script) | Riesgo de sesgo por calibrar con semillas evaluadas y de extinciones descartadas en silencio |
| 2026-10-24 | Probar el depredador gradual (prerregistrado como addendum) | P1 falló por extinciones al aparecer el depredador de golpe; la rampa confirmó el mecanismo sin cambiar ese veredicto |
| 2026-10-23 | Cerrar 2b y pasar a depredación limitada por tamaño (2c) | El bien público no hace rendir la asociación porque el parentesco espacial ya lo resuelve; hace falta un beneficio que dependa del tamaño físico del grupo (Boraas 1998; Herron 2019) |
| 2026-10-24 | Cerrar 2c y pasar a la fase 3 sobre la ecología de depredación gradual | P1-rampa se replicó con 20 semillas y los controles descartan mortalidad y protección inespecífica; los grupos existen pero son pares sin coordinación: falta que el grupo sea la unidad que se reproduce |
| 2026-10-24 | Hacer de la coordinación (paso B) la fase 3, antes del colectivo como individuo | La exploración mostró que el techo de tamaño es la coordinación del movimiento: era la condición prevista para el paso B |
| 2026-10-24 | Cerrar la fase 3 y hacer una prueba de invasión antes de tocar la física | H2 refutada. La revisión mostró que el genoma ya puede sincronizar un trío: hay que saber si la física premia la coordinación antes de cambiar la regla de movimiento (evita elegir la física hasta obtener el resultado esperado) |
| 2026-10-24 | Cambiar la regla de movimiento de grupos (modo "fuerza"), prerregistrado como decisión de modelo | 3b mostró que la física actual casi no premia la coordinación; la regla de umbral crea el valle. Se mide aparte cuánto aporta la física y cuánto la información (controles base y barajado) |
| 2026-10-24 | Adoptar "fuerza" con α = 0,5 y hacer la fase 3d antes de la fase 4 | La réplica confirmó el efecto de la información, pero la revisión mostró que el mecanismo (coordinación, rumbo, herencia) y la dependencia de α no están probados |
| 2026-10-24 | Pasar a la fase 4 con "fuerza" (α = 0,5) y percepción del rumbo | La fase 3d confirmó que la percepción del rumbo actúa en vida, que la alineación es heredada y que el efecto vale para α de 1/3 a 0,5 |
| 2026-10-25 | Cerrar la 4a como "sesgo reproductivo heredable" (no división del trabajo) y hacer la 4c | La revisión mostró que la métrica era de hojas, que no hay complementariedad y que faltaba un control de costo privado |
| 2026-10-25 | Cerrar la fase 4 y pasar a retornos crecientes a la especialización | La 4c mostró que la restricción flagelar favorece los grupos pero no produce especialización; falta la condición de convexidad de la teoría |
| 2026-10-25 | No prerregistrar la física de la fase 5 tal cual; proponer el paso C (estado interno) | Los pilotos no muestran señal y el diagnóstico apunta a límites del modelo |
| 2026-10-25 | Cambiar de eje: un mundo que exija memoria (fase 7) | La fase 6 mostró que la memoria no se usa si el mundo no la recompensa; la división del trabajo no apareció con todos los ingredientes teóricos |
| 2026-10-26 | Ampliar la regulación genética (fase 8) | La fase 7 y las fases 3b, 5 y 6 apuntan al mismo límite: el genoma no combina entradas de forma no lineal con facilidad |
| 2026-10-26 | Anotar la línea "universos abiertos" | Propuesta del usuario: universos distintos por dispositivo, conectados o no, con entradas reales y un sustrato en Docker |
| 2026-10-26 | Fase 9: genes condicionados al estado interno | La fase 8 mostró que, aun con un premio grande, la evolución no cruza el valle de cinco genes coordinados; el límite es la arquitectura del genoma |
| 2026-10-26 | Fase 10: peldaños para la memoria | La fase 9 y la literatura (Avida) indican que falta un primer paso premiado; la regla ya cabe en el genoma |
| 2026-10-26 | Fase 11: modulación por el estado interno | La fase 10 logró la memoria, pero el segundo peldaño choca con un valle de magnitud: encender o apagar un gen de ±1 no tuerce decisiones saturadas |
| 2026-10-26 | Corregir la fase 10 tras la revisión independiente ("sostenida por selección", 6 de 8, métrica corregida) | El gen estaba sembrado, P2 no se cumplió y la métrica tenía aliasing de muestreo |
| 2026-10-26 | Fase 12: universo vivo | Propuesta del autor. En mundos fijos la evolución se estanca y baja su propia tasa de mutación; un ambiente que cambia siempre (datos reales, otros organismos) ataca ese límite |
