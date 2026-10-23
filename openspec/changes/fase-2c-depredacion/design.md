# Design

## Context

Ver `proposal.md` y la bitácora de la fase 2b. Se parte de la física base (sin bien público), con asociación y movimiento por empuje.

## Goals / Non-Goals

**Goals:** una presión física dependiente del tamaño, con un control que solo difiera en el refugio.

**Non-Goals:** depredadores como agentes con su propia evolución (posible más adelante); bien público combinado con depredación.

## Decisions

### D1. Depredación como probabilidad de ataque, no como agente
Cada organismo vivo es atacado con probabilidad `p` por paso. El ataque mata si el tamaño de su grupo conexo es menor que `refugio`. Esto representa un depredador filtrador limitado por el tamaño de su boca, distribuido de manera homogénea.
- *Alternativa: depredadores como agentes móviles.* Más realista y con coevolución, pero agrega otra dinámica que interpretar. Queda para más adelante si hace falta.

### D2. Momento del ataque
Después de pagar los costos del paso y solo sobre los vivos (energía > 0). El tamaño de grupo se calcula entre los vivos, con los enlaces del inicio del paso: quien muere de hambre en ese paso no protege. Los atacados quedan con energía −1 y caen en la "muerte antes de actuar" ya existente. El depredador usa un generador propio y sortea siempre los mismos números en todos los modos, para que las semillas sean comparables entre condiciones. Hay una aclimatación (`inicio`) antes de que empiece a actuar.

### D3. Tamaño de grupo
Componentes conexas de los enlaces válidos, por propagación de etiquetas (la misma función que usa el empuje colectivo, refactorizada).

### D4. Parámetros iniciales (`experiments/configs/depredacion.toml`)
Física base (recurso simple con capacidad 10), `movimiento = "empuje"`, `p = 0,015`, `refugio = 2` (gradual), `inicio = 2000`. Calibrado con pilotos (semillas 1 y 2, que no entran en la evaluación): con 0,002–0,01 no hay efecto, con 0,02 todo se extingue y con refugio 4 la pendiente es demasiado débil para que la selección la recorra.

### D5. Controles
- `uniforme`: misma `p`, todo ataque es mortal.
- `aleatorio`: el ataque perdona con probabilidad `prob_perdon` (0,9), sin relación con los enlaces. Es una protección de magnitud parecida, pero que no depende de asociarse. Si la asociación aparece en `refugio` y no en `aleatorio`, la causa es que la protección dependa de estar unido.
- `asociacion.division_unida = false` (exploratorio): solo `unirse` crea enlaces.

## Risks / Trade-offs
- [Que el refugio "premie" la asociación de forma demasiado directa] → es la física del mecanismo biológico que se estudia; lo exploratorio es si la evolución encuentra el camino (descubrir la asociación y coordinar el movimiento del grupo) y qué estructuras produce.
- [Mortalidad alta que extinga a LUCA antes de descubrir nada] → calibración de `p` con piloto.
