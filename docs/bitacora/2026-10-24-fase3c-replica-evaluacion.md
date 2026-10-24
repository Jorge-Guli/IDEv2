# 2026-10-24 · Fase 3c, réplica: resultados (semillas 71–90)

Prerregistro: [`2026-10-24-fase3c-replica-prerregistro.md`](2026-10-24-fase3c-replica-prerregistro.md). Corrido en el equipo local (62 minutos). Informe: [`2026-10-24-fase3c-replica-informe.json`](2026-10-24-fase3c-replica-informe.json).

- **Persistencia:** 20/20 en las tres condiciones.
- **Ancestros:** mayormente en grupos en 17 de 20 semillas. En las semillas 74, 82 y 83, el ancestro tenía poca asociación (0,29–0,45).

## Hipótesis prerregistradas
| # | Resultado | Veredicto |
|---|---|---|
| **R1** (con percepción del rumbo, más poblaciones en el régimen con grupos) | `ambos` **16/20** contra `barajado` 7/20; Fisher una cola **p = 0,005** | ✅ |
| R2 (dentro del régimen, la información no achica los grupos) | media en grupos ≥ 3: `ambos` 0,38, `barajado` 0,31, `base` 0,38 | ✅ (descriptiva) |
| R3 (control: barajar no es peor que no percibir) | `barajado` 7/20 contra `base` 5/20; p = 0,73 | ✅ no difieren |

Las reglas de la fase 3c original, aplicadas a estas semillas nuevas, también se cumplen:
- F2: `ambos` supera a `barajado` por ≥ 0,1 en 14/20 (70 %), con media +0,18;
- F4: alineación +0,57 en 11/12 semillas evaluables.

| α = 0,5 | En régimen con grupos | Población media | Alineación entre enlazados | Grupo más grande |
|---|---|---|---|---|
| base | 5/20 | 595 | 0,06–0,37 | 6–18 |
| **ambos** | **16/20** | **669** | **0,60–0,86** (en régimen) | 8–16 |
| barajado | 7/20 | 595 | −0,05–0,39 | 7–15 |

- Las 4 semillas en las que `ambos` no entra al régimen incluyen las 3 con un ancestro poco asociado (74, 82 y 83). Ninguna condición forma grupos en esas semillas: sin asociación previa, la información sobre los socios no tiene sobre qué actuar.
- El gen de señal está en ~3,5 % de la población: el canal de señales sigue sin usarse.

## Revisión científica
Revisión independiente (subagente `revisor-cientifico`), con verificaciones ejecutadas:
- **Código correcto.** "fuerza" cumple la spec. El camino rápido da el mismo estado que un bucle de referencia también con "fuerza". El consumo de azar es igual en las tres percepciones. El control barajado es justo, y si filtra algo, lo acerca a `ambos` (es conservador).
- **El efecto principal es robusto, y más fuerte con la prueba correcta.** Las condiciones comparten ancestro y semilla, así que corresponde una prueba pareada:
  - McNemar: 9 pares discordantes a favor de `ambos` y 0 en contra, p ≈ 0,002;
  - permutación pareada sobre la fracción continua en grupos ≥ 3: p ≈ 3·10⁻⁵;
  - R1 se cumple con cualquier umbral entre 0,05 y 0,35.
- **"Conservar la asociación" no está sostenido.** Con enlazados ≥ 0,1: `ambos` 17/20, `barajado` 12/20, `base` 10/20 (p = 0,078). Entre las 12 semillas donde ambas condiciones conservan la asociación, `ambos` tiene más organismos en grupos de 3 o más (permutación pareada p = 0,001). El efecto está sobre todo en el **tamaño de los grupos**, no en conservar la asociación. La bimodalidad de 61–70 no se repite limpia: hay valores intermedios. R2 condiciona al resultado, así que tiene sesgo de selección.
- **"Coordinación" no está demostrada como causa.** Piloto de ablación del revisor: 3 poblaciones evolucionadas con `ambos` y continuadas sin mutación. Al quitar la información, la alineación colapsa (0,53–0,80 → 0,12–0,27) y la población cae entre 6 y 12 %, pero los grupos ya formados no se pierden de forma consistente.
- **Rumbo y señales están confundidos:** `ambos` incluye los dos. Las señales casi no evolucionan, así que la atribución al rumbo es plausible, pero no está probada.
- **Alineación heredada o aprendida:** el aprendizaje está activo y los ajustes plásticos no se heredan. No se separó.
- **Dependencia del modelo:** el resultado está acotado a α = 0,5 (con α = 1 no hay grupos). No se probaron 1/3 ni 0,75. La interacción con "empuje" (F3) no se replicó.
- R3 ("barajado no difiere de base") es falta de evidencia, no evidencia de igualdad.
- Las 3 semillas con ancestro poco asociado juegan en contra del efecto y no se excluyen.

## Lo que se afirma
- **Con movimiento por fuerza y α = 0,5, la percepción de los socios (rumbo y señales) aumenta la fracción de la población en grupos de 3 o más cuando el depredador escala.** Réplica prerregistrada con 20 semillas nuevas; prueba pareada p ≈ 0,002 a 3·10⁻⁵; 23/30 corridas en régimen contra 11/30 barajado sumando 61–90.
- La alineación entre socios aparece solo con información real y colapsa si se la quita.
- La física "fuerza" (α = 0,5) permite grupos de 3 o más; con "empuje", 0 de 30 corridas los tuvieron.

## Lo que todavía no se afirma
- Que la información haga conservar la asociación.
- Que sea la coordinación del movimiento la que produce los grupos.
- Que sea el rumbo y no las señales.
- Que la alineación se herede y no se aprenda en vida.
- Que el resultado valga fuera de α = 0,5.
- Que la información rinda más con fuerza que con empuje.

## Decisión
- **Se cierra la fase 3c adoptando "fuerza" con α = 0,5** como regla de movimiento de grupos del modelo. El prerregistro de la réplica lo preveía incluso si R1 fallaba.
- Antes de usar la percepción del rumbo como mecanismo de grupo en la fase 4, una **fase 3d** prerregistrada:
  - ablación completa sobre las poblaciones de la réplica, con brazos solo rumbo, solo señales y sin aprendizaje;
  - sensibilidad a α ∈ {1/3; 0,75};
  - una condición solo rumbo.
