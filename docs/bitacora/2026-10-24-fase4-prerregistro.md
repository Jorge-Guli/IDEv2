# 2026-10-24 · Fase 4a: restricción flagelar y división del trabajo, prerregistro

Escrito antes de correr. Antecedentes: [exploración](2026-10-24-fase4-exploracion.md). Cambio: `openspec/changes/fase-4a-restriccion-flagelar/`.

## Pregunta
Si dividirse impide empujar durante un tiempo, como la restricción flagelar de *Volvox*, ¿se separan dentro de los grupos los miembros que empujan de los que se reproducen?

## Diseño (`experiments/fase4/evaluar.py`)
- **Ancestros:** LUCA → 30 000 pasos en la ecología de la fase 2c → 60 000 pasos con el modelo adoptado (fuerza α = 0,5, rumbo y señales, refugio de 2 a 3).
- **Ramas:** 600 genomas en cada condición, refugio 3 fijo y mutación activa, 60 000 pasos.
  - **Condiciones:** `sin`, `r10`, `r20` (T = 10 o 20 pasos sin poder avanzar tras dividirse) y `r20a` (control: períodos de 20 pasos con la misma frecuencia, al azar).
- **Semillas 101–110** (piloto: 401).
- **Medición:** métricas del último cuarto. Comparaciones pareadas por semilla con inversión de signos exacta, una cola.

## Piloto (semilla 401, una población, 30 000 pasos; orienta, no prueba)
| | Concentración reproductiva | Correlación avanzar/dividirse | Nunca se dividió |
|---|---|---|---|
| sin | 0,55–0,68 | −0,28 a −0,64 | 0,10–0,18 |
| r20 | 0,59–0,67 | −0,33 a −0,57 | 0,15–0,20 |
| r20a | 0,51–0,59 | −0,01 a −0,60 | 0,00–0,11 |

Con T = 50, la población se extinguió.

## Hipótesis y reglas
| # | Predicción | Regla (p < 0,05) | Expectativa |
|---|---|---|---|
| E1 | Unos empujan y otros se reproducen | correlación avanzar/dividirse más negativa en `r20` que en `r20a` | Débil, incierta |
| E2 | Aparecen miembros que no se reproducen | fracción que nunca se dividió mayor en `r20` que en `r20a` | Débil, incierta |
| E3 | Las divisiones se concentran en pocos | concentración reproductiva mayor en `r20` que en `r20a` | Incierta |
| E4 | Estar en grupo amortigua la restricción | enlazados mayor en `r20` que en `r20a` | Incierta |
| E5 | Efecto de dosis | nunca se dividió mayor en `r20` que en `r10` | Incierta |

## Cómo se interpretará
- **E1 y E2 se cumplen:** aparece un germen de división del trabajo reproductivo, ligado específicamente al compromiso entre dividirse y moverse. El paso siguiente es buscar dependencia (que los especialistas no sobrevivan solos) y la heredabilidad de la composición del grupo.
- **Nada se cumple:** con este compromiso, y en este tiempo, la especialización no aparece. Habría que probar compromisos más fuertes o más tiempo, o revisar si la física permite especializarse (por ejemplo, si los miembros perciben su posición en el grupo).
