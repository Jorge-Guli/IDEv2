# 2026-10-25 · Fase 5, exploración: ¿retornos crecientes y energía compartida producen división del trabajo?

Exploración (no prerregistrada). Pilotos de una semilla (501) y 30 000 pasos (~220–260 generaciones), desde la población evolucionada con fuerza (α = 0,5) y rumbo (piloto de la fase 3c), con refugio 3 y mutación activa.

**Métrica:** índice de rol = (uso de comer − uso de avanzar) / (suma), con el uso medido como promedio móvil. Se reporta su desvío dentro de los grupos de 3 o más (media por grupo) y en toda la población. Es un piloto: orienta, no prueba.

## Física agregada (con todo apagado, la dinámica no cambia; verificado)
- **Maquinaria por uso** (`fisica.maquinaria_gamma`): la eficiencia de comer y de avanzar es (uso reciente / 0,35)^γ, con tope en 2,5.
  - **Primera versión:** la eficiencia multiplicaba la toma máxima. **No tenía efecto:** el 96 % de las veces la toma estaba limitada por el recurso de la celda, no por la toma máxima.
  - **Segunda versión:** multiplica el **rendimiento** (energía por unidad de recurso) y el peso del empuje.
- **Puentes citoplasmáticos** (`asociacion.difusion_energia` = κ): la energía se difunde por los enlaces y se conserva.
- **Recompensa compartida** (`asociacion.difusion_aprende`): la energía recibida por los puentes cuenta para el aprendizaje.

## Resultados (último cuarto)
| Condición | Población | Grupos ≥ 3 | Desvío de roles en grupos | Desvío de roles en la población |
|---|---|---|---|---|
| sin nada (γ = 0, κ = 0) | 1004 | 0,42 | 0,119 | 0,137 |
| κ = 0,2 | 1009 | 0,45 | 0,129 | 0,151 |
| κ = 0,5 | 1011 | 0,45 | 0,148 | 0,161 |
| γ = 2 (rendimiento) | 3146 | 0,43 | 0,121 | 0,189 |
| γ = 2, κ = 0,2 | 2707 | 0,00 | — | 0,145 |
| γ = 2, κ = 0,5 | 3019 | 0,43 | 0,153 | 0,227 |
| κ = 0,5, recompensa compartida | 1018 | 0,43 | 0,142 | 0,157 |
| γ = 2, κ = 0,5, recompensa compartida | 2883 | 0,20 | 0,122 | 0,148 |

- **No hay roles diferenciados en ninguna combinación.** La distribución del índice de rol tiene un solo pico. Con γ = 2, toda la población se corre hacia comer (el uso de comer sube de 0,37 a 0,55) y la población se triplica, porque la comida rinde más.
- La dispersión en la población aumenta con γ, pero por corrimiento y dispersión general, no por roles: dentro de los grupos casi no cambia.

## Lectura
1. **Conflicto entre niveles.** El aprendizaje de cada organismo se guía por su propia ganancia de energía. Comer le da energía al que come; empujar beneficia al grupo y al que empuja solo le cuesta. La plasticidad individual empuja a todos hacia comer. Que la energía compartida cuente para el aprendizaje no alcanzó a cambiarlo en este piloto.
2. **El genoma no tiene cómo sostener tipos celulares.** Los miembros de un grupo son clones con las mismas reglas y entradas parecidas, y el organismo es reactivo: no tiene un estado interno estable salvo los ajustes del aprendizaje. En biología, la diferenciación se apoya en redes de regulación con estados biestables (memoria epigenética). El canal de señales con su señal propia podría servir como un estado de un paso, pero nunca se usó.
3. **El tiempo es corto:** ~250 generaciones por corrida. En la evolución experimental de la multicelularidad, la diferenciación aparece después de miles de generaciones.

## Decisión
No se prerregistra una evaluación de esta física tal cual: los pilotos no muestran ninguna señal y el diagnóstico apunta a límites del modelo, no a falta de semillas. Opciones para seguir, en orden:
- **(a) Paso C de la hoja de ruta: genoma más expresivo,** con un estado interno persistente que el genoma pueda leer y escribir (memoria epigenética, posible biestabilidad) y que se herede al dividirse, con la opción de división asimétrica.
- **(b) Paso D: escala,** con corridas de cientos de miles de pasos en el equipo local.
- **(c)** Revisar la tarea: que empujar tenga un retorno propio para quien empuja (por ejemplo, comida al frente), para atenuar el conflicto entre niveles.
