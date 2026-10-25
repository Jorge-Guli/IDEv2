# 2026-10-25 · Fase 4c: sesgo reproductivo con modelo nulo, control de costo privado y réplica, prerregistro

Escrito antes de correr. Responde a la revisión de las fases 4a y 4b ([evaluación 4b](2026-10-25-fase4b-evaluacion.md)). Sin física nueva.

## Preguntas
1. ¿El sesgo reproductivo dentro de los grupos supera al de un modelo nulo con tasas iguales en las 10 poblaciones de la 4a, y no solo en la del piloto?
2. ¿Lo produce la ligadura entre reproducirse e inmovilizarse, o cualquier costo privado de reproducirse?
3. ¿Se replica, con semillas nuevas, que la restricción aumenta los grupos de 3 o más?
4. ¿Hay complementariedad: los que no se reproducen empujan más?

## Diseño (`experiments/fase4/evaluar_4c.py`)
- **Análisis nulo:** genomas sin mutación, ambiente común sin restricción, 8000 pasos, medición desde el paso 2000. En cada grupo de 3 o más (miembros con edad ≥ 100), cociente entre los miembros que nunca se dividieron y lo esperado si las divisiones del grupo se repartieran con tasa igual (multinomial con pesos por edad). Se calcula por tamaño de grupo y en total.
- **Parte 1:** las 10 poblaciones de la 4a (sin, r20, r20a; semillas 101–110).
- **Parte 2, réplica:** semillas nuevas, 111–120, con los ancestros en dos etapas de la 4a. Condiciones: sin, r20, r20a, **c6 y c12** (costo de dividirse 6 y 12, contra 2, sin inmovilidad). Al final, el mismo análisis nulo sobre sus poblaciones.
- No se puede igualar exactamente el costo de 20 pasos sin empujar con un costo en energía. Por eso se usan dos niveles que lo acotan.

## Prueba del script (poblaciones de los pilotos, semilla 401; orienta)
Cociente observado/esperado: sin 1,10; r20a 0,93; **r20 1,64**. Tasa de avanzar en los genomas r20: quienes nunca se dividieron 0,284, quienes sí 0,271 (sin complementariedad).

## Hipótesis y reglas (pareadas, inversión de signos exacta, una cola, p < 0,05)
| # | Predicción | Expectativa |
|---|---|---|
| **N1** (4a y réplica) | Cociente de r20 > sin y > r20a | Sí |
| N2 (descriptiva) | Complementariedad: tasa de avanzar de quienes nunca se dividieron − la de quienes sí, en r20 | ~0 (sin complementariedad) |
| **N3** (réplica) | Cociente de r20 > c6 y > c12: la clave es la ligadura con la inmovilidad | Incierta |
| N4 (réplica) | Un costo privado solo ya sube el cociente (c6, c12 > sin) | Incierta |
| **R1** (réplica) | Grupos ≥ 3: r20 > r20a, > sin, > c6, > c12 | Sí (replicar la 4a) |

## Cómo se interpretará
- **N1 y R1 sí, N3 sí:** la restricción flagelar, y no un costo cualquiera, selecciona grupos más grandes y supresión reproductiva en parte de sus miembros. Sin complementariedad, eso es un **sesgo reproductivo**, no división del trabajo. Para pasar a la división del trabajo haría falta que los no reproductores aporten otra función al grupo; ese sería el diseño de la fase siguiente.
- **N3 no (c6 o c12 igualan a r20):** basta un costo privado de reproducirse; la analogía con el flagelo no es necesaria.
- **N1 no:** el sesgo era propio de la población del piloto.
