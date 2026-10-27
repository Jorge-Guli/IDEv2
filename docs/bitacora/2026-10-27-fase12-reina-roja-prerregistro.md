# 2026-10-27 · Fase 12, etapa 4: depredación evolucionada (Reina Roja), prerregistro

Escrito antes de correr.

## Qué cambia
Primitiva `atacar` (`ataque.*`, apagada por defecto):
- quita `fuerza` de energía al organismo de enfrente, dividida por (1 + sus enlaces): asociarse defiende;
- el atacante gana `eficiencia` × lo quitado (pérdida trófica);
- si varios atacan al mismo y no alcanza su energía, se reparte en proporción, y el muerto ya no actúa en ese paso.

Sin ataque, las dinámicas no cambian (huellas idénticas).

## Verificaciones previas (no entran en la evaluación)
- **Duelo sin mutación** (`experiments/fase12/duelo_ataque.py`, mundo vivo.toml, 30 000 pasos, 8 semillas): LUCA con un gen que ataca cuando tiene a alguien enfrente, contra LUCA con el gen en cero.
  - Gana en 7/7 con eficiencia 0,6 y 0,9, y en 5/7 con 0,3. **La física premia atacar.**
  - La población cae a 5–114 (sin ataque, ~280): un depredador puro se come a sí mismo.
- **Exploratorio desde LUCA con mutación** (200 000 pasos, semillas 1–2; costo 0,3, fuerza 10, eficiencia 0,6):
  - el ataque evoluciona solo en < 19 000 pasos (58–87 % con el gen);
  - semilla 2: los depredadores llegan al 99 % y se extinguen;
  - semilla 1: ciclos (0,58 → 0,003 → 0,39 → 0,26 → 0), con tasa de mutación 2–4 veces más alta que los controles mientras duran.
- **Barrido** (120 000 pasos, semillas 1–4):

| Variante | Resultado |
|---|---|
| fuerza 5 | el ataque se pierde en 3/4 |
| eficiencia 0,3 | se pierde en 3/4 |
| fuerza 5 y costo 1,0 | se pierde en 4/4 |
| **costo 1,0** (adoptado) | **persiste sin extinciones en 4/4** (gen en 0,73–0,99 al final) |

## Diseño
- `python experiments/fase12/reina_roja.py --pasos 300000 --semillas 21 22 23 24 25 26 27 28 --set ataque.costo_atacar=1.0 --procesos 8 --salida runs/fase12/reina_roja_prerregistro.json`
- **Mundo:** `experiments/configs/vivo.toml` (fase 11, desde LUCA puro), con mutación.
- **Condiciones:**
  - `ataque`: atacar existe, costo 1,0;
  - `sin`: sin depredación;
  - `fijo`: el depredador fijo de la fase 2c, con rampa de 20 000 pasos.
- **Semillas nuevas 21–28; 300 000 pasos.** Las medidas son la media del último tercio (pasos ≥ 200 000).

## Reglas (las calcula el script; permutación pareada exacta, una cola; las extinguidas se excluyen del par)
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| **R1** | Con un ambiente que evoluciona, la tasa de mutación no colapsa | tasa efectiva `ataque` > `sin`, p < 0,05 | Moderada |
| R2 | Se mantiene más diversidad de genomas | perfiles distintos `ataque` > `sin`, p < 0,05 | Moderada |
| R3 | La depredación evolucionada es sostenible | extinciones de `ataque` ≤ 2 de 8 | Moderada |
| R4 | Un depredador que evoluciona empuja más que uno fijo | tasa efectiva `ataque` > `fijo`, p < 0,05 | Baja |

Exploratorias: si el ataque sigue presente al final (`tiene_atacar`) y el tamaño del genoma (`genes_medios`).

## Cómo se interpretará
- **R1 y R3 positivas:** la coevolución mantiene abierta la evolución (no se estanca la variación), que es la condición necesaria que faltaba en las fases 6–11. Siguiente: el universo continuo con ataque y clima, y ver si con esa presión sí se recluta la memoria o la asociación (defensa por enlaces).
- **R1 positiva, R2 negativa:** más mutación sin más diversidad: la presión sostiene la variación, pero la selección la recorta.
- **Negativo:** la depredación se estabiliza en un equilibrio (un nuevo mundo fijo) y la evolución se estanca igual. Habría que hacer que las defensas y los ataques tengan más grados de libertad (por ejemplo, ataque dirigido por la etiqueta del otro o defensa química), para que la carrera no termine.
