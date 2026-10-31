# 2026-10-30 · Fase 13: controles del cuerpo (prerregistro)

Escrito antes de correr. Responde a la [revisión del piloto del cuerpo](2026-10-30-fase13-cuerpo-prerregistro.md).

## Preguntas
1. ¿Los cuerpos dependen de la forma exacta de la curva del tamaño?
2. ¿Los cuerpos dependen del canibalismo interno?
3. ¿Los cuerpos son clonales?
4. ¿Hay diferenciación dentro del cuerpo, medida sin mezclar clones?

## Diseño
- **Universo:** `natural.toml`, desde LUCA.
- **Semillas:** 13–18, nuevas y emparejadas. **Pasos:** 300 000. Medición desde el paso 200 000.
- **Salida:** `runs/fase13/controles.json`, con el script `experiments/fase13/piloto.py`.
- **Condiciones:**
  - **red:** el universo tal cual (r²/(1+r²));
  - **inerte:** los genes no leen la red;
  - **suave:** la curva r/(1+r), con el mismo 0,5 entre iguales y menos pendiente;
  - **sin_intra:** control (no es un universo): los ataques a miembros del propio grupo no tienen efecto.

## Criterios
| | Medida | Cumple si |
|---|---|---|
| **S1, forma** | `frac_enlazados` en suave | ≥ 0,5 en al menos 5 de 6 semillas |
| **S2, canibalismo** | `frac_enlazados` en sin_intra | ≥ 0,5 en al menos 5 de 6 semillas (los cuerpos no dependen de comerse entre sí) |
| **K, clonalidad** | `parentesco_relativo` en red | < 0,5 en al menos 5 de 6 semillas |
| **P2', diferenciación** | `corr_reg_rol_intra` (correlación estado-rol con la media de cada grupo restada) | red − inerte > 0, permutación pareada exacta, p ≤ 0,05 |

**Exploratorias:** `frac_ataques_intragrupo`, población, depredadores y la diferencia red − sin_intra en enlazados.

## Qué significaría cada resultado
- **S1 y S2:** los cuerpos son robustos. No dependen de la curva elegida ni de un flujo de energía por canibalismo.
- **Falla S1:** el resultado depende de la forma, y se reporta como frágil.
- **Falla S2:** los "cuerpos" se sostienen comiéndose entre sí, más colonia caníbal que organismo.
- **K:** los cuerpos nacen de una célula y comparten genoma, la base para que la selección actúe sobre el cuerpo entero.
- **P2':** la red diferencia a las células de un mismo cuerpo: tipos celulares.

## Ejecución
- **Primer lanzamiento:** en Windows. Se cortó a las 21:02 (se cerró la ventana de comando que el lanzamiento abría en el escritorio), con 1 corrida terminada. Ese parcial queda en `runs/fase13/controles.windows-parcial.json` y no se usa.
- **Relanzamiento:** desde cero, entero en Docker (Linux, 4 procesos, contenedor `fase13-controles`). Así las 24 corridas son de la misma plataforma. Del lanzamiento cortado se vio la única corrida terminada (red, semilla 15: 92 % enlazados, parentesco 0,006, 45 % de ataques dentro del grupo). Los criterios no cambian.

## Resultado (2026-10-31)
Las 24 corridas terminaron en Docker (Linux), sin extinciones. Valores medios desde el paso 200 000.

| Semilla | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|
| Enlazados, red | 0,93 | 0,86 | 0,86 | 0,95 | 0,48 | 0,95 |
| Enlazados, inerte | 0,83 | 0,91 | 0,93 | 0,96 | 0,87 | 0,91 |
| Enlazados, suave | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| Enlazados, sin_intra | 0,93 | 0,91 | 0,92 | 0,91 | 0,92 | 0,93 |
| Parentesco relativo, red | 0,006 | 0,010 | 0,011 | 0,006 | 0,002 | 0,011 |
| Corr. estado-rol dentro del grupo, red | 0,34 | 0,72 | 0,21 | 0,76 | 0,41 | 0,87 |
| Ídem, inerte | 0,29 | 0,25 | 0,18 | 0,36 | 0,52 | 0,18 |

| Criterio | Resultado |
|---|---|
| **S1, forma** | **No se cumple.** Con r/(1+r) no hay cuerpos en ninguna semilla (0 de 6). |
| **S2, canibalismo** | **Se cumple** (6 de 6 ≥ 0,91). Sin canibalismo interno los cuerpos son iguales o más estables. |
| **K, clonalidad** | **Se cumple** (6 de 6 < 0,02). Dentro de un cuerpo la marca heredable casi no varía. |
| **P2', diferenciación** | **No se cumple.** red − inerte positiva en 5 de 6, p = 0,078. |

### Lectura
- **Los cuerpos son reales pero frágiles.** Dependen de que la ventaja del tamaño sea empinada. Con la curva suave pasa lo mismo que sin tamaño: aparecen grupos al principio (hasta 0,16–0,29 enlazados antes del paso 10 000), la depredación sube (58–71 % de depredadores) y los grupos desaparecen. Hay un umbral entre las dos curvas, y no sabemos de qué lado está la naturaleza.
- **No son una colonia caníbal.** Prohibir los ataques dentro del grupo no los debilita: los vuelve más parejos entre semillas (la semilla 17 de red, con 0,48, es la única baja).
- **Son clonales:** nacen de una célula y comparten genoma. Es la base para que la selección actúe sobre el cuerpo entero.
- **Diferenciación:** hay una tendencia (5 de 6, y en tres semillas la diferencia pasa de 0,4), pero no alcanza. No se afirma que haya tipos celulares.

### Consecuencia
La forma de la curva no puede elegirse mirando el resultado (D8 ya la fijó y no se ajusta). Lo que corresponde, por el principio 7, es preguntarle a la realidad: medir en la literatura cuánto más grande tiene que ser un depredador unicelular que su presa para comérsela (razones de tamaño depredador/presa en protistas). Si los datos dicen "casi siempre bastante más grande", r² es la más fiel; si dicen "a menudo del mismo tamaño", la suave. Hasta entonces, todo resultado sobre cuerpos se reporta como condicionado a esa suposición física.
