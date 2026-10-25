# 2026-10-25 · Fase 7, exploración: un mundo que exija memoria

Exploración (no prerregistrada). Mundo base desde LUCA, semillas 701 y 702, 50 000 pasos (~200–600 generaciones). Script de análisis en la bitácora de la fase 7.

## El mundo (`estaciones.*`, con tests)
- Dos tipos de comida en parches (A y B), y un sensor del tipo de comida de la celda propia.
- Una **estación oculta**, que se alterna cada 2000 pasos, decide cuál tipo nutre; el otro es tóxico.
- Una **pista** de la estación, que cada organismo percibe con probabilidad 0,01 por paso.

## Tres versiones, tres lecciones
| Versión | Acierto al comer (LUCA: 0,45) | ¿Se usa la memoria? | Por qué |
|---|---|---|---|
| 1. Toxicidad inmediata, con aprendizaje | 0,82–0,87, **también sin memoria** | No (seguimiento ≈ 0) | El **aprendizaje en vida** resuelve la tarea: comer tóxico da recompensa negativa y la conducta se reajusta en menos de 500 pasos |
| 2. Toxicidad inmediata, sin aprendizaje | 0,85–0,88, también sin memoria | No | **Probar y retirarse:** el sensor de ΔE avisa en el paso siguiente que la comida era mala. Es un "recuerdo" de un paso que alcanza |
| 3. Toxicidad diferida (energía ahora, veneno después) | 0,74–0,77, con memoria y sin ella | No | La **selección espacial** (los que están en parches malos mueren envenenados) da ~75 % sin recordar. Usar la memoria pide una regla no lineal (comer A si la memoria dice A, y B si dice B), que el genoma solo arma combinando varios genes |

## Lectura
- La cognición sí apareció, pero tomó el camino más barato disponible: la plasticidad en vida y un recuerdo de un paso, antes que una memoria persistente. Tiene sentido biológico: la memoria de largo plazo es cara de construir y se usa cuando las alternativas fallan.
- Para que la memoria persistente rinda, el mundo tiene que bloquear los atajos: sin aviso inmediato, sin aprendizaje que reajuste, y con un patrón que solo se conoce por una pista pasada. La versión 3 lo hace. Lo que falta es tiempo evolutivo para descubrir la regla no lineal, y un control (pista aleatoria) para separar el beneficio de recordar de cualquier otro efecto.

## Decisión
Prueba larga en el equipo local (200 000 pasos, ~1000–2000 generaciones), prerregistrada: [`2026-10-25-fase7-prerregistro.md`](2026-10-25-fase7-prerregistro.md).
