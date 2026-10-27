# 2026-10-27 · Fase 12, etapa 3: ¿la evolución empieza a mirar lo que le dice Claude? Prerregistro

Escrito antes de correr. Antecedente: el piloto exploratorio de [la etapa 2 y 3](2026-10-27-fase12-etapa2.md), semillas 1–4. Allí el |peso| sobre el sensor de luz fue mayor con la luz acoplada en 3/4 (media 0,83 contra 0,55); el enriquecimiento quedó cerca de 1.

## Diseño
- `python experiments/fase12/respuesta_estimulos.py --pasos 200000 --semillas 11 12 13 14 15 16 17 18 --salida runs/fase12/luz_prerregistro.json`
- **Mundo:** `experiments/configs/clima.toml` (clima real de Capitán Bermúdez, LUCA puro) con estímulos.
- **Estímulo:** cada 3000 pasos, Claude manda la frase siguiente de una conversación fija (6 frases, en ciclo); cada letra es un pulso de luz en un lugar fijo para esa letra.
- **Condiciones:**
  - acoplado: la luz hace crecer comida, `acople_luz = 0,05`;
  - desacoplado (control): misma luz, mismos lugares y pasos, `acople_luz = 0`.
- **Semillas nuevas 11–18.** 200 000 pasos (~1500 generaciones).

## Reglas (las calcula el script; prueba de permutación pareada exacta, una cola)
| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| **R1** | La selección mira la luz cuando la luz alimenta | peso_luz acoplado > desacoplado, p < 0,05 | Moderada (piloto 3/4) |
| R2 | La población se concentra en la luz | enriquecimiento acoplado > desacoplado, p < 0,05 | Baja (piloto ~1) |

Exploratorias (no se interpretan como confirmación):
- `E_peso_ruido`: deriva. Debería no diferir; si difiere, R1 se atribuye a otra cosa (por ejemplo, a la estructura de la población) y no a la luz.
- `E_avanzar_luz` y `E_comer_luz`: el signo del peso sobre la luz en los genes de avanzar y de comer. ¿Detenerse a comer en la luz, avanzar hacia ella?

Corridas extintas: se excluyen del par.

## Cómo se interpretará
- **R1 positiva y E_peso_ruido nula:** primera evidencia de que un estímulo de afuera que importa para sobrevivir es incorporado por la evolución en el genoma. Siguiente: ver el uso (ablación del sensor en poblaciones evolucionadas) y si el *contenido* del mensaje importa (texto real contra las mismas letras en orden al azar).
- **R1 negativa:** el sensor de luz es redundante con los de comida, que la luz misma hace crecer. Para que la luz informe algo propio, tendría que anticipar la comida (por ejemplo, que la comida crezca unos pasos después de la luz).
