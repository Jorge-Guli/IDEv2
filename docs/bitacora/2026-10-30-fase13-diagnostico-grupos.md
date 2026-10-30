# 2026-10-30 · Fase 13: por qué desaparecen los grupos en el universo natural (diagnóstico)

Exploración sin prerregistro, para diseñar el peldaño del cuerpo.
- **Script:** `experiments/fase13/diagnostico_grupos.py`. Una subclase solo observa, no cambia la simulación.
- **Corridas:** `natural.toml` con la red activa, semillas 1 y 2, 30 000 pasos.
- **Datos:** `runs/fase13/diagnostico_grupos.json`.

## Qué se ve (por cada 1 000 pasos, con ~550–1 600 organismos)
- **Matanza permanente:**
  - de 10 000 a 32 000 muertes por ataque cada 1 000 pasos, así que un organismo vive en promedio unos 30–50 pasos;
  - hay ~100 ataques por paso, es decir que ~15 % de la población ataca en cada paso;
  - la población se sostiene porque se reproduce sin parar.
- **Los grupos se comen desde adentro.**
  - En la semilla 1, los enlazados son 15–35 % y reciben de sus propios socios entre 1 500 y 9 300 ataques cada 1 000 pasos. En ese mismo lapso mueren 1 400–5 100 enlazados.
  - En la semilla 2 los enlazados caen del 5 % a 0 antes del paso 13 000, y sus socios los atacan cientos de veces.
  - El clon que nace pegado queda justo enfrente de su madre, y el gen "atacar lo que tengo enfrente" no distingue.
- **Los grupos sí se forman:** casi todos los enlaces nacen de dividirse unido (de 1 000 a 6 500 cada 1 000 pasos, contra menos de 120 de unirse). Es el mismo ciclo clonal de la fase 4.
- **Estar en grupo no da más energía:** enlazados y sueltos están parejos (diferencias de ±4 sin signo fijo).
- **Ataques a "parientes":** la mitad de los ataques va a organismos de etiqueta parecida. Como todos descienden de LUCA y la etiqueta deriva lento, esa cifra dice poco.

## Lectura
- **El cuerpo no falla por falta de mecanismo.** Dividirse unido, soltarse y percibir a un socio o a un pariente enfrente (sensores `socio_frente` y `similitud_frente`) ya están en el genoma.
- **Falla porque comerse al clon de al lado rinde y no hay nada que lo frene.** En esta física, cualquier célula mata a otra de su mismo tamaño en 1–3 ataques. Evitarlo pide un peso negativo sobre `socio_frente`, pero con vidas de ~40 pasos la selección de parentesco casi no tiene tiempo de actuar.
- **Diferencia con la realidad:** en la naturaleza, una célula casi nunca se traga a otra de su mismo tamaño. Los depredadores de protistas suelen ser bastante más grandes que su presa, y la principal defensa conocida contra la depredación es crecer, al punto de que en el laboratorio la depredación hizo evolucionar la multicelularidad (Herron et al. 2019, *Chlamydomonas* frente a *Paramecium*).
  - Hoy el ataque no depende del tamaño. La única protección es dividir el daño por 1 + los enlaces del atacado.
  - Hacer que el tamaño importe acercaría la física a la realidad.
  - **Pero la idea surge después de ver un resultado**, y el principio 7 exige justificarla solo por fidelidad, no porque ayude a los grupos. Por eso se consulta al autor antes de tocar nada.
