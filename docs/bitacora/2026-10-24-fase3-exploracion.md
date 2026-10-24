# 2026-10-24 · Exploración previa a la fase 3: ¿por qué los grupos no pasan de pares?

Exploración (no prerregistrada) para diseñar la fase 3. Semillas de piloto 101–103 y 201–202, distintas de todas las de evaluación.

## 1. Un depredador que escala no agranda los grupos
Se agregó la **escalada del refugio**: el tamaño de grupo que el depredador no puede tragar sube linealmente de `refugio` a `refugio_final` (`depredacion.refugio_final`, `escalada_inicio`, `escalada_pasos`). Es la idea de "trinquete" de los experimentos de evolución de la multicelularidad: una presión que crece de a poco.

Desde LUCA, con la configuración de la fase 2c (rampa de 8000 pasos), escalando de 2 a 5 entre los pasos 12 000 y 42 000 (semillas 101–103), y con un salto a 3 en el paso 12 000 (semilla 101):

| Corrida | En grupos en el paso 10 000 | En grupos al final (60 000) | Grupos de 3 o más |
|---|---|---|---|
| escalada, 101 | 0,43 | 0,00 | ≤ 0,09 en toda la corrida |
| escalada, 102 | 0,01 | 0,00 | ≤ 0,02 |
| escalada, 103 | 0,11 | 0,00 | ≤ 0,04 |
| salto a 3, 101 | 0,43 | 0,01 | ≤ 0,05 |

Cuando un par deja de estar a salvo, la población **abandona la asociación** en lugar de formar grupos más grandes. Con el depredador ya escalado, la población de sueltos sobrevive (350–920 organismos).

## 2. Diagnóstico: los grupos de 3 o más no pueden moverse
Se sembraron los genomas evolucionados de la fase 2c (rampa, semilla 31) en un mundo con refugio 2 y sin mutación, y se midió, según el tamaño del grupo, qué hacen los organismos y qué logran (pasos 1000–2500, ~1100 organismos):

| Tamaño del grupo | Fracción de la población | Eligen avanzar | **Se mueven cuando lo intentan** | ΔE medio por paso | Energía media |
|---|---|---|---|---|---|
| 1 | 0,031 | 0,25 | **0,95** | +0,09 | 26 |
| 2 | 0,951 | 0,26 | **0,80** | +0,02 | 34 |
| 3 | 0,017 | 0,42 | **0,39** | −0,31 | 11 |
| 4 | 0,001 | 0,41 | **0,31** | −0,32 | 23 |
| 5 | < 0,001 | 0,50 | **0,06** | −0,56 | 23 |

Además, los sueltos se dividen quedando unidos en el 5 % de los pasos y los miembros de un par en el 0,1 %. La población evolucionó un ciclo "suelto → par" y casi no hace tríos.

**Lectura.** Un grupo se desplaza solo si la suma de las orientaciones de los que empujan alcanza la mitad de su tamaño y todas las celdas de destino están libres. Cada miembro gira por su cuenta, porque sus sensores de alimento son relativos a su propia orientación, y no percibe hacia dónde apunta su socio. Cuanto más grande el grupo, menos probable es que se alinee: los grupos de 3 o más quedan casi inmóviles, agotan el recurso de sus celdas y pasan hambre. **El techo de tamaño es un problema de coordinación del movimiento.** La hoja de ruta lo anticipaba como el disparador del paso B ("si los grupos existen pero no se coordinan, por ejemplo, no pueden moverse juntos").

## 3. Control de física: si moverse es fácil, los grupos crecen
Desde los genomas de la fase 2c (semilla 31), con el refugio escalando de 2 a 4 entre los pasos 2000 y 32 000 (40 000 pasos; semillas 201 y 202):

| Corrida | Tamaño medio de grupo al final | En refugio (≥ 4) al final | En grupos |
|---|---|---|---|
| física actual, 201 | 1,0 | 0,00 | 0,00 |
| física actual, 202 | 1,0 | 0,00 | 0,00 |
| **empuje fácil** (basta el 10 % del tamaño), 201 | **4,2** | **0,62** | 0,88 |
| **empuje fácil**, 202 | **4,8** | **0,64** | 0,90 |

Con la misma presión, si mover al grupo no exige alinearse, los grupos crecen y siguen al depredador (máximos de 11 a 16), y la población es incluso mayor. Esto confirma el diagnóstico.

## 4. Pilotos con percepción del rumbo y señales
Mismo diseño, con los sensores nuevos (ver `openspec/changes/fase-3-coordinacion/`):

| Corrida | Alineación entre enlazados (paso 8000 → 32 000) | Éxito del empuje en grupos ≥ 3 | En grupos al final | Señal media |
|---|---|---|---|---|
| rumbo, 201 | 0,33 → 0,40 | 0,29–0,37 | 0,09 | — |
| rumbo, 202 | 0,41 → **0,72** | 0,30–0,37 | 0,58 | — |
| rumbo + señales, 201 | 0,24 → **0,75** | 0,28–0,40 | 0,32 | ~0 |
| rumbo + señales, 202 | 0,22 → **0,66** | 0,29–0,39 | 0,11 | ~0 |

- **La alineación evoluciona** en 3 de 4 corridas, y los pares resisten más la escalada que con la física actual (que llega a 0).
- **Los grupos no crecen:** casi no hay grupos de 3 o más, y los que hay se mueven poco.
- **El canal de señales no se usa** en 40 000 pasos.

Diagnóstico de los fallos de movimiento con la población final de "rumbo, 202" (refugio 4, sin mutación):

| Tamaño | Intentos | Empuje bajo el umbral | Destino bloqueado | Se mueve |
|---|---|---|---|---|
| 2 | 131 854 | 0,00 | 0,11 | 0,88 |
| 3 | 4701 | **0,54** | 0,07 | 0,39 |
| 4 | 497 | **0,57** | 0,14 | 0,28 |
| 5 | 296 | **0,81** | 0,05 | 0,14 |

Un par se mueve con un solo miembro que empuje; un trío necesita que **dos empujen alineados en el mismo paso**. Es un problema de sincronía, no de espacio. Hay además un círculo vicioso: los tríos son raros porque no se mueven, y por eso la selección casi no actúa sobre su coordinación.

## Decisión de diseño
La fase 3 se prerregistra con un objetivo más corto (refugio de 2 a 3: solo hace falta pasar de pares a tríos) y con más tiempo evolutivo (60 000 pasos). Los pilotos con refugio 3 se cortaron por un reinicio del contenedor; la evaluación completa se corre en el equipo local.
