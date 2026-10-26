# Descripción del modelo (protocolo ODD)

> Versión vigente: **fase 4a, cerrada el 2026-10-25**. El cuerpo describe la fase 1 (evolución básica); las fases siguientes se agregan como anexos al final. Este documento sigue el protocolo ODD (*Overview, Design concepts, Details*; Grimm et al. 2006, 2020) y se actualiza al cerrar cada fase. Los valores por defecto están en `src/simbio/config.py`.

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
- **Emergencia.** Las conductas de forrajeo, el tamaño del genoma, el uso de cada primitiva y los valores de los rasgos `μ`, `σ` y `η` emergen de la selección. Lo impuesto es la física (primitivas y costos) y el genoma inicial (LUCA, por *Last Universal Common Ancestor*: el último antepasado común universal).
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

## Anexo: fase 2c (depredación limitada por tamaño), cerrada el 2026-10-24

Se activa con `depredacion.activa = true`. Detalle en `openspec/specs/depredacion/spec.md`.
- **Ataque:** en cada paso, después de pagar los costos y antes de actuar, cada organismo vivo es atacado con probabilidad `p` (desde el paso `inicio`; si `rampa > 0`, `p` sube linealmente desde 0 durante `rampa` pasos).
- **Modo `tamano`:** un ataque mata con probabilidad `1 − (tamaño − 1)/(refugio − 1)`, donde el tamaño es el de la componente conexa de enlaces del organismo (o mata siempre bajo el refugio si `gradual = false`); los grupos de tamaño ≥ `refugio` no mueren.
- **Controles:** `uniforme` (todo ataque mata) y `aleatorio` (un ataque perdona con probabilidad 0,9, sin relación con los enlaces).
- **Azar:** el depredador usa un generador propio, y sortea siempre los mismos números en todas las condiciones, para que las comparaciones queden pareadas.
- **Configuración de referencia:** `experiments/configs/depredacion.toml` (movimiento por empuje, `p = 0,015`, refugio 2, inicio 2000; la variante gradual agrega `rampa = 8000`).

## Anexo: fase 3 (coordinación del grupo), cerrada el 2026-10-24

Detalle en `openspec/specs/coordinacion/spec.md`. Cambia la forma del genoma (14 primitivas, 20 sensores): los resultados de las fases anteriores se reproducen en el commit `8099dd8`, y los genomas guardados se completan con pesos nulos al cargarlos.
- **Escalada del refugio** (`depredacion.refugio_final`, `escalada_inicio`, `escalada_pasos`): el refugio vigente sube linealmente y puede no ser entero.
- **Sensores de rumbo** (`coordinacion.rumbo`), solo a través de enlaces: seno y coseno medios del ángulo entre el rumbo de cada socio y el propio (en octavos de vuelta; seno positivo: el socio apunta hacia el lado de `girar_der`), y fracción de socios que avanzaron en el paso anterior.
- **Señales** (`coordinacion.senales`): primitiva `senalar` cuyos genes no compiten por la acción; la señal es su impulso recortado a [0, 1], cuesta 0,05 por unidad y paso y no se refuerza. Sensores: señal media de los socios y señal propia del paso anterior.
- **Control barajado:** los sensores sobre los socios toman los valores de otro organismo enlazado al azar.
- **Empuje colectivo vectorizado**, con resultado idéntico al original.
- **Limitación conocida:** en el empuje colectivo, un rumbo diagonal aporta √2 a la suma (corregido en el modo "fuerza" de la fase 3c).

## Anexo: fase 3c (movimiento de grupos por fuerza), cerrada el 2026-10-24

- **Modo `asociacion.movimiento = "fuerza"`.** Cada empuje es un vector unitario. El grupo se desplaza en la dirección más alineada con la suma, con probabilidad min(1, proyección de la suma sobre esa dirección / tamaño^α), si el destino está libre. **Regla adoptada a partir de esta fase: α = 0,5** (`asociacion.exponente_arrastre`), el arrastre de una colonia plana. Con α = 1 no se sostienen ni los pares.
- El modo "empuje" (umbral) sigue disponible sin cambios, para reproducir las fases anteriores.

## Anexo: fase 4a (restricción flagelar), cerrada el 2026-10-25

- **`fisica.refractario_division` = T** (0 por defecto): tras una división lograda, progenitor e hijo quedan T pasos sin poder elegir avanzar; el grupo puede arrastrarlos. Control `refractario_modo = "aleatorio"`: períodos de T pasos sorteados con probabilidad 2 × divisiones del paso / población.
- **Contadores de vida por organismo:** avances y divisiones. Métricas de especialización en grupos de 3 o más (concentración reproductiva, correlación avanzar/dividirse, fracción que nunca se dividió). Esta última mide hojas por construcción: se usa con un modelo nulo.

## Anexo: fase 4c (modelo nulo, control de costo privado), hecha el 2026-10-25
- Sin cambios de física. Control `fisica.costo_division` (costo privado de dividirse, sin inmovilidad).

## Anexo: fase 5 (retornos crecientes, energía compartida), explorada el 2026-10-25
- **Maquinaria por uso** (`fisica.maquinaria_gamma`, `maquinaria_memoria`, `maquinaria_ref`, `maquinaria_max`): el rendimiento de comer y el éxito de avanzar crecen con el uso reciente de esa acción (media móvil por organismo); 0 = apagada.
- **Puentes citoplasmáticos** (`asociacion.difusion_energia` = κ): la energía se difunde por los enlaces a razón de κ·(diferencia)/8 por paso, sin decisión del genoma; `difusion_aprende` decide si entra en la señal de aprendizaje.

## Anexo: fase 6 (memoria interna), cerrada el 2026-10-25
- **Memoria** (`memoria.activa`): dos variables en [0, 1] por organismo. Las escriben las primitivas MEMORIA_A y MEMORIA_B (no ocupan la acción): m ← clip(m + tasa·impulso). Se leen con dos sensores y el hijo las hereda.
- Señal (SENALAR) y memoria son salidas continuas que no compiten con la acción del paso.

## Anexo: fases 7 y 8 (estaciones, pista, toxicidad diferida), cerradas el 2026-10-26
- **Estaciones** (`estaciones.activa`): cada celda tiene un tipo de comida (+1 o −1, en parches de escala `escala_parche`; 1,0 = mosaico fino de la fase 8). Una estación oculta se alterna cada `periodo` pasos y decide qué tipo nutre.
- **Toxicidad** (`toxicidad`):
  - "inmediato": la comida fuera de estación resta castigo × lo comido;
  - "diferido": nutre como la buena, pero deja un veneno de (1 + castigo) × lo comido, que se descuenta a razón de `tasa_veneno` por paso; al dividirse, el veneno se reparte.
- **Sensores:** tipo de comida aquí, y una pista de la estación con probabilidad `p_pista` por paso (`pista_informativa = false`: valor al azar, como control). La pista se sortea con un generador propio, para no alterar el resto de la simulación.

## Anexo: fase 9 (regulación condicionada), cerrada el 2026-10-26
- **Condición de expresión por gen** (`cond`, 5 valores): siempre, o solo si la memoria A (o B) está por encima o por debajo de 0,5. Con la memoria apagada no actúa.
- **Mutación de la condición** (`herencia.k_condicion`): solo si la memoria está permitida. Los genes duplicados copian su condición; los nuevos nacen con condición 0. Los genomas guardados antes de esta fase se cargan con condición 0.
- **Rampa de toxicidad** (`estaciones.rampa_toxicidad`): la toxicidad crece linealmente de 0 a su valor pleno.

## Anexo: fase 10 (peldaños para la memoria), cerrada el 2026-10-26
- **Memoria tipo cerrojo** (`memoria.umbral`): los impulsos de memoria de magnitud ≤ umbral no la cambian.
- **Rampa de la pista** (`estaciones.p_pista_inicial`, `rampa_pista`): la probabilidad de la pista baja linealmente desde el valor inicial.
- **Digestión inducible** (`estaciones.induccion`, `inercia_digestion`):
  - un estado digestivo d por organismo (inicial 0,5, heredado al dividirse) sigue a la memoria A: d ← d + (m_A − d)/inercia;
  - lo absorbido de la comida de tipo t (nutrientes y veneno) se multiplica por 1 + induccion·(2d − 1)·t, y la energía se recorta a E_max.
- **Métrica de seguimiento:** covarianza normalizada entre (2m − 1) y la estación. La versión prerregistrada tiene aliasing de muestreo (máximo ≈ 0,5); la corregida descarta los primeros 250 pasos de cada estación.

## Anexo: fase 11 (modulación y decisión estocástica), cerrada el 2026-10-26
- **Modulación** (`herencia.modulacion`):
  - condiciones 5 y 6: la memoria A o B cambia el signo de la respuesta del gen a los receptores químicos (`gen.SENS_MODULABLES` = tipo de comida): z = b + w·s + (2m − 2)·w_q·s_q;
  - con la modulación apagada, la condición muta solo entre 0 y 4;
  - **efecto lateral:** con la memoria en 0,5, la modulación anula el receptor.
- **Decisión** (`fisica.decision`):
  - "argmax" (por defecto): el impulso mayor; descansar si ninguno es positivo;
  - "softmax": la acción se sortea con probabilidad ∝ exp(impulso/`temperatura`), con descansar siempre disponible con impulso ≥ 0. Truco de Gumbel con el azar de la CPU.
- **Memoria inicial** (`memoria.inicial`): solo se aplica a los fundadores; los hijos heredan la memoria del progenitor.
