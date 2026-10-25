# 2026-10-25 · Fase 4b: jardín común, prerregistro

Escrito antes de correr. Antecedente: [fase 4a](2026-10-25-fase4a-evaluacion.md).

## Pregunta
¿Las diferencias de la fase 4a están en los genomas o son un efecto directo de la regla?

## Diseño (`experiments/fase4/jardin_comun.py`)
- **Poblaciones:** las finales de la fase 4a (semillas 101–110), evolucionadas `sin` restricción, con `r20` y con el control `r20a`.
- **Siembra:** 600 genomas de cada una, **sin mutación**, en dos ambientes comunes: `amb_sin` (sin restricción) y `amb_r20` (con restricción).
- **Duración:** 15 000 pasos; se mide desde el paso 3000.
- **Medición:** además de las métricas de la fase 4a, la fracción que nunca se dividió entre los miembros de borde (1 socio).
  - Dividirse unido agrega un enlace al progenitor, así que tener 2 o más socios suele implicar haberse dividido. Por eso no se usa la estratificación por interior.

## Prueba corta del script (semilla 401, poblaciones de los pilotos; orienta, no prueba)
En `amb_sin`, los genomas evolucionados con r20 tienen más miembros que nunca se dividen que los evolucionados sin restricción: 0,26 contra 0,15, y en el borde 0,47 contra 0,26. Su correlación, en cambio, no es más negativa: −0,20 contra −0,49.

## Hipótesis y reglas (pareadas por semilla, inversión de signos exacta, una cola, p < 0,05)
En cada ambiente, comparando los genomas `r20` contra los `sin` y contra los `r20a`:

| # | Predicción | Expectativa |
|---|---|---|
| G1 | La correlación avanzar/dividirse más negativa es heredada | **No:** sería mecánica |
| **G2** | **Más miembros que nunca se dividen es heredado** | **Sí** |
| G3 | Ídem entre los miembros de borde (sin el efecto de la posición) | Sí |
| G4 | La tendencia a formar grupos más grandes es heredada | Sí |

El criterio principal es **G2 y G3 en `amb_sin`**: si los genomas evolucionados con la restricción tienen más miembros que no se reproducen incluso cuando la restricción no está, la evolución produjo una diferenciación reproductiva heredable.

## Cómo se interpretará
- **G2 y G3 se cumplen en `amb_sin`:** hay un germen de división del trabajo reproductivo heredable (miembros "somáticos" que no se reproducen). Siguiente paso: medir dependencia (¿sobreviven solos?) y si la proporción de no reproductores es un rasgo del grupo.
- **Solo G4:** la restricción seleccionó una mayor tendencia a agruparse, pero no especialización.
- **Nada:** las diferencias de la fase 4a eran efecto directo de la regla.
