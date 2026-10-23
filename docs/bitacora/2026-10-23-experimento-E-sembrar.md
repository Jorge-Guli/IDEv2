# 2026-10-23 · Experimento E: ¿la asociación es inestable o solo difícil de descubrir?

## Pregunta
En la fase 2 la asociación casi no apareció. ¿Es porque nunca llega a descubrirse, o porque, aunque esté, la selección la elimina?

## Diseño
- Población inicial "colonial": LUCA que se divide **quedando unido** (en lugar de dividirse suelto) y que **comparte** energía solo si tiene socios con menos energía que él. Antes de correr se verifica que el genoma se reproduzca y forme enlaces (89 % enlazados sin mutación).
- Física base (fase 2), 20 000 pasos, semillas 1 a 5.

| Condición | Qué cambia |
|---|---|
| `colonial` | adhesión real |
| `colonial_inerte` | mismos genes, pero la asociación no tiene efecto: mide la pérdida por pura deriva |
| `colonial_elastico` | sin adhesión: el enlace se rompe si se separan |
| `colonial_positivo` | compartir crea energía (eficiencia 2) |

Para reproducirlo: `python experiments/fase2/sembrar.py --salida runs/sembrar --pasos 20000 --semillas 5`

**Incidencias:**
- La primera corrida fue **inválida** por un error de diseño del genoma: compartía aunque no tuviera socios, le ganaba siempre a dividirse y la población nunca se reproducía. Se corrigió y se agregó la verificación de viabilidad.
- El **control positivo no terminó**: las poblaciones gigantes que produce la energía gratuita lo vuelven muy lento y se cortó por el límite de tiempo. No se relanzó porque el resultado ya era concluyente sin él.

## Resultados

| Condición | Con gen de división unida (paso 1000) | Con división común reaparecida (paso 1000) | Enlazados (paso 1000) | Con gen de división unida (final) |
|---|---|---|---|---|
| colonial | 0,81–0,97 | **0,72–0,96** (4 de 5) | 0,03–0,17 (una semilla 0,61) | **0,01–0,60** |
| colonial_inerte | 0,98–0,99 | 0,01–0,02 | 0 | 0,97–0,99 (4 de 5) |
| colonial_elastico | 0,97–0,98 | 0,01–0,05 | ~0 | 0,36–0,99 |

- **Con adhesión real, la división común reaparece por mutación y se impone en menos de 1000 pasos** en 4 de 5 semillas. Los enlaces se desarman y casi no quedan grupos.
- En el control inerte, donde la división unida no cuesta nada, se mantiene en el 97–99 % durante toda la corrida (salvo en una semilla, por deriva).
- En el modo elástico se pierde más despacio: el enlace se rompe solo, así que el costo de estar unido es menor.
- Compartir también se pierde (de 0,9 a ~0,01–0,4).

## Interpretación
La asociación **no es solo difícil de descubrir: es inestable**. Aunque esté presente desde el principio, la selección la elimina, porque en esta física quedar pegado cuesta (movilidad, mantenimiento) y no rinde nada a cambio.

Según la hoja de ruta, esto confirma el camino: hay que cambiar **lo que rinde** (fase 2b, condiciones ecológicas), no solo dar más tiempo para descubrirla.
