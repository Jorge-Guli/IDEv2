# 2026-10-30 · Fase 12: física estable para el mundo del texto (piloto)

## Por qué
En el experimento con Asimov se extinguieron 7 de 16 poblaciones (`castigo = 0,5`, rampa de toxicidad 150 000) entre los pasos 185 000 y 391 000. Con esa tasa, cualquier diseño pierde la mitad de la potencia. Antes de otro prerregistro, hay que encontrar una física en la que sobrevivan y siga pagando elegir la comida.

## Diseño
- **Mundo:** `vivo.toml`, con el texto de calibración (`docs/00`, `01`, `04`, `06`), solo la condición texto, `texto.sensor_coincide=true` y `estaciones.induccion=0`.
- **Variantes:**
  - **A:** castigo 0,35, rampa 150 000;
  - **B:** castigo 0,5, rampa 300 000;
  - **C:** castigo 0,35, rampa 300 000.
- **Semillas de piloto:** 11–14, 500 000 pasos.
- **Salidas:** `runs/fase12/fisica_{A,B,C}.json`.

## Qué se mira
- **Supervivencia:** como mucho 1 extinción de 4.
- **Acierto en el último tercio** contra la base local del texto de calibración en esa ventana. No como prueba de predicción (el barajado también supera la base reaccionando), sino como señal de que elegir la comida se selecciona.
- **Elección:** la variante que sobreviva con mejor acierto pasa al piloto con poblaciones grandes en la GPU.

## Resultado
Base local del texto de calibración en el último tercio (letras 667–1 000): 0,524. Invertir la pista: 0,766.

| Variante | Extinciones | Acierto (último tercio, vivas) | Población media |
|---|---|---|---|
| A (0,35; 150 000) | 1 de 4 (t=266 511) | 0,551, 0,550, 0,535 | 114, 175, 59 |
| B (0,5; 300 000) | 2 de 4 (t=322 739 y 384 879) | 0,536, 0,538 | 63, 63 |
| **C (0,35; 300 000)** | **0 de 4** | 0,540, 0,550, 0,551, 0,535 | 105, 110, 96, 37 |

- **C es la única sin extinciones.** Se elige para seguir.
- **Las poblaciones son chicas** (37–175 organismos en un mundo de 128², donde sin toxicidad viven ~240). La toxicidad las mantiene cerca del límite: por eso se extinguen, y por eso descubren poco.
- El acierto queda 0,01–0,03 sobre la base: algo de selección de la comida, ninguna señal de usar la alternancia (máximo 0,557 contra 0,766 posible).
- **Siguiente:** mundo grande en la GPU con la física C, texto contra barajado. Con 16 veces más superficie hay ~16 veces más organismos, y más chances de que aparezca la mutación que invierte la pista.

## Piloto grande en la GPU (en curso)
- 384² (~9 600 organismos al inicio), `sim.poblacion_inicial=1800`, física C, texto y barajado, semillas 21–22, 500 000 pasos, 2 procesos. Salida `runs/fase12/texto_grande.json`.
- **Primer intento (2026-10-29, 4 procesos): colgó el equipo.** El pool de memoria de CuPy crecía sin límite (19 GB por proceso, más 5,5 GB de RAM). Corregido en `simbio/dispositivo.py` con un límite de 2 GB por proceso. Detalle en `docs/dispositivos.md`.
- Un vigilante detiene las corridas si la simulación ocupa más de 2 GB con poca memoria disponible, o si la GPU pasa de 12 GB. Un primer vigilante, que miraba solo la RAM libre, frenó por error la corrida a las 2 h: la memoria la ocupaban otros programas del equipo.
- Cada simulación usa un núcleo de CPU al 99 % y la GPU queda al ~60 %: el límite es la CPU que lanza los cálculos. Para aprovechar la GPU se sumaron las semillas 23–24 en paralelo (`runs/fase12/texto_grande_b.json`, 2 procesos más). Con las 4 simulaciones a la vez, la GPU queda al ~76 % y ocupa 7,2 GB.
