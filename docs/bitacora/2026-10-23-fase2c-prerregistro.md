# 2026-10-23 · Fase 2c: prerregistro de hipótesis

Escrito **antes** de la evaluación (`experiments/fase2c/evaluar.py`, 6 condiciones × 10 semillas × 30 000 pasos).

## Contexto
- **Física:** la base, con asociación, movimiento de grupos por empuje y un depredador limitado por tamaño. En cada paso, cada organismo es atacado con probabilidad 0,015; el ataque mata con probabilidad 1 − (tamaño − 1)/(refugio − 1), con refugio = 2, es decir, los sueltos mueren y los grupos de 2 o más quedan a salvo. Ver `experiments/configs/depredacion.toml`.
- **Calibración** (pilotos de 2 semillas): con intensidad 0,02 todo se extingue y con 0,01 o menos no hay efecto. Con 0,015 y refugio 2, desde LUCA, ~92 % de la población terminó en grupos en 2 de 2 semillas; con depredación uniforme, 0–7 %. Con refugio 3, una semilla se extinguió y la otra llegó al 30 % enlazado.
- Los pilotos sirvieron para elegir los parámetros; **la evaluación usa las semillas 1–10**, que incluyen las 2 del piloto. Por eso el criterio exige ≥ 8/10.

## Hipótesis
Medidas del último cuarto de cada corrida.

| # | Hipótesis | Predicción |
|---|---|---|
| P1 | Con refugio por tamaño, la asociación evoluciona desde LUCA | `refugio`: `frac_en_refugio` > 0,5 en ≥ 8/10 |
| P2 | La causa es el refugio, no la mortalidad | `uniforme`: `frac_en_refugio` < 0,1 en ≥ 8/10 |
| P3 | La asociación es la que protege (no otro rasgo) | `refugio_asoc_inerte`: `frac_en_refugio` = 0 y población media menor que `refugio` en ≥ 8/10 semillas pareadas |
| P4 | Asociarse aumenta la población sostenible bajo el depredador | `refugio` > `uniforme` en población, en ≥ 8/10 semillas pareadas |

**Exploratorias** (sin umbral): tamaño de los grupos (¿pasan de pares?), velocidad de la transición (paso en que se supera el 50 % de enlazados), si los grupos son clonales (distancia de etiqueta), si aparecen compartir y aprovechados, el efecto del modo de movimiento (`refugio_unanime`) y el refugio 3.

## Decisiones según el resultado
- **P1–P4 se cumplen** → primera condición identificada en la que la asociación evoluciona por sí sola. Siguiente paso: fase 3 (el colectivo como individuo), con este mundo como base. ¿Se reproducen los grupos como unidad? ¿Aparece división del trabajo?
- **P1 sí y P2 no** → la mortalidad por sí sola favorece la asociación; revisar el mecanismo antes de seguir.
- **P1 no** → los pilotos fueron casualidad; revisar la calibración (intensidad y refugio).

## Versión 2 (reemplaza a la anterior, escrita antes de la nueva evaluación)

**Por qué hay una versión 2.** La revisión científica señaló, mientras corría la primera evaluación:
- la intensidad 0,015 está al borde de la extinción, y la calibración usó las semillas 1 y 2, que también entraban en la evaluación;
- las corridas extintas se descartaban en silencio de los promedios;
- P4 era casi una tautología (con refugio siempre muere menos gente) y P3 se cumplía por construcción;
- había errores menores de código: ataques a organismos que ya morían de hambre, muertos que seguían en el empuje del grupo y un generador aleatorio compartido que impedía comparar semillas de a pares.

La evaluación se detuvo antes de terminar. **Lo que alcancé a ver** (y declaro para que conste): en esa corrida, `refugio` se había extinguido en las semillas 5 y 6 y `uniforme` sobrevivía en la semilla 3. No vi ninguna fracción en refugio de la evaluación.

**Cambios de diseño:**
- **Semillas nuevas:** 11–20 aquí y 21–30 en el equipo local. Las semillas de calibración no se usan.
- **Aclimatación:** el depredador actúa desde el paso 2000, para que la extinción inicial no domine.
- **Control nuevo, `aleatorio`:** un ataque perdona con probabilidad 0,9, sin relación con los enlaces. Es una protección parecida en magnitud, pero que no depende de asociarse.
- **Barrido de dosis:** intensidades 0,0125, 0,015 y 0,0175.
- **Exploratorios:** sin división unida (solo `unirse` crea enlaces) y refugio 3.
- **Las hipótesis las calcula el script** (`evaluar_hipotesis`). Las fracciones se evalúan sobre las corridas que sobrevivieron y las extinciones se informan aparte.

| # | Hipótesis | Regla |
|---|---|---|
| P1 | Con refugio por tamaño evoluciona la **división unida** (grupos clonales) | `refugio`: sobreviven ≥ 7/10, y `frac_en_refugio` > 0,5 en ≥ 80 % de las que sobrevivieron |
| P2 | Sin refugio, no evoluciona | `uniforme`: `frac_en_refugio` < 0,1 en ≥ 80 % de las que sobrevivieron |
| P3 | La causa es que la protección **dependa de asociarse**, no la menor mortalidad | `aleatorio`: `frac_en_refugio` < 0,1 en ≥ 80 % de las que sobrevivieron |
| P4 | El efecto no depende de un único valor de intensidad | `refugio_p0125` y `refugio_p0175`: `frac_en_refugio` > 0,5 en ≥ 80 % de las que sobrevivieron |

Se agrega la siguiente lectura: P1 mide que evolucione la división unida, un solo cambio de primitiva, análogo a las células hijas que no se separan en Boraas et al. (1998). No implica coordinación ni unión activa entre extraños; eso es lo que explora `refugio_sin_division_unida`.

## Addendum a la versión 2: aparición gradual del depredador (antes de correrlo)

**Resultado que lo motiva** (semillas 11–20, ya registrado):
- P1 no alcanzó sus umbrales: sobrevivieron 6/10 y 4 de 6 superaron 0,5. P2 y P3 se cumplieron.
- Las extinciones se concentraron justo después de que el depredador apareció de golpe en el paso 2000: el 40 % de las corridas con refugio y el 60 % de las uniformes.
- En 3 de las 4 extinciones con refugio, la asociación ya había superado el 50 % antes de la caída.

**Experimento nuevo** (semillas 31–40, que no se usaron antes): la intensidad del ataque sube linealmente de 0 a 0,015 durante 8000 pasos, a partir del paso 2000 (`depredacion.rampa = 8000`). Condiciones: `refugio_rampa`, `uniforme_rampa` y `aleatorio_rampa`.

**Hipótesis**, con las mismas reglas que P1–P3:
- **P1-rampa**: sobreviven ≥ 7/10 y `frac_en_refugio` > 0,5 en ≥ 80 % de las que sobreviven.
- **P2-rampa** (uniforme) y **P3-rampa** (aleatorio): `frac_en_refugio` < 0,1 en ≥ 80 % de las que sobreviven.

**Interpretación prevista:** si P1-rampa se cumple, el fallo de P1 se debió a la brusquedad de la aparición del depredador y no al mecanismo. El veredicto de P1 original **no cambia**: queda registrado como no cumplido.
