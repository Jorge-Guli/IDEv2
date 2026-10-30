# Guía del proyecto para agentes

Proyecto de investigación en vida artificial (IDE: Inteligencia Distribuida Emergente; simulador `simbio`): organismos simples que se adaptan y se asocian, para estudiar si evolución tras evolución emergen organizaciones más complejas e inteligencia. **Para retomar el trabajo, leer primero `docs/07-traspaso.md`** (estado actual, cómo trabaja el autor y próximos pasos). Fundamentos: `docs/00-hipotesis-fundacional.md` y `docs/01-metodologia.md`.

## Idioma
**Responder al autor siempre en español**: no entiende inglés. Esto incluye resúmenes, preguntas, botones y avisos intermedios.
Documentación, specs, comentarios y nombres del dominio en **español**. Los encabezados estructurales y las palabras SHALL/MUST de OpenSpec van en inglés.

## Flujo de trabajo
- Cada fase es un cambio de OpenSpec (`openspec/changes/<fase>/`): proposal → specs → design → tasks → implementación → experimentos → revisión → `openspec archive`.
- Los criterios de éxito de una fase son numéricos y se verifican con un script en `experiments/<fase>/`.
- Los experimentos se registran en `docs/bitacora/`. El modelo vigente se describe en `docs/odd/modelo.md` (protocolo ODD), que se actualiza al cerrar cada fase.
- Subagentes del proyecto: `experimentador` (corre y registra experimentos) y `revisor-cientifico` (revisión escéptica antes de cerrar una fase).

## Principios que no se negocian
- La física (primitivas y costos) es fija; **qué acciones tiene y usa cada organismo sale de su genoma**.
- **El universo no se acomoda al organismo.** Solo se modifica para que sea más fiel a la realidad del autor (clima, cambio climático, El Niño, gravedad, espacio en 3D, sus propias acciones), nunca para facilitar un resultado buscado. Una extinción es un dato, no algo que corregir. Lo que se amplía es qué permite el genoma. **Nada de fuerzas diseñadas:** ni depredador externo, ni estaciones o toxicidad artificiales, ni premios para un rasgo. Las presiones surgen de la propia población (escasez, competencia, depredación que evoluciona con `atacar`) o del mundo real. Ver principio 7 de `docs/01-metodologia.md`.
- Nada de LLMs ni modelos preentrenados dentro de los organismos.
- Percepción solo local.
- Toda afirmación se compara con un control y varias semillas.
- Determinismo: misma configuración y misma semilla dan el mismo resultado. Toda la aleatoriedad pasa por los generadores de la simulación, que viven en CPU.
- Portabilidad: el código no puede depender de un hardware particular. Se usa `xp` (NumPy o CuPy, según `simbio/dispositivo.py`) para operar sobre arreglos, nunca `np.` directamente en la simulación, y todo azar se genera con el `rng` de CPU y se copia con `xp.asarray`. Ver `docs/dispositivos.md`.

## Comandos
- Tests: `python -m pytest -q`
- Corrida: `python -m simbio correr experiments/configs/base.toml --salida runs/x --semilla 1 --pasos 20000 [--set seccion.clave=valor]`
- Competencia: `python -m simbio competir luca runs/x/poblacion.npz experiments/configs/base.toml --pasos 3000`
- Evaluación de la fase 1: `python experiments/fase1/evaluar.py --salida runs/fase1`
- Validar specs: `openspec validate --all --strict`
- Dispositivo: `python -m simbio dispositivo`
- Universo continuo: `python -m simbio vivir experiments/configs/vivo.toml --salida runs/vivo/universo` y `python -m simbio mirar runs/vivo/universo` (o `docker compose up -d --build`)
- Huellas de determinismo: `python experiments/herramientas/huellas.py --comparar`
