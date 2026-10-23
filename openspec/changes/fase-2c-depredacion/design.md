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
Al comienzo del paso, con los enlaces validados. Los muertos por ataque reciben energía −∞ y caen en la "muerte antes de actuar" ya existente: no comen, no se mueven, no ocupan su celda.

### D3. Tamaño de grupo
Componentes conexas de los enlaces válidos, por propagación de etiquetas (la misma función que usa el empuje colectivo, refactorizada).

### D4. Parámetros iniciales (`experiments/configs/depredacion.toml`)
Física base (recurso simple con capacidad 10), `movimiento = "empuje"`, `p = 0,002` (vida media de 500 pasos para un suelto, comparable a su tiempo generacional de ~400) y `refugio = 4`. Se calibran con un piloto: LUCA tiene que sobrevivir a la depredación uniforme.

### D5. Control uniforme
`depredacion.modo = "uniforme"`: misma `p`, todo ataque es mortal. Si la asociación evoluciona con refugio y no en modo uniforme, la causa es el refugio y no la mortalidad.

## Risks / Trade-offs
- [Que el refugio "premie" la asociación de forma demasiado directa] → es la física del mecanismo biológico que se estudia; lo exploratorio es si la evolución encuentra el camino (descubrir la asociación y coordinar el movimiento del grupo) y qué estructuras produce.
- [Mortalidad alta que extinga a LUCA antes de descubrir nada] → calibración de `p` con piloto.
