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
- C4, rendimiento: **el valor del informe no es válido** (44 551 pasos/s con población 0). La prueba arrancaba desde LUCA con el depredador activo desde el paso 0 y medía un mundo extinto.
  - Una primera corrección, sin depredador, daba 59 pasos/s. La revisión señaló que también era optimista: desde LUCA no hay grupos y el código del empuje colectivo ni se ejecuta.
  - Medido como corresponde (1500 genomas evolucionados de la fase 2c, con grupos, depredador, rumbo y señales; 180×180): **32 pasos/s en el contenedor**, bajo el umbral.
  - Se vectorizó el empuje colectivo, con resultado idéntico (test de equivalencia contra la versión original y huellas iguales): **50 pasos/s con ~1250 organismos, el 96 % enlazados**. ✅ El script ahora mide así y exige ≥ 1000 organismos y > 30 % de enlazados.

## Hipótesis
Variable principal: fracción de la población en grupos de 3 o más (el refugio final), en el último cuarto.

| # | Predicción | Resultado | Veredicto |
|---|---|---|---|
| H0 | Sin percepción nueva, se abandonan los grupos | `base`: 0,00–0,04 en 10/10 | ✅ |
| H1 | El cuello de botella es el movimiento | `facil` supera a `base` en **10/10** (diferencia media +0,59; `facil`: 0,49–0,73) | ✅ |
| **H2** | La coordinación evoluciona lo suficiente para que los grupos crezcan | `rumbo` +0,01, `senales` +0,00, `ambos` +0,01 sobre `base`; **0/10** superan por 0,2 | ❌ **Refutada** |
| H3 | El efecto viene de la información | `ambos` contra `barajado`: +0,00, 0/10 | ❌ No interpretable: no hay efecto que atribuir, y el control estaba contaminado (ver Revisión) |
| H4 | La alineación del rumbo evoluciona | `ambos`: supera a `base` por ≥ 0,2 en **9/10** (alineación 0,31–0,88, contra 0,11–0,25). `rumbo`: en 7/10, justo en el umbral | ✅ |

Detalle de H4 en `rumbo`: **cumple justo en el umbral y es frágil.** En las semillas 49 y 50 queda ~1 enlazado de 760 (fracción 0,001), así que su alineación (0,42 y −0,19) es ruido de uno o dos pares; en la 41 quedan pocos (0,09). El prerregistro no fijó un mínimo de pares para calcular la alineación; a futuro se exigirán ≥ 20 pares por registro. Con ese filtro, `rumbo` daría 7/8.

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

## Revisión científica
Revisión independiente (subagente `revisor-cientifico`), con verificaciones ejecutadas:
- **Sin bugs que inviertan los resultados.** Verificados: el signo de los sensores de rumbo (un gen de girar a la derecha con peso positivo converge al rumbo del socio); que el empuje lea la acción del paso anterior; que la señal no compita por la acción ni se refuerce; que la siembra ponga en 0 los pesos nuevos; y las métricas de alineación y éxito del empuje.
- **Ablación causal de H4:** con los sensores en 0, la alineación de poblaciones evolucionadas cae de 0,70–0,79 a 0,05–0,06, sin que cambie la frecuencia de giro. Los genomas usan el sensor.
- **El control barajado estaba contaminado:** permutaba entre toda la población (el 42 % de los enlazados recibía ceros y el 56 % de los sueltos recibía valores) y barajaba también la memoria propia. Se corrigió (ahora permuta solo entre enlazados y no toca la señal propia), con test. En esta evaluación no cambia nada, porque H2 no tuvo efecto.
- **C4** era optimista (ver Criterios). Se corrigió.
- **Anisotropía del empuje:** un rumbo diagonal aporta √2 a la suma. Por ejemplo, un trío con un solo empujador diagonal no se mueve (1,41 < 1,5), pero con empujes N + NE sí. Es menor en esta física, pero hay que corregirlo antes de cualquier regla de movimiento nueva.
- **El control fácil** quita a la vez la exigencia de coordinación y la de esfuerzo por miembro (un solo miembro arrastra un grupo de hasta 10). Muestra que el movimiento limita, pero no separa esos dos factores.
- **Hallazgo clave: el genoma actual ya puede sincronizar un trío, sin memoria.** Un trío alineado con un solo gen de avanzar que sigue al sensor de empuje de los socios (sesgo −0,6, +3 sobre empuje de socios, +0,8 sobre ruido) se movió en el 99,5 % de los pasos en que alguien empujó, contra el 14 % sin ese peso. El mecanismo es "seguir al que empuja": con un paso de retraso alcanza.

**Exploratorio (no prerregistrado; muchas comparaciones posibles):** `ambos` frente a `barajado` da +0,56 de alineación (10/10 semillas), +0,09 de éxito del empuje en grupos ≥ 3 (9/10), +55 de población (10/10) y +0,15 de enlazados (9/10). Es consistente con que la información del rumbo se usa y mejora algo el movimiento y la persistencia de los pares. La diferencia en grupos ≥ 3 frente a `base` (+0,012, 9/10) es despreciable y elegida después de ver los datos: no se presenta como efecto.

## Conclusión de la fase
- **Lo que se afirma:** con esta física y en 60 000 pasos, la percepción del rumbo de los socios hace evolucionar la alineación (sólido con rumbo y señales; frágil solo con rumbo), pero no rompe el techo de tamaño de los grupos (H2 refutada en las tres variantes). El canal de señales, con costo 0,05, no despega. El techo es el movimiento del grupo (H1, 10/10).
- **Lo que cambia respecto del prerregistro:** la opción "hace falta memoria" queda descartada para tríos, porque el genoma actual puede sincronizar sin ella. El cuello de botella parece de **accesibilidad evolutiva o de selección**, no de expresividad: los tríos son raros y pasan hambre, así que la selección casi no actúa sobre su coordinación.

## Decisión
Antes de cambiar la física, una **prueba de invasión**, barata y diagnóstica (fase 3b): insertar un mutante coordinado diseñado a mano (alineación más "seguir al que empuja") en poblaciones evolucionadas con refugio 3, contra un mutante control con los mismos genes pero sin conexión a los sensores.
- **Si invade:** la física premia la coordinación y lo que falta es tiempo o acceso (más tiempo, escalada más lenta, arrancar con tríos).
- **Si no invade:** la ecología no premia a los tríos coordinados. Cambiar la regla de movimiento pasa a ser una decisión de modelo, con prerregistro y semillas nuevas, corrigiendo antes la anisotropía.
