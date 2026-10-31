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
