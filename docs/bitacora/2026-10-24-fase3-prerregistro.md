# 2026-10-24 · Fase 3: coordinación del grupo, prerregistro

Escrito antes de correr la evaluación. Diseño y antecedentes: [`2026-10-24-fase3-exploracion.md`](2026-10-24-fase3-exploracion.md) y `openspec/changes/fase-3-coordinacion/`.

## Pregunta
Los grupos de la fase 2c no pasan de pares porque los grupos más grandes no logran moverse juntos. Si los organismos pueden percibir el rumbo y el empuje de sus socios, o mandarse señales, ¿evoluciona la coordinación suficiente para que los grupos crezcan cuando el depredador lo exige?

## Diseño
- **Ancestro por semilla:** LUCA evoluciona 30 000 pasos en la ecología de la fase 2c con depredador gradual (`depredacion.toml`, rampa 8000), sin los sensores nuevos.
- **Ramas:** de la población final se siembran 600 genomas (los mismos en todas las condiciones), con pesos nulos sobre los sensores nuevos. Cada rama corre 60 000 pasos (`coordinacion.toml`), con el refugio subiendo de 2 a 3 entre los pasos 2000 y 32 000.
- **Condiciones:** `base` (sin percepción nueva), `rumbo`, `senales`, `ambos`, `barajado` (rumbo y señales con valores de otro organismo al azar) y `facil` (control de física: el grupo se mueve con un empuje del 10 % de su tamaño).
- **Semillas:** 41–50, que no se usaron en ningún piloto (los pilotos usaron 101–103 y 201–202).
- **Variable principal:** fracción de la población en grupos de 3 o más (el refugio final), media del último cuarto. Una corrida extinta cuenta como 0.
- **Comparaciones pareadas** por semilla; "supera" significa una diferencia de al menos 0,2.

## Hipótesis y reglas (las aplica `experiments/fase3/evaluar.py`)
| # | Predicción | Regla | Expectativa según los pilotos |
|---|---|---|---|
| H0 | Sin percepción nueva, la población abandona los grupos | `base` < 0,1 en ≥ 70 % de las semillas | Se cumple |
| H1 | El cuello de botella es el movimiento | `facil` supera a `base` en ≥ 70 % | Se cumple |
| **H2** | **La coordinación evoluciona lo suficiente para que los grupos crezcan** | `rumbo`, `senales` o `ambos` superan a `base` en ≥ 70 % (cada una por separado) | **Probablemente no** (en los pilotos, con refugio 4, la alineación subió pero los grupos no crecieron) |
| H3 | El efecto viene de la información, no de sensores extra | `ambos` supera a `barajado` en ≥ 70 % | Depende de H2 |
| H4 (secundaria) | La alineación del rumbo evoluciona | alineación entre enlazados de `rumbo` (y `ambos`) supera a la de `base` por ≥ 0,2 en ≥ 70 % de las semillas que sobreviven | Se cumple |

## Criterios de la fase
- C1: cada condición persiste en ≥ 7/10 semillas.
- C2: invariantes de enlaces, con señal en [0, 1].
- C3: reproducibilidad.
- C4: ≥ 40 pasos/s con ~1500 organismos.

## Qué haría cambiar de rumbo
- **H2 se cumple:** pasar a la fase 4 (el colectivo como individuo) sobre grupos coordinados.
- **H2 no se cumple pero H4 sí:** la evolución alinea pero no sincroniza. Opciones, en orden: (a) más tiempo evolutivo o una escalada más lenta; (b) genoma más expresivo, con estado interno (paso C), porque sincronizar exige memoria; (c) aceptar la física "fácil" como supuesto del modelo, justificándolo con la biología (las colonias reales se mueven por la suma de sus flagelos, sin decidir en conjunto) y seguir a la fase 4.
- **H1 no se cumple:** el diagnóstico estaba mal y hay que revisarlo antes de seguir.
