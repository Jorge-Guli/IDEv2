# 2026-10-25 · Fase 4b: jardín común, resultados

Prerregistro: [`2026-10-25-fase4b-prerregistro.md`](2026-10-25-fase4b-prerregistro.md). Corrido en el equipo local (13 minutos). Informe: [`2026-10-25-fase4b-informe.json`](2026-10-25-fase4b-informe.json).

Las poblaciones evolucionadas en la fase 4a corrieron sin mutación en dos ambientes comunes. Medias de 10 semillas; las métricas de especialización, sobre 8 semillas (en 2 no hay grupos en alguna de las condiciones comparadas).

| Genomas evolucionados con… | Ambiente | Grupos ≥ 3 | Nunca se dividió | Nunca se dividió (borde) | Correlación | Población |
|---|---|---|---|---|---|---|
| sin | sin restricción | 0,27 | 0,10 | 0,14 | −0,27 | 690 |
| r20a (control) | sin restricción | 0,28 | 0,09 | 0,13 | −0,32 | 687 |
| **r20** | sin restricción | **0,58** | **0,17** | **0,35** | −0,22 | **749** |
| sin | con r20 | 0,36 | 0,11 | 0,21 | −0,59 | 550 |
| r20a (control) | con r20 | 0,35 | 0,08 | 0,14 | −0,58 | 571 |
| **r20** | con r20 | **0,59** | **0,17** | **0,38** | −0,43 | **659** |

## Hipótesis (genomas r20 contra sin y contra r20a, en cada ambiente)
| # | Resultado | Veredicto |
|---|---|---|
| G1: la correlación más negativa es heredada | No: es igual o menos negativa (p = 0,94–1,0) | ❌ (lo esperado: era mecánica) |
| **G2: más miembros que nunca se dividen** | 0,17 contra 0,08–0,11; **p = 0,004–0,016**, 4/4 comparaciones | ✅ |
| **G3: ídem entre los de borde** | 0,35–0,38 contra 0,13–0,21; **p = 0,004–0,008**, 4/4 | ✅ |
| **G4: más grupos de 3 o más** | 0,58 contra 0,27–0,36; **p = 0,002–0,009**, 4/4 | ✅ |

## Lo que muestran los datos
1. **La evolución bajo la restricción flagelar dejó dos cambios heredables**, que se ven aunque la restricción no esté:
   - una tendencia mucho mayor a formar grupos de 3 o más (el doble);
   - el doble de miembros que no se reproducen.
   
   Las poblaciones con esos genomas son además más grandes: 749 contra 690 en el ambiente sin restricción, y 659 contra 550–571 con ella.
2. **La correlación negativa de la fase 4a era mecánica:** en el jardín común, los genomas r20 no la muestran más que los otros.
3. El control r20a (la misma inmovilidad, al azar) no produce nada de esto: lo que seleccionó estos cambios es que la inmovilidad estuviera **ligada a reproducirse**.

## Revisión científica
Revisión independiente (subagente `revisor-cientifico`), con verificaciones ejecutadas:
- **Implementación correcta y determinista.** El control aleatorio no tiene efectos colaterales que sesguen. Su ocupación refractaria no es idéntica: en la 4a fue algo mayor en r20a (0,32 contra 0,28) en 8 de 10 semillas, un sesgo conservador para G4.
- **"Nunca se dividió" es una métrica de hojas.** Los enlaces nacen casi solo de dividirse unido, así que quien nunca se dividió tiene, por construcción, un solo socio: `nunca_dividio_interior` vale 0 en las 60 corridas. **G3 no controla la posición**, y G2 y G3 no son evidencia independiente. La frase "G3 reduce el efecto de la posición" era errónea.
- **Prueba de sobredispersión, a favor de la conclusión, pero con una sola población evolucionada** (piloto 401):
  - modelo nulo: reparto de las divisiones de cada grupo con tasa igual para todos (pesos por edad), a igual tamaño de grupo;
  - genomas sin y r20a: coinciden con el nulo; genomas r20: 1,5 a 2 veces más miembros sin dividirse que el nulo;
  - no es espacio ni energía: quienes nunca se dividieron tenían celdas libres y energía, pero ~50 % nunca intentó dividirse;
  - en toda la vida, el 30–33 % de los miembros de grupos con genomas r20 mueren sin haberse dividido, contra el 9–11 % con sin y r20a.
- **No hay complementariedad funcional:** quienes no se reproducen no empujan más (tasa de avanzar 0,285 contra 0,271). Es **supresión reproductiva dependiente del contexto**, no división del trabajo.
- **El control r20a no aísla "ligada a la inmovilidad".** En r20, dividirse tiene un costo privado para quien se divide; en r20a, el costo se reparte. Hace falta un control con un costo privado equivalente sin inmovilidad.
- **Estadística:** con 8 semillas, p = 0,0039 es el mínimo posible (las 8 con el mismo signo). Las 4 comparaciones comparten poblaciones: la evidencia equivale a "8 de 8 semillas", no a 4 réplicas independientes.
- **G4 no replica el hallazgo de la 4a:** usa las mismas poblaciones donde se descubrió. Hacen falta semillas nuevas.

## Lo que se afirma
- La evolución bajo la restricción flagelar, frente al control aleatorio, dejó **cambios heredables**:
  - más tendencia a formar grupos de 3 o más;
  - menor propensión a dividirse;
  - en una población analizada con modelo nulo, **un sesgo reproductivo dentro de los grupos**: miembros que no se dividen aunque tienen espacio y energía, más de lo que daría el azar con tasas iguales.
- La correlación negativa de la 4a era mecánica.

## Lo que todavía no se puede afirmar
- **"División del trabajo" o "miembros somáticos":** los no reproductores no hacen otra cosa útil para el grupo.
- **Que la clave sea la ligadura con la inmovilidad** y no cualquier costo privado de reproducirse.
- **Que el sesgo reproductivo sea general:** el análisis con modelo nulo cubre una sola población.
- **Que exista dependencia:** no se midió si los miembros no reproductores sobreviven solos.

## Decisión
Fase 4c ([prerregistro](2026-10-25-fase4c-prerregistro.md)):
- el análisis con modelo nulo sobre las 10 poblaciones de la 4a;
- un control de costo privado de dividirse sin inmovilidad;
- réplica con semillas nuevas.
