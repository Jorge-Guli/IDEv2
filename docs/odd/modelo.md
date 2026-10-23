# Descripción del modelo (protocolo ODD)

> Versión vigente: **fase 1, cerrada el 2026-10-23** (evolución básica, sin asociación). Este documento sigue el protocolo ODD (*Overview, Design concepts, Details*; Grimm et al. 2006, 2020) y se actualiza al cerrar cada fase. Los valores por defecto están en `src/simbio/config.py`.

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
En cada paso: (1) el entorno regenera recursos (con estación y cambios abruptos); (2) cada organismo actualiza su aprendizaje con el ΔE de su acción anterior; (3) sensa; (4) decide; (5) paga los costos basal, de genoma y de acción; quien queda sin energía tras los costos muere antes de actuar; (6) gira; (7) come; (8) avanza; (9) se actualiza el estrés; (10) se divide. Todos los organismos actúan de forma sincrónica; los conflictos por una misma celda se resuelven en orden aleatorio.

## 2. Conceptos de diseño

- **Principios básicos.** Transiciones mayores de la evolución; quimiotaxis bacteriana tipo "correr y dar voltereta"; mutagénesis por estrés (respuesta SOS); efecto Baldwin (el aprendizaje guía la evolución sin heredarse).
- **Emergencia.** Las conductas de forrajeo, el tamaño del genoma, el uso de cada primitiva y los valores de los rasgos `μ`, `σ` y `η` emergen de la selección. Lo impuesto es la física (primitivas y costos) y el genoma inicial (LUCA).
- **Adaptación.** Cada organismo elige en cada paso la primitiva con mayor impulso positivo: el impulso es la suma de las activaciones `tanh` de los genes que la expresan. Una primitiva sin genes no está disponible.
- **Objetivos.** No hay una función objetivo explícita: lo único que persiste es lo que sobrevive y se reproduce. El aprendizaje usa como recompensa el ΔE relativo a la línea base del propio organismo.
- **Aprendizaje.** Regla de refuerzo local: los genes que impulsaron la acción ejecutada ajustan su respuesta en la dirección del gradiente de su activación, en proporción a `η · recompensa`. Los ajustes decaen y están acotados. La división queda fuera de la recompensa, de la línea base y del sensor de ΔE.
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
- **División**: requiere `E ≥ 20` y una celda vecina libre; cuesta 2; el resto se reparte por mitades. El hijo hereda el genoma mutado y nace con estrés y ajustes plásticos en cero. Un intento fallido no cuesta nada.
- **Mutación** con tasa `m = min(μ·(1 + σ·estrés), 0.2)`: puntual por peso (prob. `m`, N(0, 0.3)); cambio de primitiva `0.3m`; duplicación `0.5m`; eliminación `0.5m` por gen; gen nuevo `0.2·G·m` por genoma; rasgos log-normales con prob. `min(1, 10m)`. Control: modo "barajado" (estrés de otro organismo al azar).
- **Estrés**: `estrés ← 0.95·estrés + 0.05·hambre`, con `hambre = clip((25 − E)/25, 0, 1)`, calculado antes de la división.
- **Aprendizaje**: `r = clip((ΔE − base)/5, −1, 1)`; `ΔP_g = η·r·(1 − a_g²)·s` para los genes de la primitiva ejecutada; decaimiento 1 %/paso; ajustes acotados a ±2; `base ← 0.9·base + 0.1·ΔE`.

## Anexo: fase 2 (asociación), cerrada el 2026-10-23

Se agrega a la física, sin cambiar lo anterior (detalle en `openspec/specs/asociacion/spec.md` y en el diseño archivado de la fase 2):
- **Primitivas:** unirse (con el de enfrente; costo 0,1), soltarse (rompe todos los enlaces; 0,05), compartir (cede 20 % de E en partes iguales a los enlazados, que reciben ×0,9; 0,05; ocurre antes de comer), dividirse unido (como dividirse; el hijo queda enlazado y orientado como su progenitor) y conjugar (copia un gen al azar en una ranura libre de un enlazado; 0,5).
- **Enlaces:** guardados por dirección con la identidad del socio. Mantenerlos cuesta 0,02 por enlace y paso. Se validan en cada paso: se rompen si el socio deja de estar en esa posición relativa o muere.
- **Movimiento:** simultáneo, y se puede entrar a la celda que deja alguien que avanza en la misma dirección. **Adhesión** (activada por defecto): un grupo enlazado se mueve junto o no se mueve (punto fijo), y quien queda frenado no paga el avance.
- **Sensores sociales:** enlaces/8, energía media de los enlazados, enlazado al frente, similitud de etiqueta con el de enfrente.
- **Etiqueta** heredable de 2 valores, sin efecto físico.
- **Aprendizaje:** no refuerza dividirse, dividirse unido, compartir ni conjugar; descuenta del ΔE la energía recibida de otros.
- **Controles:** asociación desactivada, inerte (las primitivas cuestan pero no hacen nada), sin beneficio (eficiencia 0) y positivo (eficiencia 2).
- **Dispositivo:** CPU (NumPy) o GPU (CuPy), detectado automáticamente. El azar se genera siempre en CPU.

## Anexo: fase 2b (bien público), cerrada el 2026-10-23

Se activa con `bien_publico.activo = true`. Detalle en `openspec/specs/bien-publico/spec.md`.
- **Campos:** recurso complejo C (no comestible; parches propios, regeneración 0,01, capacidad 20), enzima Z y alimento libre A.
- **Primitiva secretar** (costo 0,3): agrega 1 unidad de Z en la propia celda, después de comer. No se refuerza por aprendizaje.
- **Dinámica del entorno, en cada paso:** Z se difunde (0,1) y se degrada (0,3); la digestión convierte `d = C·(1 − exp(−0,05·Z))` de C en A; A se difunde (0,8) y se degrada (0,02).
- **Comer:** toma de R y después de A, hasta 4 por paso. Los sensores de alimento miden R + A; hay un sensor nuevo, `complejo_aqui`.
- **Controles:** secreción inerte; bien privado (el secretor digiere al instante en su celda lo que su enzima digeriría en su vida y se lo queda).
- **Movimiento de grupos:** se agrega el modo opcional `asociacion.movimiento = "empuje"`. Cada grupo conexo se desplaza una celda en la dirección más alineada con la suma de las orientaciones de sus miembros que avanzan, si esa suma alcanza la mitad del tamaño del grupo y el destino está libre.
