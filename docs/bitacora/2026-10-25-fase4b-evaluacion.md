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

## Lo que todavía no se puede afirmar
- **Que sea división del trabajo en sentido estricto**, con roles diferenciados dentro del grupo. Dos explicaciones son compatibles con los datos:
  - (a) diferenciación: algunos miembros se reproducen y otros no;
  - (b) que los grupos sean más grandes y apretados, de modo que más miembros quedan sin espacio para dividirse.
  
  G3 (solo miembros de borde) reduce el efecto de la posición, pero no lo elimina: un miembro de borde puede estar rodeado por vecinos sin enlace. Para distinguirlas hace falta medir si las divisiones dentro de cada grupo están más concentradas de lo que daría el azar con tasas iguales (sobredispersión), a igual tamaño de grupo.
- **Que exista dependencia:** no se midió si los miembros no reproductores sobreviven solos.
