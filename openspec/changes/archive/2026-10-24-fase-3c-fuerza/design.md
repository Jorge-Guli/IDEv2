# Design

## Context
Ver `proposal.md`, `docs/bitacora/2026-10-24-fase3-evaluacion.md` y `docs/bitacora/2026-10-24-fase3b-evaluacion.md`.

## Decisions

### D1. Probabilidad, no umbral
La velocidad media de un grupo es proporcional a la fuerza neta sobre el arrastre. En una grilla discreta, eso se traduce en una probabilidad de desplazarse por paso. Coordinarse sigue rindiendo: más empujadores alineados significan más velocidad. Pero ya no hay un valle donde cualquier descoordinación inmoviliza al grupo.

### D2. Exponente del arrastre
A bajo número de Reynolds, el arrastre crece con el tamaño lineal: ~n^½ en una colonia plana y ~n^⅓ en una esfera. **α = 0,5 es el valor principal.** α = 1 es una variante de sensibilidad, que castiga más el tamaño. La revisión de la fase 3 advirtió que el exponente decide el resultado, así que ambos van prerregistrados.

### D3. Vectores unitarios
Se corrige la anisotropía señalada por la revisión de la fase 3: en "empuje", un rumbo diagonal aporta √2. "empuje" se deja como estaba, para no alterar los resultados anteriores.

### D4. Lo que se puede afirmar
El efecto de la física se mide con `fuerza_base` contra `empuje_base`. El de la información, con `fuerza_ambos` contra `fuerza_barajado`. La interacción es la diferencia de diferencias contra "empuje". Si los grupos crecen solo por la física, no se afirma que la coordinación haya emergido.

## Risks / Trade-offs
- [Elegir la física hasta obtener el resultado] → decisión justificada por 3 y 3b, prerregistrada, con semillas nuevas, sin ajustar con ellas, y con un piloto de una sola semilla (301).
- [Con fuerza, un solo miembro mueve a un grupo grande con alguna probabilidad] → la coordinación compra velocidad, no eficiencia por celda recorrida; se mide la alineación y el éxito del empuje.
