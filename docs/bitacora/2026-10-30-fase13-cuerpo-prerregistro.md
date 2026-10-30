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
