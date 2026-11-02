# 2026-11-01 · Fase 14: ¿evolucionan los ojos y hacen que se use el cerebro? (prerregistro)

Escrito antes de correr.

## Por qué
**Decisión del autor (2026-10-31):** la naturaleza es inspiración, no receta. Si un paso se puede saltear, adelante.

**Diagnóstico de las fases 1–13:** el límite para la inteligencia no son los cuerpos. Es que el mundo casi no premia procesar información:
- la memoria nunca evolucionó (fase 9);
- la red interna de 8 unidades no se usa (fase 13);
- cada organismo percibe solo lo que tiene al lado.

En la Tierra, los cerebros despegaron cuando apareció la percepción a distancia: los ojos del Cámbrico (Parker 2003, *In the Blink of an Eye*). Con ella hay algo que anticipar: la comida que está más allá, el que se acerca.

**Atajo:** un cerebro antes que un cuerpo. La red regulatoria de cada organismo, recurrente y con estado, hace de cerebro, y se le da al genoma la posibilidad de tener ojos.

## Física nueva (fidelidad, no premio)
- **Rasgo heredable `alcance`:** cuántas celdas más allá de la de enfrente ve el organismo, entre 0 y 5. LUCA vale 0. Muta sumando un ruido normal (σ = 0,3) con la misma probabilidad que los otros rasgos.
- **Costo:** 0,02 de energía por paso y por celda de alcance; el basal es 0,3. Un ojo de alcance 5 cuesta un tercio del basal. Es del orden de lo que gastan los ojos reales: los fotorreceptores de una mosca usan ~8 % del metabolismo en reposo (Niven y Laughlin 2008). Se fija una vez; no se retoca según los resultados.
- **Sensores nuevos**, en la dirección en que mira:
  - `comida_lejos`: el recurso más rico a la vista;
  - `otro_lejos`: la cercanía del primer organismo a la vista;
  - `tamano_lejos`: el tamaño del grupo de ese organismo relativo al propio, para saber si es presa o depredador.
- Con la visión apagada, el universo no cambia: tests 215 pasan, 1 omitido; huellas iguales a la referencia.

## Diseño
- **Universo:** `natural.toml`, con la red regulatoria y desde LUCA.
- **Condiciones:**
  - **vision:** el genoma puede tener ojos;
  - **cegada:** los ojos existen, mutan y cuestan igual, pero no informan;
  - **ciega:** sin ojos, el mundo de la fase 13.
- **Prueba de lesión**, como en neurociencia:
  - al terminar, la población se copia y sigue 20 000 pasos más, con el mismo azar, en dos versiones: intacta y lesionada;
  - `lesion_cerebro`: los genes dejan de leer la red;
  - `lesion_ojos`: solo en vision; los ojos dejan de informar, pero siguen costando;
  - medida: costo de la lesión = (población intacta − lesionada) / intacta, en el último cuarto de esos 20 000 pasos.
- **Semillas:** 49–58, nuevas. **Pasos:** 300 000. Medición desde el paso 200 000.
- **Ejecución:** Docker (`experiments/fase14/ojos.py`, contenedor `fase14-ojos`). **Salida:** `runs/fase14/ojos.json`.

## Criterios
| | Medida | Cumple si |
|---|---|---|
| **V1, los ojos evolucionan por lo que informan** | `alcance_medio` vision − cegada | > 0, permutación pareada, p ≤ 0,05 |
| **V2, los ojos se usan** | `lesion_ojos` en vision | > 0, permutación de signos, p ≤ 0,05 |
| **V3, con ojos el cerebro pasa a importar** | `lesion_cerebro` vision − ciega | > 0, permutación pareada, p ≤ 0,05 |

**Exploratorias:**
- `lesion_cerebro` en cada condición;
- población, vision − ciega;
- `frac_con_ojos`;
- uso de la red: `peso_regulador_medio`.

## Qué significaría cada resultado
- **V1 y V2:** la percepción a distancia paga y se usa: primer paso del atajo.
- **V3:** el cerebro empieza a importar cuando hay información a distancia para procesar. Es el paso clave hacia la inteligencia, y abre la siguiente pregunta: ¿anticipa?
- **V1 y V2 sin V3:** los ojos se usan como reflejo (ver comida lejos → avanzar) sin necesidad del cerebro. Habría que buscar qué situación real exige recordar o anticipar; por ejemplo, presas que se mueven, que ya existen porque la depredación evoluciona sola.
- **Ninguno:** la visión no paga a ese costo en este mundo. Es un dato; no se baja el costo para que aparezca.

## Resultado de la primera corrida (2026-11-01) y enmienda
Corrida completa: 30 de 30, sin extinciones. Salida guardada en `runs/fase14/ojos_error_copia.json`.

**V1, los ojos evolucionan por lo que informan: no se cumple.**
- `alcance_medio` vision − cegada: 5 de 10 semillas positivas, p = 0,42.
- Los ojos aparecieron de verdad en una sola semilla, la 51: el 60 % de la población tiene alcance ≥ 1 y el alcance medio es 0,73. En las otras nueve, menos del 0,1 % tiene ojos, igual que en cegada.
- Esta medida sale de la serie de la corrida, no de la lesión, así que vale: **la visión no paga a ese costo en este mundo.** Es un dato; el costo no se toca.

**V2 y V3 no valen: error en la prueba de lesión.**
- `lesion()` armaba las dos copias con `copy.deepcopy(sim, memo)` y `copy.deepcopy(sim, dict(memo))`. La segunda copia del memo se hacía *después* de la primera copia, así que ya contenía `sim → intacta`, y deepcopy devolvía la misma copia dos veces.
- La "intacta" era, entonces, la lesionada. El "costo" comparaba dos tramos sucesivos de 20 000 pasos de la misma simulación lesionada. Por eso todos los valores salieron negativos y parecidos (−3 % a −29 %): reflejaban el crecimiento de la población en el tiempo, no la lesión.
- Corrección:
  - cada copia lleva su propio memo, con una aserción de que son objetos distintos;
  - `tests/test_lesion.py`: una lesión nula cuesta exactamente 0; una lesión real cambia la historia; la simulación original no se toca.

**Enmienda:**
- Se vuelven a correr vision y ciega con la lesión corregida: mismas semillas, mismos pasos, mismos criterios. Por el determinismo, las series son idénticas a la primera corrida; solo cambian las lesiones.
- Las corridas de cegada se reutilizan sin su `lesion_cerebro`, que era inválido y es solo exploratorio.
- Salida: `runs/fase14/ojos.json`.
