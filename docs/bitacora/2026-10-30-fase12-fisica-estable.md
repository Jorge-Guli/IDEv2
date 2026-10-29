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
