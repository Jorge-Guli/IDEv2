# Guía del proyecto para agentes

Proyecto de investigación en vida artificial: organismos simples que se adaptan y se asocian, para estudiar si evolución tras evolución emergen organizaciones más complejas e inteligencia. Leer primero `docs/00-hipotesis-fundacional.md` y `docs/01-metodologia.md`.

## Idioma
Documentación, specs, comentarios y nombres del dominio en **español**. Los encabezados estructurales y las palabras SHALL/MUST de OpenSpec van en inglés.

## Flujo de trabajo
- Cada fase es un cambio de OpenSpec (`openspec/changes/<fase>/`): proposal → specs → design → tasks → implementación → experimentos → revisión → `openspec archive`.
- Los criterios de éxito de una fase son numéricos y se verifican con un script en `experiments/<fase>/`.
- Los experimentos se registran en `docs/bitacora/`. El modelo vigente se describe en `docs/odd/modelo.md` (protocolo ODD), que se actualiza al cerrar cada fase.
- Subagentes del proyecto: `experimentador` (corre y registra experimentos) y `revisor-cientifico` (revisión escéptica antes de cerrar una fase).

## Principios que no se negocian
- La física (primitivas y costos) es fija; **qué acciones tiene y usa cada organismo sale de su genoma**.
- Nada de LLMs ni modelos preentrenados dentro de los organismos.
- Percepción solo local.
- Toda afirmación se compara con un control y varias semillas.
- Determinismo: misma configuración y misma semilla dan el mismo resultado. Toda la aleatoriedad pasa por los generadores de la simulación.

## Comandos
- Tests: `python -m pytest -q`
- Corrida: `python -m simbio correr experiments/configs/base.toml --salida runs/x --semilla 1 --pasos 20000 [--set seccion.clave=valor]`
- Competencia: `python -m simbio competir luca runs/x/poblacion.npz experiments/configs/base.toml --pasos 3000`
- Evaluación de la fase 1: `python experiments/fase1/evaluar.py --salida runs/fase1`
- Validar specs: `openspec validate --all --strict`
