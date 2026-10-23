# Design

## Context

Se extiende el simulador de la fase 2 (`openspec/specs/`, anexo de la fase 2 en `docs/odd/modelo.md`). Ver `proposal.md`. El rendimiento actual es de ~55 pasos/s con ~1800 organismos en CPU; el modo GPU existe para mundos grandes.

## Goals / Non-Goals

**Goals:**
- Un bien público físico con un dilema real: producirlo cuesta al que secreta, y el beneficio se reparte entre todos los vecinos.
- Que la localidad del beneficio (difusión del alimento libre) sea un parámetro, para estudiar cuándo conviene agruparse.
- Que con `bien_publico.activo = false` todo siga igual que en la fase 2.

**Non-Goals:**
- Regulación de la secreción por señales (quorum sensing): es fase B.
- Varios tipos de enzima o recurso.

## Decisions

### D1. Tres campos nuevos en el entorno
- `C`: recurso complejo, con regeneración `C += g_c·(K_c − C)` y un mapa de parches propio generado con otra semilla derivada.
- `Z`: enzima.
- `A`: alimento libre.

Orden dentro del paso del entorno: regenerar R y C, difundir y degradar Z, digerir (`d = C·(1 − exp(−k·Z))`; `C −= d`; `A += r·d`) y difundir y degradar A.
- *Alternativa: volcar lo digerido en R.* Se descartó porque la regeneración de R hacia K y el recorte estacional destruirían el alimento libre, y se perdería la medición separada.

### D2. Difusión
Una fracción `f` de cada celda se reparte en partes iguales entre sus 8 vecinas (toroidal, con `np.roll`); conserva el total. La degradación es multiplicativa `(1 − δ)`.

### D3. Comer
`toma = min(R + A, toma_max, E_max − E)`. Se come primero del recurso simple y después del libre.

### D4. Secretar
Primitiva 12. Cuesta `costo_secretar` y agrega `enzima_por_secrecion` a Z en la propia celda, después de comer y antes de moverse. Queda excluida del aprendizaje (beneficio demorado y compartido) y de la mutación si el bien público está desactivado. **Secreción inerte**: cuesta pero no agrega enzima (control).

### D5. Sensores
Se agrega `complejo_aqui = C / K_c_max` al final; los índices anteriores no cambian. `recurso_aqui`, `frente`, `frente_izq` y `frente_der` pasan a medir `(R + A) / K_max`. Con el bien público desactivado, A = 0 y no cambia nada.

### D6. Parámetros iniciales (`experiments/configs/bien_publico.toml`)
- Recurso simple escaso: `capacidad_max = 5` (con 3, LUCA se extingue antes de descubrir la secreción).
- Recurso complejo abundante: `K_c = 20`, regeneración 0,01, parches de escala 8.
- Enzima: secreción 1,0, costo 0,3, degradación 0,3, difusión 0,1, `k = 0,05`.
- Alimento libre: rendimiento 1,0, degradación 0,02, difusión 0,8.

**Recalibrado tras la revisión.** Con `k = 0,5` y degradación 0,1, un secretor recuperaba entre 50 y 150 veces su costo aunque lo rodearan aprovechados: no había dilema, secretar era "comer mejor". El objetivo prerregistrado de calibración (`experiments/fase2b/calibrar.py`) es que un secretor solo **no** recupere su costo y un grupo sí: beneficio propio / costo < 1 < grupo / costo. Con los valores elegidos, 0,81 < 1 < 1,39, y lo producido en total es 2,1 veces el costo.

### D8. Control de bien privado
`bien_publico.privado = true`: al secretar, el secretor digiere al instante en su celda lo que la enzima digeriría durante su vida (exponente `k·Z/δ`) y se queda con todo; no deja enzima ni alimento libre. Sirve para contrastar el bien público con el privado.

### D7. Métricas
- `tiene_secretar` y `usa_secretar` (automáticas).
- Totales de C, Z y A, y el alimento libre comido por organismo y paso.
- Fracción de enlazados entre los secretores y entre los no secretores.
- Energía media de secretores y no secretores.

## Risks / Trade-offs

- [Calibración: si el bien público es demasiado generoso, todos secretan sin dilema; si es pobre, nadie secreta] → barrido corto de `costo_secretar` y de la difusión de A antes de la evaluación; se reporta.
- [La difusión con `np.roll` de 3 campos cuesta tiempo] → son operaciones O(celdas), comparables a la regeneración; se mide en C4.
- [Que el bien público favorezca la asociación por cómo se eligieron los parámetros] → los controles (asociación desactivada e inerte) y la variación de la difusión permiten ver si el efecto depende de la localidad, como predice la teoría.
