# 2026-11-01 · El universo de LUCA es digital: se quita el clima real

**Decisión del autor:** "el clima de mi ciudad es algo del mundo físico, no del mundo digital donde habita LUCA. Desde la primera vez que lo sumaste me generó ruido."

**Qué se hizo:**
- **Sin clima.** `natural.toml` ya no tiene `[realidad]`: la comida recrece a ritmo constante. Las presiones y la variación salen de la propia población: escasez, competencia y depredación que evoluciona.
- **Universo reiniciado desde LUCA** (contenedor `idev2-natural-1`, datos en `runs/vivo/natural`).
- **La versión con clima queda como dato histórico** en `runs/vivo/natural_clima`: unos 4,04 millones de pasos, del 2026-10-31 al 2026-11-01, población final de unos 1 400 organismos.
- **Principio 7 reescrito** (CLAUDE.md y `docs/01-metodologia.md`): mundo digital con física propia, nada traído de la Tierra. Su "mundo físico" es el equipo donde corre.
- Tests: 217 pasan, 1 omitido.

**Siguiente, a partir de la propuesta del autor:** que el estado del propio equipo alimente al universo, como su verdadero entorno físico: carga, energía, temperatura y la actividad del autor, incluidas las sesiones de chat, con su permiso. Diseño en curso, con estas condiciones:
- **Determinismo:** todo lo que entra se graba, para poder reproducir cualquier tramo.
- **Privacidad:** de las sesiones se toman solo ritmos (cuándo y cuánto), nunca el contenido.

## El equipo como mundo físico de LUCA (hecho el mismo día)
El autor: "el universo de LUCA es un contenedor dentro de mi equipo físico; este equipo es un universo en sí mismo". Dio permiso para usar también la actividad de las sesiones de chat.

**Una sola conexión, la más literal:** la comida recrece en proporción a la CPU libre del equipo (`regeneracion · cpu_libre`, `EquipoCfg`). Cuando la computadora está ocupada, al mundo de LUCA le llega menos energía; eso incluye nuestros propios experimentos. No hay otra elección de diseño: ni umbrales, ni premios.

**Lector del equipo** (`experiments/herramientas/lector_equipo.py`):
- corre afuera del contenedor, con prioridad mínima, y toma una muestra cada 10 segundos;
- escribe en `datos/equipo/` (no se sube al repositorio) la CPU libre, la memoria libre y el ritmo de las sesiones de Claude Code;
- de las sesiones mira solo cuántos bytes crecieron sus registros y cuántos cambiaron. **Nunca abre su contenido.** El ritmo queda registrado para estudiarlo, pero hoy no alimenta al universo.

**Determinismo:**
- el universo lee la última muestra cada 1 000 pasos y graba el valor aplicado en `runs/vivo/natural/equipo.jsonl`, así que con ese registro cualquier tramo se puede volver a correr;
- si la muestra tiene más de 10 minutos, no se aplica y queda la anterior;
- los experimentos con semilla no usan el equipo, porque su opción está apagada por defecto. Huellas iguales a la referencia; tests: 220 pasan, 1 omitido.

**Universo reiniciado desde LUCA** con el equipo conectado. Primeras lecturas: CPU libre entre 0,81 y 0,88.

**El lector corre en Docker** (servicio `lector`), a pregunta del autor. Arranca solo con Docker, sin tocar el inicio de Windows, sin internet y con 0,1 CPU. Lee las sesiones montadas en solo lectura, y únicamente sus tamaños.
- **Consecuencia:** la CPU y la memoria que ve son las de la máquina de Docker Desktop, no las de todo Windows. Es el barrio inmediato de LUCA: los otros contenedores y nuestros experimentos.
- Primeras lecturas: CPU libre 0,95; memoria libre 0,92.
