# Design

## Context
La primera extinción causada por el equipo mostró que la población no tiene ninguna salida ante una caída de la comida: estar vivo cuesta lo mismo haga lo que haga el organismo. La propuesta cambia esa ley, sin regalar comportamientos.

## Goals / Non-Goals
**Goals:**
- Que el gasto de estar vivo dependa de la actividad, como en una PC y en la naturaleza.
- Medir si, con esa ley, evoluciona el letargo ante la escasez, y si aparecen crías que nacen aquietadas (semillas).

**Non-Goals:**
- No hay primitiva "dormir" ni "esporular": se usa la que ya existe, `descansar`.
- No hay sensor nuevo: para despertar, el organismo usa lo que ya percibe (comida local, energía propia, socios).
- No hay reciclaje de cadáveres: un muerto de hambre no tiene energía para devolver (ver la propuesta).

## Decisions
- **Actividad con inercia, no instantánea.** Si una sola acción de descansar bajara el gasto al piso, alternar descansar y comer sería gratis. Con inercia (0,05: ~20 pasos para bajar a la mitad), aquietarse rinde solo si se sostiene. Lo mismo vale en la realidad: entrar en letargo lleva tiempo.
- **Piso = 0,1.** El metabolismo de reposo de los animales en torpor baja a entre el 1 % y el 25 % del basal; un proceso en pausa en una PC usa cerca de 0 % de CPU, pero sigue ocupando memoria. Se fija 0,1 antes de correr y no se ajusta según el resultado.
- **El costo por gen no baja.** Es el análogo de la memoria que ocupa un programa en pausa. Así un genoma grande sigue costando aunque duerma.
- **La cría hereda la actividad.** Es lo que hace posible una semilla sin diseñarla: un progenitor quieto que se divide tiene crías quietas. Para dividirse hay que gastar `costo_division`, así que una semilla cuesta.
- **Serie del equipo a escala real.** El universo natural corre a ~50 pasos/s y el lector toma una muestra cada 10 s: 500 pasos por muestra. Cada semilla arranca en un punto distinto de la serie, elegido por su generador, y la serie se repite en ciclo si se termina.

## Risks / Trade-offs
- **Reposo reflejo o adaptación.** Si no hay comida, cualquier organismo "descansa" más por reflejo y el gasto baja solo. Para distinguirlo de una adaptación, se compara contra el mismo metabolismo con el promedio quieto y con la serie barajada, y entre el primer y el último tercio de cada corrida.
- **Pocas caídas grabadas.** Al 2026-11-02 hay una sola caída fuerte (< 0,2). El experimento no corre hasta tener al menos 3 días de registro y al menos 3 caídas por debajo de 0,2; si no las hay, se informa sin correr.
- **Población más grande.** Descansar más barato puede subir la población en todos los mundos. Por eso los criterios comparan siempre dentro de la misma física.

## Experimento (prerregistro resumido; el completo va en la bitácora antes de correr)
Condiciones: A = física actual + serie real; B = metabolismo + serie real; C = metabolismo + promedio quieto; D = metabolismo + serie barajada. Configuración: `natural.toml`; 6 semillas; 1 000 000 pasos. Estimado: ~17 h con 4 procesos en Docker.
- **C1 Supervivencia:** con la serie real, B sobrevive más que A. Pasos hasta la extinción, o el total si no se extingue; Mann–Whitney de una cola, p < 0,05.
- **C2 Letargo ante la escasez:** en B, la actividad media en los pasos con cpu_libre < 0,3 es al menos 0,1 menor que con cpu_libre ≥ 0,6, en al menos 5 de 6 semillas.
- **C3 Adaptación y no reflejo:** en B, esa diferencia es mayor en el último tercio que en el primero; Wilcoxon pareado de una cola, p < 0,05.
- **Exploratorio:** fracción de nacimientos quietos (semillas) en B frente a C y D.
