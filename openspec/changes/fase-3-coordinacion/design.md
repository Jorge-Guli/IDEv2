# Design

## Context
Ver `proposal.md` y `docs/bitacora/2026-10-24-fase3-exploracion.md`. Se parte de la ecología de la fase 2c (depredación limitada por tamaño, movimiento por empuje).

## Goals / Non-Goals
**Goals:** dar a los organismos percepción local que **permita** coordinarse, sin imponer ninguna conducta, y medir si la coordinación evoluciona y rompe el techo de tamaño.

**Non-Goals:** cambiar la regla de movimiento del grupo (solo aparece como control positivo); reproducción del grupo o especialización (fase 4).

## Decisions

### D1. Sensores por contacto, no visión
El rumbo y el empuje de los socios se perciben solo a través de enlaces válidos, como una tracción mecánica. El ángulo se mide en octavos de vuelta respecto del rumbo propio; el seno indica hacia qué lado girar y el coseno, cuán alineados están.
- *Alternativa: una primitiva "alinearse".* Descartada: sería una conducta programada.

### D2. La señal es una salida continua, no una acción
Si emitir una señal ocupara la acción del paso, señalar y moverse serían excluyentes y la sincronía se volvería casi imposible. Los genes de `senalar` suman impulso como cualquier otro, pero ese impulso, recortado a [0, 1], es la señal. Cuesta energía en proporción a su intensidad y no se refuerza por aprendizaje. La señal propia del paso anterior es un sensor: la memoria mínima de un paso.

### D3. Control barajado
Permuta entre organismos los valores de los sensores nuevos. Conserva la distribución, y por lo tanto los grados de libertad extra del genoma, pero quita la información sobre los socios propios.

### D4. Escalada del refugio
Lineal y con valores no enteros: la probabilidad de muerte del modo gradual sube de forma continua y la selección encuentra una pendiente.

### D5. Diseño experimental pareado
Un ancestro por semilla, generado desde LUCA con la ecología de la fase 2c, y las mismas 600 semillas genómicas en todas las condiciones. Los pesos sobre los sensores nuevos se ponen en 0 al sembrar, porque derivaron sin efecto en el ancestro.

### D6. Objetivo de tamaño: refugio 3
Con refugio 4, ni la percepción del rumbo ni las señales hicieron crecer los grupos en 40 000 pasos. El refugio 3 pide el paso mínimo (de pares a tríos) y la corrida dura 60 000 pasos.

## Risks / Trade-offs
- [Los sensores de rumbo hacen "demasiado fácil" la coordinación] → la evolución todavía tiene que cablearlos (los pesos parten de 0), y el control barajado separa la información de los grados de libertad.
- [Tiempo evolutivo insuficiente] → si H4 se cumple y H2 no, la hoja de ruta prevé más tiempo o un genoma con estado interno.
- [Compatibilidad] → el genoma cambia de forma: los resultados de fases anteriores se reproducen en el commit `8099dd8`, y los genomas guardados se completan con pesos nulos.
