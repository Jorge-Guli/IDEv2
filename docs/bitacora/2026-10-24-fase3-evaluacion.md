# 2026-10-24 · Fase 3: coordinación del grupo, resultados

Hipótesis y reglas prerregistradas en [`2026-10-24-fase3-prerregistro.md`](2026-10-24-fase3-prerregistro.md); las evalúa `experiments/fase3/evaluar.py`. Semillas 41–50, corridas en el equipo local (96 minutos). Informe: [`2026-10-24-fase3-informe.json`](2026-10-24-fase3-informe.json).

```powershell
python experiments/fase3/evaluar.py --salida runs/fase3 --procesos 8
```

## Ancestros
LUCA evolucionó 30 000 pasos en la ecología de la fase 2c. En 9 de 10 semillas el ancestro termina mayormente en grupos (fracción 0,85–0,96); en la semilla 49, en 0,26.

## Criterios
- C1, persistencia: 10/10 en las seis condiciones. ✅
- C2, invariantes con rumbo y señales: 0 violaciones en 315 290 enlaces. ✅
- C3, reproducibilidad: ✅
- C4, rendimiento: el informe dice 44 551 pasos/s con población 0 porque la prueba arrancaba desde LUCA con el depredador activo desde el paso 0, y medía un mundo extinto. Se corrigió el script (sin depredador, y exige ≥ 1000 organismos) y se midió aparte: **59 pasos/s con 1408 organismos** en el contenedor, que es más lento que el equipo local. ✅

## Hipótesis
Variable principal: fracción de la población en grupos de 3 o más (el refugio final), en el último cuarto.

| # | Predicción | Resultado | Veredicto |
|---|---|---|---|
| H0 | Sin percepción nueva, se abandonan los grupos | `base`: 0,00–0,04 en 10/10 | ✅ |
| H1 | El cuello de botella es el movimiento | `facil` supera a `base` en **10/10** (diferencia media +0,59; `facil`: 0,49–0,73) | ✅ |
| **H2** | La coordinación evoluciona lo suficiente para que los grupos crezcan | `rumbo` +0,01, `senales` +0,00, `ambos` +0,01 sobre `base`; **0/10** superan por 0,2 | ❌ **Refutada** |
| H3 | El efecto viene de la información | `ambos` contra `barajado`: +0,00, 0/10 | ❌ (no hay efecto que atribuir) |
| H4 | La alineación del rumbo evoluciona | `ambos`: supera a `base` por ≥ 0,2 en **9/10** (alineación 0,31–0,88, contra 0,11–0,25). `rumbo`: en 7/10, justo en el umbral | ✅ |

Detalle de H4 en `rumbo`: en las semillas 41, 49 y 50 casi no quedan enlazados al final (fracción 0,00–0,09), así que su alineación se mide sobre muy pocos pares y no es interpretable. Si se excluyen, 7/7 superan por ≥ 0,2.

| Condición | En grupos ≥ 3 | Tamaño medio | Enlazados | Alineación | Éxito del empuje (grupos ≥ 3) | Población |
|---|---|---|---|---|---|---|
| base | 0,017 | 1,45 | 0,43 | 0,19 | 0,27 | 748 |
| rumbo | 0,029 | 1,51 | 0,47 | 0,53 | 0,32 | 742 |
| senales | 0,019 | 1,46 | 0,44 | 0,15 | 0,26 | 744 |
| ambos | 0,029 | 1,63 | 0,60 | **0,73** | 0,35 | 781 |
| barajado | 0,027 | 1,48 | 0,45 | 0,17 | 0,26 | 726 |
| **facil** | **0,61** | **3,35** | **0,83** | 0,10 | **0,74** | **998** |

## Lo que muestran los datos
1. **La predicción de los pilotos se cumplió: la evolución alinea, pero no sincroniza.** Con percepción del rumbo de los socios, la alineación entre enlazados sube de ~0,2 a ~0,7, y los pares resisten mejor la escalada (enlazados 0,60 en `ambos` contra 0,43 en `base`). Pero los grupos de 3 o más siguen siendo ~2–3 % de la población, y su empuje funciona en ~1 de cada 3 intentos.
2. **El canal de señales no se inventa.** El gen de señal está en ~1 % de la población en todas las condiciones con señales, la señal media es ~0 y `senales` no se distingue de `base`.
3. **El control fácil confirma el diagnóstico con 10 semillas nuevas.** Cuando mover al grupo no exige sincronía, los grupos crecen (máximos de 13 a 28) y la población es un 33 % mayor. En ese control **la alineación no evoluciona** (0,10, menos que en `base`): la coordinación solo se selecciona cuando hace falta.
4. **Por qué no alcanza la alineación.** Un trío se mueve solo si dos miembros empujan alineados en el mismo paso. Alinearse se aprende de a pares, que son la mayoría. Sincronizar el empuje solo rinde en grupos de 3 o más, que son raros porque no se mueven: la selección casi no actúa sobre esa conducta.

## Interpretación (prudente)
- La pregunta de la fase era si la coordinación puede evolucionar desde la percepción local. La respuesta, en esta física y en 60 000 pasos, es **en parte**: evoluciona la alineación (una coordinación de a pares), pero no la sincronía que exige el umbral de empuje de los grupos más grandes.
- El resultado depende de una decisión de física tomada en la fase 2b: que un grupo solo se mueva si el empuje alcanza la mitad de su tamaño. Esa regla convierte el tamaño en un valle de aptitud.

## Decisión
Pendiente de la revisión científica.
