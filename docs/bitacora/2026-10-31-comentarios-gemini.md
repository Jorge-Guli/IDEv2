# 2026-10-31 · Comentarios de Gemini sobre el código (fase 13)

El autor compartió una revisión de Gemini. Cada punto se verificó contra el código.

| Punto | Veredicto | Qué se hizo |
|---|---|---|
| **1. Ataques dentro del cuerpo con la masa del cuerpo detrás** | **No se sostiene.** Dentro de un cuerpo, r = N/N = 1 y el daño es 0,5: el mismo que daría su arreglo (1 contra 1). Atacar hacia afuera a una célula suelta rinde más (r = N), no menos. El 16–45 % de ataques internos se explica porque los vecinos de una célula son casi siempre hermanas. El control `sin_intra` ya mostró que los cuerpos no dependen del canibalismo interno. | Nada. |
| **2. Aprendizaje en vida activo en `natural.toml`** | **Cierto, pero no es una fuerza diseñada:** es una capacidad del organismo, con tasa `eta` heredable, que la evolución puede llevar a 0. Sí es razonable preguntar si el refuerzo de la energía propia frena los roles del soma. Es cierto también que `aprender` toca los pesos de sensores y no los `v` de la red. | `eta_media` se agrega como exploratoria en el piloto germinal. Si G1 da nulo, el control sin aprendizaje es candidato. |
| **3. Sin acoplamiento metabólico entre células unidas** | **Cierto,** y ya estaba previsto como el siguiente candidato si la línea germinal da nula: puentes citoplasmáticos regulados por el genoma (como en *Volvox*). | Sin cambios hasta ver el resultado. |
| **4. Potencia con 6 semillas** | **Cierto:** una semilla ruidosa deja p en 0,078. | El piloto germinal se amplía a 10 semillas, antes de ver resultados (enmienda del prerregistro). |
| **README desactualizado** | Cierto. | Actualizado: principio 7, `natural.toml` y fase 13. |
| **Universos con física vieja** | Cierto: `vivo.toml` y `clima.toml` tienen depredador externo, estaciones y la lluvia decidiendo qué nutre. | Retirados (perfil `historico`, sus datos se conservan). Arrancó el universo natural continuo (`idev2-natural-1`, medio núcleo, sin resembrar). |
| **Reglas en `.agent/rules/`** | No hace falta: el principio 7 ya está en `CLAUDE.md`, que lee toda sesión, y en la memoria. | Nada. |
