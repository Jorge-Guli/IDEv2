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
| 3c | Movimiento por fuerza (decisión de modelo) | ▶ siguiente | El grupo se mueve con probabilidad fuerza/tamaño^α, sin umbral y sin ventaja diagonal |
| 4 | El colectivo como individuo | siguiente | — |

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
