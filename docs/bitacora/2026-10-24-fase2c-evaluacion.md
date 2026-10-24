# 2026-10-24 · Fase 2c: depredación limitada por tamaño, resultados

Hipótesis y reglas prerregistradas en [`2026-10-23-fase2c-prerregistro.md`](2026-10-23-fase2c-prerregistro.md): versión 2 y su addendum, ambos escritos antes de cada corrida. Las hipótesis las evalúa el propio script (`experiments/fase2c/evaluar.py`, `evaluar_hipotesis`).

## Configuración
- `experiments/configs/depredacion.toml`: física base con asociación y movimiento de grupos por empuje.
- Depredador: ataque con probabilidad 0,015 por organismo y paso. El ataque mata con probabilidad 1 − (tamaño − 1)/(refugio − 1), con refugio 2: los sueltos mueren y los grupos de 2 o más quedan a salvo. Aclimatación de 2000 pasos.
- **Núcleo** (aparición brusca): semillas 11–20. Informe: [`2026-10-24-fase2c-nucleo-informe.json`](2026-10-24-fase2c-nucleo-informe.json).
- **Rampa** (la intensidad sube durante 8000 pasos): semillas 31–40. Informe: [`2026-10-24-fase2c-rampa-informe.json`](2026-10-24-fase2c-rampa-informe.json).
- Las semillas 1 y 2 se usaron para calibrar y no entran en ninguna evaluación. Las semillas 21–30 (dosis y exploratorios) se corren en el equipo local y se agregan cuando estén.

## Criterios
- C1: 6/10 en el núcleo, ❌; 10/10 en la rampa.
- C2, invariantes: 0 violaciones en 415 000 enlaces revisados, y ningún organismo en un grupo refugio murió por un ataque. ✅
- C3, reproducibilidad. ✅
- C4, rendimiento: 70 pasos/s con 1394 organismos. ✅

## Hipótesis

| # | Aparición brusca (11–20) | Rampa (31–40) |
|---|---|---|
| **P1.** Con refugio evoluciona la asociación (sobreviven ≥ 7/10 y > 0,5 en refugio en ≥ 80 % de las que sobreviven) | ❌ Sobreviven 6/10; > 0,5 en 4/6 (0,45 / 0,08 / 0,79 / 0,75 / 0,65 / 0,52) | ✅ **Sobreviven 10/10; > 0,5 en 9/10** (media 0,77, hasta 0,96) |
| **P2.** Depredador uniforme: < 0,1 | ✅ 4/4 sobrevivientes (~0,1 %) | ✅ 10/10 (~0,1 %) |
| **P3.** Protección aleatoria (90 %, sin relación con los enlaces): < 0,1 | ✅ 10/10 (~0,2 %) | ✅ 10/10 (~0,2 %) |

El veredicto de P1 con aparición brusca **queda como no cumplido**. La rampa no lo reemplaza: muestra que la falla se debió a las extinciones al aparecer el depredador de golpe (40 % con refugio y 60 % con depredador uniforme). En 3 de las 4 extinciones con refugio, la asociación ya había superado el 50 % antes de la caída.

![mundo con depredador gradual: casi todos en pares](img/2026-10-24-fase2c-rampa-mundo.png)
![métricas](img/2026-10-24-fase2c-rampa-metricas.png)

## Lo que muestran los datos
1. **La asociación evoluciona sola desde LUCA** cuando hay un depredador que no puede comer grupos. Es la primera condición del proyecto en la que asociarse rinde y se impone.
2. **La causa es que la protección dependa de estar unido, no la menor mortalidad.** Con una protección de magnitud parecida pero aleatoria (`aleatorio`), la asociación no aparece (0,2 %), aunque la población es incluso mayor (~950 contra ~750).
3. **Los grupos son clonales.** La distancia de etiqueta entre enlazados es 0,015, contra 0,12 entre pares al azar. Nacen de la división unida, que llega al 99 % en 9 de 10 semillas.
4. **Dos caminos evolutivos, como en la biología.**
   - **Clonal** ("quedarse juntos", como *Volvox*): en 9 de 10 semillas, la división unida (un solo cambio de primitiva).
   - **Agregativo** ("juntarse", como *Dictyostelium*): en la semilla 32, la división unida no se impuso (2,5 %). En su lugar evolucionó la **unión activa con vecinos** (el gen de unirse llegó al 40–60 %), con socios solo parcialmente emparentados, y alcanzó un 35 % en refugio.
5. **Los grupos son mayormente pares** (tamaño medio 1,8), porque con refugio 2 un grupo más grande no protege más. Aparecen grupos de hasta 19, pero son raros (~5 % de la población en grupos de 3 o más).
6. **La transición lleva tiempo y varía entre semillas.** La fracción de enlazados superó el 50 % entre los pasos 6000 y 21 200 en la rampa, y entre 2800 y 4600 con aparición brusca.

## Interpretación (prudente)
- Esto reproduce en la simulación el resultado de Boraas et al. (1998): **un depredador limitado por tamaño basta para que evolucionen grupos**, y el control aleatorio descarta que la causa sea solo la menor mortalidad.
- Lo emergente es todavía **mínimo**: mayormente pares clonales, sin división del trabajo ni coordinación compleja. Es el **primer escalón** de la transición que plantea la hipótesis. El grupo existe y paga, pero todavía no es un individuo.
- La aparición de las dos vías (clonal y agregativa) es un resultado exploratorio de una sola semilla. Vale la pena estudiarla.

## Pendiente
- Semillas 21–30 en el equipo local: barrido de dosis (P4), refugio 3 y la condición sin división unida.
- Revisión de esta interpretación con el `revisor-cientifico` antes de archivar la fase.
