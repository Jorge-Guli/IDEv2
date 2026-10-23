# Design

## Context

Repositorio nuevo, sin código previo. Ver `proposal.md` (Why) y `docs/01-metodologia.md` (principios). Restricciones: Python, sin modelos preentrenados, ejecutable en un contenedor de 4 núcleos y escalable luego a una máquina local más potente.

## Goals / Non-Goals

**Goals:**
- Un núcleo de simulación vectorizado (NumPy) que mantenga ~1500–5000 organismos a decenas de pasos por segundo.
- Una representación genética donde las conductas sean combinables, ganables y perdibles por mutación, y que se extienda en fases futuras agregando primitivas (unirse, compartir, señalizar) sin rediseñar.
- Experimentos con controles por interruptores de configuración.

**Non-Goals:**
- Asociación, comunicación, transferencia horizontal (fases 2+).
- Origen de la vida: LUCA se diseña a mano.
- Interfaz interactiva: alcanza con imágenes y gráficos.

## Decisions

### D1. Genoma como colección de genes-regla (y no programa tipo Avida ni red neuronal fija)
Cada gen `g` tiene: `activo`, `primitiva_g` (entero), pesos `w_g ∈ R^S` y sesgo `b_g`. Su activación es `a_g = tanh((w_g + P_g)·s + b_g + p_g)` (P, p: ajustes plásticos). El impulso de cada primitiva es la suma de las activaciones de los genes que la expresan; se ejecuta la de mayor impulso si es positivo, si no se descansa. Una primitiva sin genes no puede ejecutarse.

- *Alternativa: instrucciones tipo Avida.* Muy abierta pero lenta en Python (un intérprete por organismo) y difícil de vectorizar.
- *Alternativa: red neuronal de topología fija.* Rápida, pero todas las acciones están siempre presentes: contradice el principio de que las acciones salen del ADN.
- La opción elegida equivale a una red neuronal dispersa de topología evolutiva (cada gen ≈ una neurona dedicada a una acción), análoga a genes que codifican proteínas con función. Duplicación + divergencia permite conductas condicionales nuevas (p. ej. "comer solo si hay mucho recurso" y "comer siempre si estoy hambriento").
- Representación con número máximo de ranuras `G` (24) y máscara `activo`, para vectorizar con arreglos `(N, G, S)`.

### D2. Primitivas y sensores de la fase 1
Primitivas (física fija): `DESCANSAR, AVANZAR, GIRAR_IZQ, GIRAR_DER, VOLTERETA, COMER, DIVIDIRSE`. Orientación en 8 direcciones; los giros son de 45°; la voltereta elige una orientación al azar (conducta "correr y dar voltereta" de *E. coli*).
Sensores (S = 10): constante 1, recurso aquí, recurso al frente, recurso frente-izquierda, recurso frente-derecha, energía propia, ocupación del vecindario, frente bloqueado, último ΔE, ruido uniforme. Recursos normalizados por la capacidad máxima; energía por la energía máxima.

### D3. Física (valores por defecto, todos configurables)
Grilla 128×128 toroidal. Capacidad máxima por celda 10; regeneración `R += 0.02·(K−R)`. Parches: ruido blanco suavizado con filtro gaussiano por FFT, normalizado a [0,1] y elevado a una potencia para contraste. Estacionalidad: `K_eff = K·(1 + A·sin(2πt/P))`.
Energía máxima 100; costo basal 0.3/paso; costo por gen activo 0.01/paso; avanzar 0.4; girar 0.05; voltereta 0.1; comer 0.05 con toma máxima 4/paso; dividirse 2 con energía mínima 20.

### D4. Orden de un paso y resolución de conflictos
1) Regenerar recursos. 2) Aprendizaje: actualizar ajustes plásticos con el ΔE desde la decisión previa. 3) Sensar. 4) Decidir. 5) Cobrar costos basales y de acción. 6) Girar/voltereta. 7) Comer (como hay un organismo por celda no hay conflicto). 8) Avanzar: destino válido solo si estaba libre al inicio; los conflictos entre organismos con el mismo destino se resuelven en orden aleatorio (gana el primero). 9) Dividir: el hijo va a una celda vecina libre elegida al azar; conflictos resueltos igual. 10) Muertes. 11) Estrés y métricas.
Todo es vectorizado; el orden aleatorio sale del generador con semilla, por lo que la corrida es determinista.

### D5. Herencia y mutagénesis por estrés
Estrés: `estrés ← 0.95·estrés + 0.05·hambre`, con `hambre = clip((25 − E)/25, 0, 1)`, calculado antes de dividirse para que la reproducción no cuente como hambre (una versión previa usaba `1 − E/E_max` y quedaba dominada por la división, según la revisión independiente). El hijo nace con estrés 0. Tasa efectiva del hijo: `m = min(μ·(1 + σ·estrés), 0.2)`, con `μ` (tasa base) y `σ` (sensibilidad) heredables. Con tasa `m`, por gen activo: mutación puntual de cada peso con probabilidad `m` (ruido N(0, 0.3)); cambio de primitiva con `0.3·m`; duplicación hacia una ranura libre con `0.5·m`; eliminación con `0.5·m`. Por genoma: gen nuevo aleatorio con probabilidad `G·m·0.2`. Rasgos (`μ`, `σ`, `η`) mutan con probabilidad `min(1, 10·m)` por un factor log-normal (σ_log = 0.2) y se acotan. Control experimental: modo "barajado", en el que cada hijo usa el estrés de otro organismo al azar.
LUCA: genes "comer si hay recurso aquí y no estoy lleno", "avanzar si aquí no hay recurso (más si hay al frente)", "voltereta al azar o si estoy bloqueado", "dividirse si energía alta" (calibrado para ser viable con y sin aprendizaje); `μ = 0.02`, `σ = 2`, `η = 0.05`.

### D6. Aprendizaje
Recompensa `r = clip((ΔE − línea_base)/5, −1, 1)`, `línea_base ← 0.9·línea_base + 0.1·ΔE`. Para los genes que expresan la primitiva ejecutada: `P_g += η·r·(1 − a_g²)·s`, `p_g += η·r·(1 − a_g²)` (gradiente del impulso respecto de la entrada del gen: una acción recompensada aumenta su impulso en ese contexto). Los pasos de división se excluyen de la recompensa, de la línea base y del sensor de ΔE. Decaimiento 1 % por paso y recorte a ±2. Así el aprendizaje modula la respuesta de genes existentes; no puede crear acciones que el genoma no tiene (coherente con la biología: la plasticidad opera sobre lo que el genotipo permite).

### D7. Estructura del código
`src/simbio/`: `config.py` (dataclasses + TOML), `entorno.py`, `genoma.py`, `poblacion.py` (estructura de arreglos), `simulacion.py` (paso), `metricas.py`, `persistencia.py`, `visual.py`, `cli.py`. `experiments/configs/*.toml`, `experiments/fase1/*.py`. Configuración en TOML porque `tomllib` está en la biblioteca estándar.

### D8. Muerte antes de actuar e intentos de división
Quien queda sin energía tras pagar los costos muere antes de comer, moverse o dividirse. Un intento de división fallido (poca energía o sin espacio) no cuesta nada ni se evalúa en el aprendizaje: equivale a descansar. Se acepta por simplicidad; la selección igual penaliza a los genes que pierden turnos.

## Risks / Trade-offs

- [Mundo saturado y sin presión] → regeneración y costos calibrados para que la población sea limitada por recursos; métricas de energía media lo vigilan.
- [Extinción temprana por mutaciones letales (perder el gen de división)] → es selección legítima; la tasa base inicial es baja y C1 lo verifica.
- [La selección sobre μ y σ es débil (selección de segundo orden)] → no es criterio de éxito; se reporta como exploratorio.
- [Conflictos de movimiento simplificados (no se puede entrar a una celda que se libera en el mismo paso)] → sesgo menor y uniforme para todos.
- [Python limita la escala] → núcleo vectorizado; si la fase 3+ lo requiere, migrar a JAX/Numba sin cambiar specs.
