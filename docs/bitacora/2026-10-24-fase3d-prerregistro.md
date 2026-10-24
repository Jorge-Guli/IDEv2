# 2026-10-24 · Fase 3d: ablación y sensibilidad, prerregistro

Escrito antes de correr. Responde a la revisión de la fase 3c ([réplica](2026-10-24-fase3c-replica-evaluacion.md)). No hay física nueva: es un experimento diagnóstico, como el E y la 3b, y no tiene cambio de OpenSpec.

## Preguntas
1. ¿La información sobre los socios actúa en vida? ¿O lo que importa es lo que la población evolucionó con ella?
2. ¿Hace falta para formar los grupos, para mantenerlos, o solo para alinearse y moverse mejor?
3. ¿El efecto es del rumbo o de las señales?
4. ¿La alineación es heredada o aprendida?
5. ¿El efecto vale con otros exponentes de arrastre?

## Parte A: ablación (`experiments/fase3d/evaluar.py`)
- **Poblaciones:** las que evolucionaron con `fuerza05_ambos` en la réplica (semillas 71–90).
- **Siembra:** 600 genomas en un mundo con refugio 3 fijo, movimiento por fuerza (α = 0,5) y **sin mutación**.
- **Brazos:** intacto, cero (sin sensores de rumbo ni señales, ni emisión), barajado, solo rumbo, solo señales, sin aprendizaje (con los ajustes plásticos en 0).
- **Momentos:**
  - formación: los brazos parten de la siembra; 4 brazos;
  - mantenimiento: los brazos parten de un mismo estado, tras 5000 pasos intactos; 6 brazos.
- Cada brazo corre 15 000 pasos y se mide el último tercio. Todos los brazos de una semilla y un momento comparten estado y generador.

## Parte B: sensibilidad
`experiments/fase3c/evaluar.py` con semillas nuevas, 91–100, y el diseño de la fase 3c:
- α = 1/3: ambos contra barajado;
- α = 0,75: ambos contra barajado;
- α = 0,5: solo rumbo contra barajado.

## Orientación previa (no entra en la evaluación)
- **Piloto del revisor** (3 poblaciones, sin mutación): sin información, la alineación colapsa y la población cae entre 6 y 12 %, pero los grupos no se pierden de forma consistente.
- **Prueba del script** (1 población, brazos de 600 pasos): sin información, la alineación cae de 0,72 a 0,14 y la población alrededor del 15 %; los grupos de 3 o más casi no cambian. Sin aprendizaje, la alineación se mantiene.

## Hipótesis y reglas
Las pruebas pareadas usan inversión de signos exacta, con una cola.

| # | Predicción | Regla | Expectativa |
|---|---|---|---|
| A1 | La información mantiene los grupos | grupos ≥ 3: intacto > cero, en mantenimiento, en semillas con grupos ≥ 3 de al menos 0,1 en el brazo intacto; p < 0,05 | **Probablemente no** |
| A2 | La información es necesaria para formarlos | grupos ≥ 3: intacto > cero, en formación; p < 0,05 | Incierta |
| A3 | La alineación depende de la información en vida | alineación: intacto − cero ≥ 0,2 en ≥ 70 % | Sí |
| A4 | La alineación es heredada | alineación: sin aprendizaje − cero ≥ 0,2 en ≥ 70 % | Sí |
| A5 | El efecto es del rumbo | grupos ≥ 3: solo rumbo > solo señales, en mantenimiento; p < 0,05 | Incierta |
| A6 | La información mejora la economía de la población | población: intacto > cero, en mantenimiento; p < 0,05 | Sí |
| S1 | Vale con α = 1/3 | grupos ≥ 3: ambos > barajado; p < 0,05 | Incierta |
| S2 | Vale con α = 0,75 | ídem | Incierta |
| S3 | Basta el rumbo | grupos ≥ 3, α = 0,5: solo rumbo > barajado; p < 0,05 | Sí |

## Cómo se interpretará
- **A1 y A2 no, A3, A4 y A6 sí:** la información no sostiene a los grupos en vida. Lo que hace es alinear a los socios, que se mueven y comen mejor. El efecto sobre el tamaño de los grupos de la fase 3c actuaría a escala evolutiva: con información, los linajes asociados rinden más y la asociación sobrevive a la escalada. En ese caso se dirá "la información mejora el rendimiento de los grupos", no "coordina su formación".
- **A1 o A2 sí:** la información es parte del mecanismo que forma o sostiene a los grupos.
- **S1 y S2:** si el efecto desaparece fuera de α = 0,5, se informa como dependiente del modelo.
- **Fase 4:** se usa la física "fuerza" con α = 0,5. Que la percepción del rumbo entre o no depende de A3, A6 y S3.
