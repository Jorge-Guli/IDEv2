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
