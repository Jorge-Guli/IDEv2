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

## Resultado (2026-10-31)
10 semillas por condición, 300 000 pasos, sin extinciones. Salida: `runs/fase13/cancer.json`.

| Criterio | Resultado | ¿Cumple? |
|---|---|---|
| **C1** `supresion_cancer` en red > 0 | 9 de 10 positivas, p = 0,002. La semilla 30 da 0, pero no tiene cuerpos (0,01 % de enlazados): no hay cáncer posible | **Sí, con una reserva** (abajo) |
| **C2** red − sin_intra > 0 | 6 de 10 positivas, p = 0,11 | **No** |

**Lo que se ve:**
- **En red** hay dos grupos de semillas:
  - 6 suprimen fuerte: 0,39–0,54. Por ejemplo, tienen una hermana enfrente el 92 % de las veces, pero solo el 38 % de sus ataques van a hermanas.
  - 3 suprimen poco: 0,01–0,10.
- **En sin_intra** también hay supresión, más pareja: 0,004–0,39, positiva en 10 de 10.

**Por qué C2 sale nulo, y qué significa:**
- El control `sin_intra` no es un universo "sin cáncer" neutral. Ahí atacar a una hermana **no rinde nada** al atacante, mientras que en red rinde la mitad.
- Por lo tanto, en sin_intra la propia célula tiene más razones para no atacar hermanas, y aun así la supresión es en general menor que en red (6 de 10).
- Es una pista a favor de una selección a nivel del cuerpo, pero no alcanza a ser significativa. El control mezcla dos cosas: el daño al cuerpo y la ganancia del atacante.

**Reserva sobre C1 (geometría):** el azar ciego se calculó sobre todas las células con alguien enfrente. Las que atacan son sobre todo las del borde, que tienen menos hermanas enfrente que las del interior. Parte de la "supresión" puede ser solo eso: atacan las del borde y miran hacia afuera.

## Conclusión
- **Hay supresión del cáncer en sentido amplio:** las células atacan a sus hermanas mucho menos de lo que les tocaría a ciegas, en 9 de 9 semillas con cuerpos.
- **No está demostrado que sea por el bien del cuerpo** (C2 nulo).
- **Tampoco está descartado que sea geometría** del borde.

## Correcciones para la próxima medición (hechas antes de ver nuevos datos)
- **Medida nueva** `supresion_cancer_atacantes`: el azar ciego pesado por cuánto ataca cada célula (`uso_atacar`). Así compara a las atacantes contra sí mismas y saca la geometría del borde.
  - Se agregó al experimento de respuesta al ataque (semillas 39–48, red contra inerte), reiniciado a los pocos segundos de arrancar, sin datos.
- **Un control más limpio para C2** sería uno donde atacar a una hermana siga rindiendo al atacante, pero no le quite energía a la hermana. Eso crea energía de la nada y viola la física. Por eso no se hace.
  - La alternativa honesta es comparar la supresión entre cuerpos más y menos emparentados: con más parentesco, más selección a nivel del cuerpo.
  - Hoy el parentesco es casi siempre clonal (< 0,02), así que hoy no hay variación para comparar.
