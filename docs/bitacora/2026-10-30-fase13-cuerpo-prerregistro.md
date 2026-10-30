# 2026-10-30 · Fase 13: comer según el tamaño y el cuerpo (prerregistro)

Escrito antes de correr. Antecedentes:
- [piloto de la red](2026-10-30-fase13-red-regulatoria-prerregistro.md): nulo y casi sin grupos;
- [diagnóstico](2026-10-30-fase13-diagnostico-grupos.md): los grupos se forman, pero se los comen, y cualquier célula mata a otra de su tamaño en 1–3 ataques.

## Cambio de física (más fiel a la realidad, aprobado por el autor)
`ataque.tamano = true`: el daño de un ataque se multiplica por r² / (1 + r²), donde r es el tamaño del grupo del atacante dividido por el del atacado.
- **Valores:** 0,5 entre iguales, 0,9 si el atacante es el triple y 0,1 si es un tercio. Reemplaza a la protección por enlaces.
- **Por qué:** en la naturaleza una célula casi nunca se traga a otra de su tamaño, y los depredadores suelen ser más grandes que su presa.
- **Forma elegida una vez:** no se ajusta según el resultado.
- **Ya forma parte de `natural.toml`.**
- **Prueba de viabilidad:** 20 000 pasos, semillas 101 y 102. Se miró solo la población: 590–3 400 organismos, sin extinciones.

## Pregunta
- Con una física del comer más real, ¿se sostienen los cuerpos (grupos)?
- Si hay cuerpos, ¿la red regulatoria diferencia sus células?

## Diseño
- **Universo:** `natural.toml` (con el tamaño), desde LUCA.
- **Semillas:** 7–12, nuevas y emparejadas. **Pasos:** 300 000.
- **Salida:** `runs/fase13/cuerpo.json`, con el script `experiments/fase13/piloto.py`.
- **Condiciones:**
  - **red:** el universo tal cual;
  - **inerte:** los genes no leen la red (control de la red);
  - **sin_tamano:** el ataque de antes (control de la física del tamaño).
- **Medición:** en el último tercio (desde el paso 200 000), con un registro cada 1 000 pasos.

## Criterios (permutación pareada exacta, una cola; con 6 semillas, el p mínimo es 1/64)
| | Medida | Cumple si |
|---|---|---|
| **C1, cuerpo** | `frac_enlazados` | red − sin_tamano > 0, p ≤ 0,05 |
| **P2, diferenciación** | desvío del estado regulatorio dentro de los grupos de 3 o más, dividido por el de la población | red − inerte > 0, p ≤ 0,05. Solo es evaluable si hay grupos de 3 o más en al menos 5 de los 6 pares; si no, "no evaluable" |

**Sin criterio de uso de la red:** en el piloto anterior `con_gen_regulado` se saturó por deriva. El peso medio de lectura queda como exploratoria y se compara con el inerte sabiendo que ahí los pesos derivan libres.

**Exploratorias:**
- grupos de 3 o más;
- población y depredadores frente a sin_tamano;
- dispersión de roles en los grupos;
- correlación entre estado y rol;
- extinciones.

## Qué significaría cada resultado
- **C1 y P2:** la física real del tamaño sostiene cuerpos y la red diferencia sus células. Son los primeros tipos celulares, y lo siguiente es la reproducción sexual o las células mensajeras.
- **C1 sin P2:** hay cuerpos, pero sin tipos celulares. Lo siguiente sería un cuerpo con línea germinal o más tiempo evolutivo (universo continuo).
- **Ninguno:** el tamaño no alcanza para sostener cuerpos. Se registra y se busca la próxima diferencia con la realidad, sin premiar a los grupos.

## Resultado (2026-10-30, 19:47): C1 se cumple; P2 no
18 corridas de 300 000 pasos y **0 extinciones**. Medido desde el paso 200 000.

| | red | control | Diferencias | p | |
|---|---|---|---|---|---|
| **C1** `frac_enlazados` | 0,80–0,96 | sin_tamano: 0,0001–0,0003 | +0,80 a +0,96, 6 de 6 | **1/64 = 0,016** | ✅ |
| **P2** diferenciación relativa | 0,25–0,75 | inerte: 0,16–0,75 | 4 de 6 positivas (−0,38 a +0,52) | 0,22 | ❌ |

**Exploratorias:**
- **Cuerpos:**
  - con el tamaño, el 51–85 % de los organismos vive en grupos de 3 o más, con un tamaño medio de 3–10 células;
  - sin el tamaño, nadie: los enlazados caen a 0 antes del paso 10 000;
  - los cuerpos se forman despacio: 38 % enlazados a los 10 000 pasos, 64 % a los 50 000 y 90 % a los 300 000.
- **Ecología:**
  - más población con el tamaño (+36 a +669 en las 6 semillas);
  - menos depredadores (24–41 % contra 56–69 %);
  - vidas más largas: ~2 000 generaciones en 300 000 pasos, contra ~8 300 sin el tamaño.
- **La red:**
  - el peso de lectura ya no es menor que en el inerte (4 de 6 mayores, p = 0,44): con cuerpos, la red deja de estorbar;
  - correlación entre estado regulatorio y rol: máxima 0,78–0,80 en las semillas 8 y 9 con red, contra 0,20–0,54 en todas las del inerte;
  - dispersión de roles en los grupos: mayor con red en 3 de 6.
  - **Indicio en 2–3 semillas, no un resultado.**

**Lectura:**
- Corregir una sola cosa para que se pareciera más a la realidad (una célula casi no puede comerse a otra de su tamaño) bastó para que aparecieran **cuerpos multicelulares**: grupos clonales que dominan la población. No se programó ningún premio para los grupos.
- Es lo mismo que se observa en el laboratorio: la depredación hizo evolucionar la multicelularidad en *Chlamydomonas* (Herron et al. 2019).
- **Límites:**
  - el efecto de la física es directo: estar en grupo protege por definición del ataque según el tamaño. Lo que emerge es que la evolución lo aprovecha formando grupos clonales que crecen y se mantienen;
  - todavía no hay tipos celulares consistentes, solo indicios en 2 semillas.
- **Siguiente:**
  - mirar por dentro los cuerpos de las semillas 8 y 9: si las células en distinto estado hacen cosas distintas;
  - llevar el universo natural, con cuerpos, a corridas más largas.

## Revisión escéptica (`revisor-cientifico`, 2026-10-30) y correcciones
- **C1 está bien calculado, pero "emergen cuerpos" está sobredicho.** Que estar en grupo proteja es una consecuencia directa de la física del tamaño, que premia el tamaño del conjunto tanto al defenderse como al atacar.
  - **No es el factor 0,5 entre iguales:** el revisor corrió un control con la depredación a la mitad y sin dependencia del tamaño (64², semillas 1–3). Dio 0–0,005 enlazados, contra 0,74–0,85 con el tamaño.
  - **La lectura correcta:** la evolución aprovecha el refugio que ofrece la física y forma grupos que se sostienen. El tamaño como protección es un **supuesto físico declarado**, no un hallazgo.
- **"Clonales" no está demostrado:** no se midió parentesco dentro de los grupos. Se corrige y se agrega la medida `parentesco_relativo`.
- **Canibalismo dentro del cuerpo:** según la medición del revisor, del 16 % al 37 % de los ataques van a un miembro del propio grupo, y crece con el tiempo. Los "cuerpos" son en parte colonias que se comen entre sí. Se agrega la medida `frac_ataques_intragrupo` y un control sin canibalismo interno.
- **Forma de la curva:** r²/(1+r²) fue una elección hecha después de ver el fracaso de los grupos. Se agrega una prueba de sensibilidad con r/(1+r), sin ajustar nada.
- **Las exploratorias de la red son ruido o artefacto:**
  - `corr_reg_rol_max` mezcla diferencias entre clones distintos y toma el máximo de 8 reguladores;
  - "la red deja de estorbar" (p = 0,44) no debe citarse.
  - Se agrega `corr_reg_rol_intra`, que resta la media de cada grupo y deja solo la diferencia entre células del mismo cuerpo.
- **Estado estacionario no demostrado:** los cuerpos seguían creciendo a los 300 000 pasos.
- **Código:** sin errores graves. `componentes` corre en CPU dentro del ataque, como ya hacía el movimiento de grupos.
