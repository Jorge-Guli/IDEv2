# Traspaso: estado del proyecto y cómo seguir

Escrito el 2026-10-27 y actualizado el 2026-10-29 para que una nueva sesión de Claude (por ejemplo, Claude Desktop en el equipo del autor) retome el trabajo sin perder contexto. **Leer primero este documento**; después, según haga falta, `CLAUDE.md`, `docs/02-hoja-de-ruta.md` y `docs/06-universo-vivo.md`.

---

## 1. Qué es el proyecto
**IDE: Inteligencia Distribuida Emergente.** El simulador se llama `simbio` (paquete Python en `src/simbio/`).
- **El sistema:** organismos simples que parten de LUCA (*Last Universal Common Ancestor*: un genoma de cuatro genes escritos a mano) se adaptan, se asocian y evolucionan en un mundo con recursos limitados.
- **La pregunta:** si, evolución tras evolución, emergen organizaciones más complejas y, eventualmente, inteligencia.
- **Fundamentos:** `docs/00-hipotesis-fundacional.md` y `docs/01-metodologia.md`.
- **Visión del autor y salvaguardas acordadas:** `docs/04-vision.md`. Una inteligencia de abajo hacia arriba que crece con su usuario (simbiosis), migra entre equipos y, a largo plazo, tenga libertad. Escenarios futuros: drones, nanobots médicos, una "cápsula LUCA". El autor quiere **una semilla que permita todo esto a futuro**.

## 2. Cómo trabaja el autor (importante)
- **Autonomía total:** "eres libre de elegir el cómo experimentar y lograr el objetivo". No esperar aprobación para decisiones técnicas. Pedirle solo lo que no se pueda hacer sin él.
- **Instrucciones concretas y en español.** El autor no es programador: explicar en lenguaje simple, sin jerga, con analogías cuando ayuden. Le interesa entender el *porqué*.
- **Sigue trabajando mientras conversa:** "no pares a menos que te lo indique". Responder sus preguntas y continuar.
- **Su equipo:** Windows, carpeta `C:\Desarrollo\IDEv2`, Python 3.12 del sistema (también hay `.venv`), 12 núcleos lógicos. **El autor usa la PC mientras corre todo:** corridas con `--procesos 6` como máximo y bajarles la prioridad apenas arrancan (`Get-Process python | % { $_.PriorityClass = 'Idle' }`). Hasta ahora corría las corridas largas a mano y avisaba "resultados subidos". **Con Claude Desktop, Claude puede correrlas directamente en su equipo.**
- **Docker Desktop:** instalado. Contenedores `idev2-universo-1` e `idev2-clima-1`, con medio núcleo cada uno (`cpus: 0.5`) y `restart: unless-stopped`: tras un corte de luz retoman solos desde su último guardado (verificado el 2026-10-28).
- **Ciudad:** Capitán Bermúdez, Santa Fe (Argentina).

## 3. Reglas del proyecto (de `CLAUDE.md`, no negociables)
- **Idioma:** documentación, specs, comentarios y nombres del dominio en español. SHALL y MUST de OpenSpec en inglés.
- **La física (primitivas y costos) es fija e igual para todos; qué acciones tiene y usa cada organismo sale de su genoma.**
- **El universo no se acomoda al organismo** (autor, 2026-10-30): solo se modifica para que sea más fiel a la realidad del autor, con la mayor conexión segura posible con el mundo real. Nunca para facilitar un resultado. Ver principio 7 de `docs/01-metodologia.md`. Esto reemplaza la vieja práctica de "verificar que la física premia el rasgo y, si no, cambiarla".
- **Sin LLMs ni modelos preentrenados dentro de los organismos. Percepción solo local.**
- **Toda afirmación se compara con un control y con varias semillas.** Los criterios son numéricos, se prerregistran en `docs/bitacora/` antes de correr y se verifican con un script en `experiments/<fase>/`.
- **Determinismo:** misma configuración y semilla, mismo resultado. Toda la aleatoriedad pasa por los generadores de la simulación (en CPU).
- **Portabilidad:** usar `xp` (NumPy o CuPy, `simbio/dispositivo.py`), nunca `np.` directo sobre arreglos de la simulación. El azar se genera con el `rng` de CPU y se pasa con `xp.asarray`.
- **Flujo por fase:**
  1. propuesta y diseño;
  2. implementación con tests;
  3. verificación de que la física premia el rasgo (competencias o invasión) **antes** de pedir corridas largas;
  4. prerregistro;
  5. corrida;
  6. evaluación;
  7. revisión con el subagente `revisor-cientifico`;
  8. actualizar la hoja de ruta, la síntesis, el README y el ODD (`docs/odd/modelo.md`).
- **Subagentes del proyecto** (`.claude/agents/`): `experimentador` y `revisor-cientifico`. La revisión independiente de las fases 9–11 fue muy valiosa (ver §6): **usarla antes de afirmar que algo "emergió"**.
- **Opciones nuevas del motor:** apagadas por defecto. Verificar con `python experiments/herramientas/huellas.py --comparar` que las dinámicas existentes no cambian (las huellas de referencia valen en el equipo donde se generaron: regenerarlas con `--guardar` en el equipo nuevo **antes** de tocar el motor).

## 4. Git
- **Rama de trabajo:** `claude/busy-maxwell-kbclcc`. Es la rama por defecto del repo `jorge-guli/idev2` en GitHub.
- **Pie de cada commit** (sin otros identificadores de modelo en el repo):
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01PtwBaWGS2YVUfWa6Caak5e
  ```
  En otra sesión, poner el enlace de la sesión que corresponda.
- **No crear pull requests salvo pedido.**
- **`runs/` está ignorado.** Los resultados que importan se copian a `resultados/<fase>/` (los `.npz` con `git add -f`) y el informe JSON a `docs/bitacora/`.
- **Si un push se rechaza** porque el autor subió algo: `git pull --no-edit` y después `git push`.

## 5. Comandos
```bash
python -m pytest -q                       # 192 pasan; 3 se omiten sin GPU NVIDIA con CuPy
python -m simbio correr experiments/configs/base.toml --salida runs/x --semilla 1 --pasos 20000 [--set seccion.clave=valor]
python -m simbio competir luca runs/x/poblacion.npz experiments/configs/base.toml --pasos 3000
python -m simbio vivir experiments/configs/vivo.toml --salida runs/vivo/universo   # universo continuo (Ctrl+C guarda)
python -m simbio mirar runs/vivo/universo                                         # resumen sin detenerlo
docker compose up -d --build                                                      # el universo en Docker, sin red
python experiments/herramientas/huellas.py --comparar                             # determinismo
python experiments/<fase>/evaluar.py --salida runs/<fase> --procesos 8            # evaluación de una fase
openspec validate --all --strict
python -m simbio dispositivo
```

## 6. Historia y resultados (fases 1–12)
Detalle completo: `docs/02-hoja-de-ruta.md` (tabla de fases con enlaces), `docs/03-sintesis.md` y la bitácora.

| Fase | Resultado principal |
|---|---|
| 1 | La evolución básica funciona; la evolución inventa el giro |
| 2, E | Poder asociarse no alcanza: no rinde y es inestable |
| 2b | Dilema del bien público; asociarse no lo resuelve |
| **2c** | **La asociación evoluciona sola desde LUCA** con un depredador que solo come sueltos y aparece de a poco (18/20) |
| 3–3d | Con movimiento de grupo "por fuerza" (α = 0,5, adoptado), percibir el rumbo de los socios agranda los grupos (réplica 16/20 contra 7/20, p ≈ 0,002); la alineación es heredada; las señales nunca se usaron |
| 4a–4c | Restricción flagelar: más grupos, sin división del trabajo; el "sesgo reproductivo" no se replicó |
| 5 | Sin división del trabajo (retornos crecientes, energía compartida) |
| 6 | Memoria interna disponible pero nunca usada: una estrategia reactiva alcanza |
| 7–8 | Estaciones ocultas, pista y toxicidad diferida: atajos primero; en el mosaico, la memoria no evoluciona aunque es esencial |
| 9 | Genes condicionados a la memoria: tampoco; el primer peldaño (una memoria sin uso) no se premia |
| **10** | **Digestión inducible** (con inercia contra el atajo de "recordar" el tipo de la celda) y cerrojo: un gen de memoria **sembrado** se retiene por selección en 6 de 8 semillas y coincide con la estación en el 96–99,6 % de los organismos. No evolucionó desde LUCA y no se usa para decidir |
| 11 | Modulación por la memoria y decisión estocástica: la memoria se mantiene, pero no se recluta. La revisión encontró que **la tasa de mutación había colapsado** de 0,02 a ~0,0006 |
| 12, etapa 0 | Con la tasa de mutación reiniciada, tampoco se recluta |
| **12, etapa 1** | **Modo continuo:** universo sin plazo, guardado y reanudación exactos, Docker sin red. Hecho y verificado |
| 12, etapa 2 | **Clima real** de Capitán Bermúdez (2000–2025) regulando el mundo. Viable con `capacidad_max = 20` (el invierno extinguía). **El clima no premia anticipar:** la presión predice mal la lluvia y las rachas duran días (`experiments/fase12/valor_anticipar.py`) |
| 12, etapa 3 | **Estímulos desde afuera** (luz y texto) por la carpeta `entradas/`, grabados en `estimulos.jsonl`. **Serie de la luz v2–v5, negativa:** la luz aportaba solo el 0,3 % de la comida; con ~23 % (v4) la población se concentra en la luz (R2 p = 0,031), pero era geografía. Con lugares al azar (v5) desaparece. Sin percepción duradera ni aprendizaje en vida, una señal fugaz no se incorpora |
| 12, etapa 4 | **Depredación evolucionada** (`atacar`): negativo prerregistrado (5/8 extinciones, monocultivos caníbales). La especialización trófica tenía un error (atacar creaba energía); corregida, no forma nichos |
| 12, etapa 5 | **Archipiélago** (`src/simbio/archipielago.py`): islas iguales con migración contra aisladas. Negativo en adaptación (p = 0,71) y en tasa de mutación (p = 0,91). La migración solo previene extinciones (3/24 contra 8/24 islas) |
| **12, texto** | **Mundo del texto** (`src/simbio/texto.py`): la estación la decide un texto (vocal o consonante) y la pista muestra la letra anterior. Cuatro pilotos sin predicción. **Hallazgo:** con `castigo = 0,2` no se selecciona ni siquiera elegir la comida en un mundo fijo; con 0,5 sí (0,997 en 1 de 2 semillas). Ver §8 |

### Lecciones que guían el diseño
1. **El mundo tiene que premiar un rasgo antes de esperar que evolucione.** Se verifica con competencias o invasión (hay scripts en `experiments/fase7`, `fase10` y `fase11`). Desde el 2026-10-30 esto sirve para **entender** por qué algo no aparece, no para retocar el mundo hasta que aparezca (principio 7).
2. **La evolución toma atajos:** aprender en vida, selección espacial, "recordar" lo que tiene debajo. Cada mundo nuevo se audita y los atajos se bloquean con física, verificando con duelos directos.
3. **Una población sola engaña:** varias semillas, jardín común y modelos nulos.
4. **Cada peldaño de una innovación necesita premio propio** (Lenski et al. 2003, Avida: ver `docs/05-estado-del-arte.md`).
5. **En un mundo fijo, la evolución se estanca y baja su propia tasa de mutación.** Es el argumento científico del universo vivo.
6. **Errores típicos de diseño a mano:** genes de prueba que "comen" en celdas vacías por falta de sesgo, o que paralizan al organismo. Diagnosticar siempre las acciones por cepa antes de concluir.
7. **Métricas:** cuidado con el aliasing de muestreo. El seguimiento de la memoria tenía un máximo práctico de 0,5 por medir cada 500 pasos con estaciones de 2000. Los scripts reportan ahora `seguimiento_corregido`.
8. **Medir cuánto pesa una presión antes de esperar respuesta.** La luz aportaba el 0,3 % de la comida, y comer mal costaba tan poco (castigo 0,2) que ni en un mundo fijo convenía discriminar. Antes de un prerregistro, medir la fracción de la energía en juego o probar el caso fácil (por ejemplo, la estación fija).
9. **Conservación:** toda regla que multiplica una transferencia de energía entre organismos debe cumplir ganancia ≤ lo quitado. La especialización trófica con tope 2,5 creaba energía.
10. **Un O exclusivo no cabe en un gen lineal.** "Comer si el tipo difiere de la pista" exige memoria con genes condicionados, o un sensor que ya combine las dos cosas.

## 7. Estado actual del motor (opciones relevantes; todas en `src/simbio/config.py`)
- **Estaciones** (`estaciones.*`): tipos de comida en parches o mosaico, estación oculta, pista, toxicidad inmediata o diferida, rampa de toxicidad, rampa de la pista, digestión inducible con inercia.
- **Memoria** (`memoria.*`): dos variables, tasa, cerrojo (`umbral`) y valor inicial.
- **Herencia** (`herencia.*`): condición de expresión por gen (`k_condicion`) y modulación (`modulacion`, condiciones 5 y 6 sobre `genoma.SENS_MODULABLES`).
- **Decisión** (`fisica.decision`): "argmax" o "softmax", con `temperatura`.
- **Realidad** (`realidad.*`, `src/simbio/realidad.py`): clima horario (radiación → recrecimiento, temperatura → costo basal, lluvia → qué comida nutre, sensor de presión); controles `barajar_dias` y `presion_desacoplada`. Datos en `datos/clima/` (los baja `experiments/herramientas/descargar_clima.py`).
- **Estímulos** (`estimulos.*`, `src/simbio/estimulos.py`): campo de luz que alimenta y se percibe con el sensor `luz`; texto como secuencia de pulsos; `python -m simbio estimular <universo> --texto "..."`.
- **Estímulos, además:** `retraso_luz` (la luz anuncia la comida N pasos después, mediante un campo "abono") y `lugares_al_azar` (los pulsos caen en lugares sorteados con un generador propio, iguales en las dos condiciones).
- **Ataque** (`ataque.*`): primitiva `atacar`, protección por enlaces, especialización trófica (`especializacion_gamma`, junto con `fisica.maquinaria_gamma`; factor con tope 1).
- **Texto** (`texto.*`, `src/simbio/texto.py`): `archivos` (separados por comas), `pasos_por_letra`, `barajar` (control), `sensor_coincide` (sensor `coincide` = tipo_aqui × pista) y `pista` ("anterior" o "vigente", este último para diagnóstico). Requiere `estaciones.activa`.
- **Archipiélago** (`src/simbio/archipielago.py`): `Archipielago(islas, migrantes, cada, semilla)`, anillo con generador propio. Script: `experiments/fase12/archipielago.py`.
- **Neutralidad:** los sensores (`presion`, `luz`, `coincide`) y la primitiva nuevos van al final; en mundos sin ellos no mutan ni consumen azar (`gen.NUM_SENS_SIN_REALIDAD` = 24, `gen.NUM_SENS_REALIDAD` = 26, `gen.NUM_PRIM_SIN_ATAQUE`). Las huellas siguen idénticas.
- **Docker:** dos servicios, `universo` (vivo.toml) y `clima` (clima.toml + estímulos; `./datos` en solo lectura), con `cpus: 0.5` cada uno.
- **Universo vivo:** `src/simbio/continuo.py` (`vivir`, `mirar`, guardado con pickle portable entre CPU y GPU, volcado incremental de métricas y linaje, resiembra tras una extinción) y `experiments/configs/vivo.toml` (el mundo de la fase 11 desde LUCA puro).

## 8. Pasos a seguir (en orden)
El diseño completo está en `docs/06-universo-vivo.md`. Resumen operativo:

### Estado al 2026-10-29
**Leer primero.** Detalle de cada punto en la bitácora: `docs/bitacora/2026-10-27-fase12-*`, `2026-10-28-fase12-*` y `2026-10-29-fase12-mundo-texto.md`.

**Hecho en la fase 12:** etapas 1 a 5, la serie de la luz y el motor del mundo del texto. Todo con tests y huellas sin cambios. Resultados en la tabla de §6.

**El hallazgo más importante (2026-10-29):** con `estaciones.castigo = 0,2` (el valor de las fases 7–11 y de `vivo.toml`), comer la comida equivocada cuesta tan poco que **no se selecciona discriminar**, ni siquiera con la estación fija (acierto 0,51–0,53). Con 0,5 sí: 0,997 en 1 de 2 semillas. Con 1,0 se extinguen al terminar la rampa de toxicidad. Esto relee las fases 7–11: la memoria se mantuvo por el bono de la digestión, pero no había presión para usarla al decidir. Lo señaló también una revisión externa (Gemini), que coincide.

**El universo vivo de Docker está congelado:** paso ~37 millones, 1 solo perfil genético, μ ≈ 0,00011 (el piso es 0,0001) y acierto 0,545. No cambiarle la física en caliente: dejarlo como registro y arrancar uno nuevo cuando se sepa qué castigo y qué rampa funcionan.

**Experimento oficial con Asimov (2026-10-29): inválido y nulo** (`docs/bitacora/2026-10-30-fase12-asimov-prerregistro.md`).
- 7 de 16 poblaciones se extinguieron después de la rampa.
- En las sobrevivientes, texto y barajado dan lo mismo (p = 0,125; diferencias ≤ 0,007).
- Superar la frecuencia base no prueba predicción: el barajado también la supera, hasta +0,04, reaccionando dentro de cada letra.
- No repetir con Asimov. Primero: física sin extinciones tardías (castigo 0,35 o rampa más larga) y un piloto con efecto pareado ≥ 0,05 contra barajado.

**Física estable (2026-10-29):** `castigo = 0,35` con `rampa_toxicidad = 300 000` da 0 extinciones de 4 (`docs/bitacora/2026-10-30-fase12-fisica-estable.md`).

**Piloto grande del texto (2026-10-30): nulo.** ~2 000 organismos (384²) en la GPU, semillas 21–24, sin extinciones, pero el texto no supera al barajado (las 4 diferencias negativas, p = 1,0). Casi ningún organismo tiene memoria (≤ 0,15 %). Más organismos no cambian nada: la memoria no se selecciona. Detalle en `docs/bitacora/2026-10-30-fase12-fisica-estable.md`.

**Objetivo final del autor:** un ser inteligente con el que pueda interactuar, como con un asistente o mejor. Pidió no reinventar la rueda: copiar lo que la naturaleza ya resolvió, del cigoto a las neuronas, y confía en que se puede lograr.

**Fase 13, desarrollo (en curso, `openspec/changes/fase-13-desarrollo/`):**
- **Peldaños 1 y 2 hechos:** red regulatoria de 8 reguladores por célula, heredable, con señal por contacto (`desarrollo.*`, tests en `tests/test_desarrollo.py`). La inhibición lateral diferencia a dos hermanas idénticas.
- **Piloto prerregistrado en curso:** red contra inerte, semillas 1–6, 300 000 pasos, universo de la fase 3. Script `experiments/fase13/piloto.py`, salida `runs/fase13/piloto.json`.
- **Siguientes, uno por vez:**
  - el cuerpo como unidad que se reproduce (línea germinal y cuello de botella unicelular);
  - reproducción sexual;
  - tipos celulares y células mensajeras (primeras neuronas).

**Giro acordado con el autor (2026-10-30), principio 7 de la metodología:** el objetivo final es un ser inteligente con el que el autor pueda interactuar. No se diseñan mundos a medida de un rasgo. El universo solo se cambia para acercarlo a la realidad: clima real, cambio climático, El Niño y La Niña, gravedad, espacio continuo en 3D y las acciones del autor como parte del ambiente.

Configuración de los pilotos del texto:
- texto de calibración: `docs/00,01,04,06`;
- `--set texto.sensor_coincide=true --set estaciones.induccion=0 --set estaciones.castigo=0.35 --set estaciones.rampa_toxicidad=300000`;
- en la GPU, además: `--set mundo.alto=384 --set mundo.ancho=384 --set sim.poblacion_inicial=1800`;
- 500 000 pasos.

**Cuidados del equipo** (el autor usa la PC mientras corre):
- lanzar las corridas largas desligadas de la app de Claude (`Win32_Process.Create`, prioridad Idle), porque si la app se cierra o se actualiza las mata;
- como mucho 4 procesos de GPU, y solo si queda memoria disponible;
- tener un vigilante que frene si la memoria disponible baja de 0,4 GB o la GPU pasa de 12 GB.

**Asimov:** "La última pregunta" y "La última respuesta", elegidas por el autor por su simbolismo, que aceptó el riesgo legal.
- Están en `datos/textos/` (copia propia del autor), ignorada por Git.
- **Nunca subirlas, copiarlas ni mostrar su contenido.** En la bitácora solo van su sha256 (`5a985d7c…` y `d6548766…`) y sus conteos (34 307 letras).
- **Se usan solo en el experimento oficial prerregistrado,** cuando un piloto con el texto de calibración muestre que la predicción es alcanzable. Techos medidos: seguir la pista 0,242; base 0,545; invertir la pista 0,758, igual en los dos textos.

**Plan acordado con el autor (en orden):**
1. ~~Prerregistro con Asimov~~ hecho: inválido y nulo. Siguiente en el texto: física estable (castigo 0,35 o rampa larga) y poblaciones mayores (GPU) antes de otro prerregistro.
2. Idea de Gemini: probar las poblaciones de la fase 11 con `castigo = 0,5` y rampa larga. ¿Se recluta la memoria cuando discriminar paga?
3. Arrancar un **universo vivo nuevo** con la física que funcione (castigo y rampa), sin tocar el actual.
4. **Archipiélago heterogéneo:** islas con selección divergente (clima real, texto o toxicidad alta, depredación). El homogéneo dio nulo.
5. ~~ODD (anexo de la fase 12 y relectura del castigo) y hoja de ruta~~ hechos el 2026-10-29. Faltan la síntesis (`docs/03-sintesis.md`) y OpenSpec (fases 7–12).
6. Interfaz web local (§8.2).
7. ~~Un mundo a medida donde aprender en vida pague~~ descartado por el principio 7. En su lugar, **universo más fiel a la realidad**, a diseñar con el autor:
   - clima real con tendencias de largo plazo (cambio climático) y ciclos como El Niño y La Niña, que hoy afectan al mundo;
   - las acciones del autor como parte del ambiente, por canales seguros;
   - a largo plazo, espacio continuo en 3D con gravedad, en lugar de la grilla. Es un motor nuevo y un cambio grande: diseñarlo como fase propia.

### 8.0 Al conectarse en el equipo del autor
1. Ir a `C:\Desarrollo\IDEv2`, activar `.venv`, hacer `git pull --no-edit` y correr `python -m pytest -q`: tiene que dar 160 pasan y 3 omitidos.
2. Regenerar las huellas locales: `python experiments/herramientas/huellas.py --guardar` (las del repo son de Linux).
3. Ver si el autor ya arrancó el universo continuo. Buscar `runs/vivo/universo`, correr `python -m simbio mirar runs/vivo/universo` y revisar `docker ps`. Si no está corriendo, arrancarlo (§5) y dejarlo vivo.
4. Preguntarle una sola vez, si no está anotado: si tiene Docker Desktop y **en qué ciudad vive** (para el clima real de la etapa 2; el correo es .com.ar, probablemente Argentina).

### 8.1 Etapa 2: datos reales (clima)
- **Descarga, en un proceso aparte de la simulación** (`experiments/herramientas/descargar_clima.py`, por hacer): serie horaria de años de la ciudad del autor, desde la API de archivo de Open-Meteo, que es libre y no pide clave (`https://archive-api.open-meteo.com/v1/archive`). Variables: temperatura, precipitación, presión, radiación solar y nubosidad. Guardar en `datos/clima/<ciudad>.npz` con sus metadatos. Los organismos nunca tocan la red.
- **En el motor, una sección nueva de configuración** (por ejemplo `realidad.*`, apagada por defecto):
  - archivo de datos y pasos de simulación por hora real (para recorrer años en semanas);
  - un acoplamiento simple y documentado:
    - radiación → recrecimiento de la comida (día y noche reales);
    - temperatura → costo basal o tasa de recrecimiento;
    - lluvia → qué tipo de comida nutre (reemplaza a la estación artificial);
    - presión → un sensor nuevo, local, que anticipa la lluvia: premia anticipar;
  - revisar en `src/simbio/entorno.py` cómo crece el recurso antes de decidir el acoplamiento.
- **Control:** el mismo clima con los días mezclados al azar (mismas cantidades, sin patrones). Si los organismos responden igual, responden a la cantidad, no a la estructura.
- **Verificar antes de corridas largas:** que LUCA sea viable con el acoplamiento, y una competencia que muestre que anticipar (por ejemplo, con un gen armado a mano que lee la presión) se premia.
- **Prerregistro, corrida y evaluación**, como en cualquier fase.

### 8.2 Etapa 3: interfaz para estimular el universo
- **Servidor web local, solo con la biblioteca estándar** para no agregar dependencias: `python -m simbio interfaz runs/vivo/universo`, que se abre en el navegador.
- **Lectura:** muestra el universo en vivo (imagen del mundo, población, gráficos desde `metricas.jsonl`).
- **Escritura de estímulos por archivo:** la interfaz escribe en `<universo>/entradas/` y la simulación los lee en cada paso. Así se respeta `network_mode: none`: la interfaz corre fuera del contenedor y escribe en el volumen compartido.
- **Estímulos:** chat (texto → patrón de señales que recorre el mundo), carga de datos; después audio (espectro → campo sonoro local) y video (imagen reducida → luz que hace crecer comida).
- **Regla clave:** un estímulo que no afecta la supervivencia se ignora. Acoplarlo a algo y medirlo contra un control con el estímulo mezclado o desacoplado.
- **Todo lo que entra se graba** (reproducibilidad).

### 8.3 Etapa 4: depredación evolucionada
Una primitiva nueva (por ejemplo `ATACAR`), con costos físicos y transferencia de energía al atacante, para que el ambiente sean otros organismos (Reina Roja). Control: el depredador fijo de la fase 2c.

### 8.4 Etapa 5: archipiélago
Varios universos (servicios en `docker-compose.yml`) que intercambian migrantes por una carpeta compartida (`migrantes/`): cada uno exporta unos pocos organismos cada tanto e importa los de los otros. Pueden tener físicas distintas. Control: islas aisladas.

### 8.5 Etapa 6 (investigación aparte)
Sustrato tipo *Tierra* dentro del contenedor: organismos como programas en un intérprete propio, nunca código nativo.

## 9. Deudas pendientes (no bloquean, pero hay que saldarlas)
- **OpenSpec:** no hay cambios abiertos ni archivados para las fases 7–12 (el último archivado es `fase-6-memoria`). Abrir uno que documente estaciones, toxicidad, regulación, inducción, cerrojo, modulación, softmax y modo continuo, y validar con `openspec validate --all --strict`.
- **Recomendaciones de la revisión de las fases 9–11 todavía no hechas:**
  - una condición "inducción sin cerrojo", para separar el peldaño de la persistencia física;
  - que la memoria sin gen decaiga hacia 0,5, o que la inducción actúe solo con un gen de memoria activo, para que la digestión de un organismo sin información quede neutra;
  - efectos laterales de la memoria inicial 0,5: la condición 6 anula el receptor y las condiciones 3 y 4 quedan fijas.
- ~~**ODD:** anexo de la fase 12 y relectura del castigo~~ hecho el 2026-10-29.
- **Los scripts de competencias** (`experiments/fase10/*.py`, `experiments/fase11/*.py`) se corren desde la raíz del repo.
- **Métricas viejas:** las fases 7–9 reportan `seguimiento` con el aliasing de muestreo. Sus conclusiones no cambian (valores ~0), pero conviene recordarlo al citarlas.

## 10. Salvaguardas acordadas con el autor (`docs/04-vision.md`)
- **Aislamiento:** el contenedor es la frontera. La simulación corre sin red, los datos externos entran por carpeta en solo lectura, y los organismos nunca tocan internet ni el sistema. "Sin límites", para el autor, significa sin el corral del plano 2D, no sin seguridad.
- **Sin autorreplicación física autónoma** por ahora (condición revisable).
- **ADN o datos personales,** solo con consentimiento informado, almacenamiento local y propósito explícito.
- **Las salvaguardas viven en la física y en las dependencias, no en el genoma** (línea "S" de la hoja de ruta: experimento pendiente sobre cuánto dura una salvaguarda genética frente a una física).
- **Reproducibilidad y apertura:** todo lo que entra se graba.
