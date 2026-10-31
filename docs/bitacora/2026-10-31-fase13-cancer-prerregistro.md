# 2026-10-31 · Fase 13: ¿la evolución suprime el "cáncer"? (prerregistro)

Escrito antes de correr.

## Origen
Una observación del autor: atacar a una hermana del propio cuerpo es casi como un cáncer, donde células del mismo cuerpo atacan a otras. En biología es exactamente así: el cáncer es una célula que "hace trampa" contra el cuerpo y vuelve a comportarse como un individuo suelto (Aktipis et al. 2015, *Cancer across the tree of life*). Todo organismo multicelular tuvo que evolucionar defensas contra eso. **Que aparezca esa supresión es una de las señales de que el cuerpo pasó a ser un individuo.**

No se cambia la física: el cáncer es real, no se prohíbe. Se mide si la evolución lo frena.

## Mirada exploratoria previa (datos de los controles, semillas 13–18)
- En `red`, donde atacar a una hermana le quita energía, los ataques internos son el 8–52 % del total.
- En `sin_intra`, donde atacarla no tiene efecto, son el 54–84 %.
- Más bajos en `red` en las 6 semillas.

Pero falta saber cuántos ataques internos habría si las células atacaran a ciegas: depende de cuántas tienen a una hermana enfrente.

## Medida nueva (código)
- `frac_frente_hermana`: entre los organismos con alguien enfrente, fracción cuyo vecino de enfrente es de su mismo cuerpo. Es la fracción de ataques internos esperada a ciegas.
- **`supresion_cancer`** = `frac_frente_hermana` − `frac_ataques_intragrupo`. Mayor que 0 significa que se evita atacar a las hermanas.
- Las células pueden distinguir a una hermana: tienen los sensores `socio_frente` y `similitud_frente`, y la red regulatoria.

Tests: 209 pasan, 1 omitido. Huellas iguales.

## Diseño
- **Universo:** `natural.toml`, desde LUCA.
- **Condiciones:** `red` (el universo tal cual) y `sin_intra` (control: los ataques a hermanas no tienen efecto, no hay cáncer que suprimir).
- **Semillas:** 29–38 (10, nuevas). **Pasos:** 300 000. Medición desde el paso 200 000.
- **Ejecución:** Docker (`experiments/fase13/cancer.py`), apenas termine la línea germinal (límite de procesos del equipo).

## Criterios
| | Medida | Cumple si |
|---|---|---|
| **C1, supresión** | `supresion_cancer` en red | > 0, permutación de signos exacta, p ≤ 0,05 |
| **C2, por selección** | `supresion_cancer` red − sin_intra | > 0, permutación pareada, p ≤ 0,05 |

## Qué significaría
- **C1 y C2:** la evolución frena el cáncer porque daña al cuerpo. Es selección al nivel del cuerpo: el cuerpo empieza a ser un individuo.
- **C1 sin C2:** las células evitan atacar a las hermanas, pero también sin daño. Puede ser solo que atacar a una hermana rinde poco (r = 1, la mitad del efecto).
- **Ninguno:** las células atacan a ciegas; el cuerpo todavía es una colonia sin defensas contra sus tramposas.
