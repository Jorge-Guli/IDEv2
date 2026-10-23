# Descripción del modelo (protocolo ODD)

> Versión vigente: **fase 1** (evolución básica, sin asociación). Este documento sigue el protocolo ODD (*Overview, Design concepts, Details*; Grimm et al. 2006, 2020) y se actualiza al cerrar cada fase. Los valores por defecto están en `src/simbio/config.py`.

## 1. Visión general

### 1.1 Propósito
Investigar bajo qué condiciones organismos artificiales simples, que se adaptan y se asocian localmente, pueden construir niveles crecientes de organización (ver `docs/00-hipotesis-fundacional.md`). La fase 1 provee y valida la base: organismos tipo bacteria que viven, se reproducen, heredan, mutan, aprenden y se adaptan.

### 1.2 Entidades, variables de estado y escalas
- **Celda** (grilla toroidal `alto × ancho`, por defecto 128×128): recurso `R`, capacidad base `K_base`. Como máximo un organismo por celda.
- **Organismo**: posición, orientación (8 direcciones), energía `E ∈ (0, E_max]`, estrés (promedio móvil del déficit de energía), línea base de recompensa, último ΔE, identificador, progenitor, generación, cepa.
  - **Genoma** (heredable): hasta `G = 24` genes; cada gen tiene un indicador de activo, la primitiva que expresa, pesos sobre 10 sensores y un sesgo. Rasgos: tasa base de mutación `μ`, sensibilidad al estrés `σ` y tasa de aprendizaje `η`.
  - **Ajustes plásticos** (no heredables): un ajuste por peso y sesgo de cada gen.
- **Escala temporal**: pasos discretos; un paso es una decisión por organismo.

### 1.3 Visión general del proceso y orden
En cada paso: (1) el entorno regenera recursos (con estación y cambios abruptos); (2) cada organismo actualiza su aprendizaje con el ΔE de su acción anterior; (3) sensa; (4) decide; (5) paga los costos basal, de genoma y de acción; (6) gira; (7) come; (8) avanza; (9) se divide; (10) mueren los que no tienen energía; (11) se actualiza el estrés. Todos los organismos actúan de forma sincrónica; los conflictos por una misma celda se resuelven en orden aleatorio.

## 2. Conceptos de diseño

- **Principios básicos.** Transiciones mayores de la evolución; quimiotaxis bacteriana tipo "correr y dar voltereta"; mutagénesis por estrés (respuesta SOS); efecto Baldwin (el aprendizaje guía la evolución sin heredarse).
- **Emergencia.** Las conductas de forrajeo, el tamaño del genoma, el uso de cada primitiva y los valores de los rasgos `μ`, `σ` y `η` emergen de la selección. Lo impuesto es la física (primitivas y costos) y el genoma inicial (LUCA).
- **Adaptación.** Cada organismo elige en cada paso la primitiva con mayor impulso positivo: el impulso es la suma de las activaciones `tanh` de los genes que la expresan. Una primitiva sin genes no está disponible.
- **Objetivos.** No hay una función objetivo explícita: lo único que persiste es lo que sobrevive y se reproduce. El aprendizaje usa como recompensa el ΔE relativo a la línea base del propio organismo.
- **Aprendizaje.** Regla de refuerzo local: los genes que impulsaron la acción ejecutada ajustan su respuesta en la dirección del gradiente de su activación, en proporción a `η · recompensa`. Los ajustes decaen y están acotados. La división no se evalúa por energía.
- **Predicción.** Ninguna explícita.
- **Percepción.** Local: recurso en la celda propia, al frente, al frente-izquierda y al frente-derecha; energía propia; ocupación de los 8 vecinos; frente bloqueado; último ΔE; ruido; constante.
- **Interacción.** Indirecta: competencia por recursos y por espacio. No hay interacción directa en la fase 1.
- **Estocasticidad.** Posiciones iniciales, voltereta, sensor de ruido, orden de resolución de conflictos, elección de la celda del hijo y mutaciones. Todo sale de generadores con semilla.
- **Colectivos.** No existen en la fase 1 (se introducen en las fases 2 y 3).
- **Observación.** Cada `registrar_cada` pasos se registran: población, nacimientos, muertes, energía media, recurso total, forrajeo (energía comida por organismo y paso), genes medios, perfiles genómicos distintos, presencia y uso de cada primitiva, rasgos medios, estrés, tasa de mutación efectiva y generación. Además se guardan la población final, el linaje completo e imágenes.

## 3. Detalles

### 3.1 Inicialización
`poblacion_inicial` organismos (por defecto 200) en celdas al azar, con energía 50 y genoma LUCA:

| Gen | Primitiva | Lógica |
|---|---|---|
| 1 | comer | `0.5 + 20·recurso_aquí − 3·energía` |
| 2 | avanzar | `0.3 + 4·recurso_frente − 10·recurso_aquí − 3·bloqueado` |
| 3 | voltereta | `−0.2 + 0.8·ruido + 2·bloqueado` |
| 4 | dividirse | `−5 + 8·energía` |

Rasgos de LUCA: `μ = 0.02`, `σ = 2`, `η = 0.05`. LUCA es viable con y sin aprendizaje (verificado).

### 3.2 Entrada
Sin datos externos. Variabilidad ambiental: estacionalidad `K·(1 + A·sin(2πt/P))` y regeneración del mapa de parches en el paso configurado.

### 3.3 Submodelos
- **Parches**: ruido blanco con filtro gaussiano (σ = 6 celdas) por FFT, normalizado a [0, 1] y elevado al exponente 2, multiplicado por `capacidad_max = 10`.
- **Regeneración**: `R ← min(R + 0.02·(K − R), K)`.
- **Metabolismo**: costo por paso de `0.3 + 0.01·genes_activos`, más la acción: avanzar 0.4, girar 0.05, voltereta 0.1, comer 0.05, descansar 0.
- **Comer**: toma `min(R, 4, E_max − E)`.
- **División**: requiere `E ≥ 20` y una celda vecina libre; cuesta 2; el resto se reparte por mitades. El hijo hereda el genoma mutado, el estrés del progenitor y ajustes plásticos en cero.
- **Mutación** con tasa `m = μ·(1 + σ·estrés)`: puntual por peso (prob. `m`, N(0, 0.3)); cambio de primitiva `0.3m`; duplicación `0.5m`; eliminación `0.5m` por gen; gen nuevo `0.2·G·m` por genoma; rasgos log-normales con prob. 0.2.
- **Estrés**: `estrés ← 0.95·estrés + 0.05·(1 − E/E_max)`.
- **Aprendizaje**: `r = clip((ΔE − base)/5, −1, 1)`; `ΔP_g = η·r·(1 − a_g²)·s` para los genes de la primitiva ejecutada; decaimiento 1 %/paso; ajustes acotados a ±2; `base ← 0.9·base + 0.1·ΔE`.
