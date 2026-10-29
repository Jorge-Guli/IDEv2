# Traspaso: estado del proyecto y cómo seguir

Escrito el 2026-10-27 para que una nueva sesión de Claude (por ejemplo, Claude Desktop en el equipo del autor) retome el trabajo sin perder contexto. **Leer primero este documento**; después, según haga falta, `CLAUDE.md`, `docs/02-hoja-de-ruta.md` y `docs/06-universo-vivo.md`.

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
- **Su equipo:** Windows, carpeta `C:\Desarrollo\IDEv2`, entorno virtual `.venv` (PowerShell: `.\.venv\Scripts\Activate.ps1`), 8 procesos para corridas paralelas (`--procesos 8`). Hasta ahora corría las corridas largas a mano y avisaba "resultados subidos". **Con Claude Desktop, Claude puede correrlas directamente en su equipo.**
- **Docker Desktop:** consultar si está instalado antes de usar `docker compose`.

## 3. Reglas del proyecto (de `CLAUDE.md`, no negociables)
- **Idioma:** documentación, specs, comentarios y nombres del dominio en español. SHALL y MUST de OpenSpec en inglés.
- **La física (primitivas y costos) es fija e igual para todos; qué acciones tiene y usa cada organismo sale de su genoma.**
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
python -m pytest -q                       # 160 pasan; 3 se omiten sin GPU NVIDIA con CuPy
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
| 12, etapa 3 | **Estímulos desde afuera** (luz y texto) por la carpeta `entradas/`, grabados en `estimulos.jsonl`. Claude le habla al universo `clima`. Piloto: indicio de que la selección mira la luz si alimenta (3/4); prerregistro v1 inválido por extinciones en invierno; v2 en curso |
| 12, etapa 4 | **Depredación evolucionada** (`atacar`): evoluciona sola desde LUCA, pero **negativo prerregistrado**: 5/8 extinciones, monocultivos caníbales, sin más mutación ni diversidad. Próximo: especialización trófica |

### Lecciones que guían el diseño
1. **El mundo tiene que premiar un rasgo antes de esperar que evolucione.** Se verifica con competencias o invasión (hay scripts en `experiments/fase7`, `fase10` y `fase11`).
2. **La evolución toma atajos:** aprender en vida, selección espacial, "recordar" lo que tiene debajo. Cada mundo nuevo se audita y los atajos se bloquean con física, verificando con duelos directos.
3. **Una población sola engaña:** varias semillas, jardín común y modelos nulos.
4. **Cada peldaño de una innovación necesita premio propio** (Lenski et al. 2003, Avida: ver `docs/05-estado-del-arte.md`).
5. **En un mundo fijo, la evolución se estanca y baja su propia tasa de mutación.** Es el argumento científico del universo vivo.
6. **Errores típicos de diseño a mano:** genes de prueba que "comen" en celdas vacías por falta de sesgo, o que paralizan al organismo. Diagnosticar siempre las acciones por cepa antes de concluir.
7. **Métricas:** cuidado con el aliasing de muestreo. El seguimiento de la memoria tenía un máximo práctico de 0,5 por medir cada 500 pasos con estaciones de 2000. Los scripts reportan ahora `seguimiento_corregido`.

## 7. Estado actual del motor (opciones relevantes; todas en `src/simbio/config.py`)
- **Estaciones** (`estaciones.*`): tipos de comida en parches o mosaico, estación oculta, pista, toxicidad inmediata o diferida, rampa de toxicidad, rampa de la pista, digestión inducible con inercia.
- **Memoria** (`memoria.*`): dos variables, tasa, cerrojo (`umbral`) y valor inicial.
- **Herencia** (`herencia.*`): condición de expresión por gen (`k_condicion`) y modulación (`modulacion`, condiciones 5 y 6 sobre `genoma.SENS_MODULABLES`).
- **Decisión** (`fisica.decision`): "argmax" o "softmax", con `temperatura`.
- **Realidad** (`realidad.*`, `src/simbio/realidad.py`): clima horario (radiación → recrecimiento, temperatura → costo basal, lluvia → qué comida nutre, sensor de presión); controles `barajar_dias` y `presion_desacoplada`. Datos en `datos/clima/` (los baja `experiments/herramientas/descargar_clima.py`).
- **Estímulos** (`estimulos.*`, `src/simbio/estimulos.py`): campo de luz que alimenta y se percibe con el sensor `luz`; texto como secuencia de pulsos; `python -m simbio estimular <universo> --texto "..."`.
- **Ataque** (`ataque.*`): primitiva `atacar`, protección por enlaces, especialización trófica (`especializacion_gamma`, junto con `fisica.maquinaria_gamma`).
- **Neutralidad:** los sensores (`presion`, `luz`) y la primitiva nuevos van al final; en mundos sin ellos no mutan ni consumen azar (`gen.NUM_SENS_SIN_REALIDAD`, `gen.NUM_PRIM_SIN_ATAQUE`). Las huellas siguen idénticas.
- **Docker:** dos servicios, `universo` (vivo.toml) y `clima` (clima.toml + estímulos; `./datos` en solo lectura).
- **Universo vivo:** `src/simbio/continuo.py` (`vivir`, `mirar`, guardado con pickle portable entre CPU y GPU, volcado incremental de métricas y linaje, resiembra tras una extinción) y `experiments/configs/vivo.toml` (el mundo de la fase 11 desde LUCA puro).

## 8. Pasos a seguir (en orden)
El diseño completo está en `docs/06-universo-vivo.md`. Resumen operativo:

### Estado al 2026-10-27 (tarde)
- **Hecho:** 8.0; las etapas 2 y 3 construidas; la etapa 4 construida y con su primer prerregistro (negativo). Detalle en `docs/bitacora/2026-10-27-fase12-*.md`.
- **El autor vive en Capitán Bermúdez (Santa Fe)** y tiene Docker Desktop. Pidió que Claude alimente el universo e interactúe con él directamente.
- **Pendiente:**
  1. ~~evaluar la luz v2~~: hecho el 2026-10-28. La serie de la luz (v2 a v5) es negativa: ver `docs/bitacora/2026-10-28-fase12-luz-anticipa-prerregistro.md`;
  2. ~~especialización trófica~~: corregida (atacar creaba energía) y sin nichos. Ver la evaluación de la Reina Roja;
  3. un mundo donde anticipar pague (daño al empezar la lluvia, o respuesta lenta). La luz mostró que hace falta una señal duradera o aprendizaje en vida;
  4. ~~archipiélago~~: hecho, negativo en adaptación y variación; la migración solo evita extinciones (3/24 contra 8/24 islas). Ver `docs/bitacora/2026-10-28-fase12-archipielago-prerregistro.md`;
  - **Siguiente: el mundo del texto.** El texto real pasa letra por letra y quien anticipa la próxima letra consigue comida. Premia la memoria y la predicción, y ofrece patrones sin fin.
    - Primero se calibra con un texto de dominio público.
    - Después se corre con "La última pregunta" y "La última respuesta" de Asimov, elegidas por el autor por su simbolismo. Están en `datos/textos/`, con copia propia del autor e ignoradas por Git: **nunca subirlas ni copiar su contenido**. En la bitácora solo van su sha256 (`5a985d7c…` y `d6548766…`) y su tamaño.
  5. el ODD, la hoja de ruta y el cambio de OpenSpec de la fase 12.
- **Equipo:** corridas con 6 procesos como máximo, en prioridad Idle; contenedores con `cpus: 0.5`.

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
- **ODD:** agregar el anexo de la fase 12 (modo continuo; después, los datos reales).
- **Los scripts de competencias** (`experiments/fase10/*.py`, `experiments/fase11/*.py`) se corren desde la raíz del repo.
- **Métricas viejas:** las fases 7–9 reportan `seguimiento` con el aliasing de muestreo. Sus conclusiones no cambian (valores ~0), pero conviene recordarlo al citarlas.

## 10. Salvaguardas acordadas con el autor (`docs/04-vision.md`)
- **Aislamiento:** el contenedor es la frontera. La simulación corre sin red, los datos externos entran por carpeta en solo lectura, y los organismos nunca tocan internet ni el sistema. "Sin límites", para el autor, significa sin el corral del plano 2D, no sin seguridad.
- **Sin autorreplicación física autónoma** por ahora (condición revisable).
- **ADN o datos personales,** solo con consentimiento informado, almacenamiento local y propósito explícito.
- **Las salvaguardas viven en la física y en las dependencias, no en el genoma** (línea "S" de la hoja de ruta: experimento pendiente sobre cuánto dura una salvaguarda genética frente a una física).
- **Reproducibilidad y apertura:** todo lo que entra se graba.
