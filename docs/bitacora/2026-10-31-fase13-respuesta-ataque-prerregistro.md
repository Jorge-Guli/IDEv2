# 2026-10-31 · Fase 13: ¿el cuerpo responde a un ataque? ¿Se parte en pedazos? (prerregistro)

Escrito antes de correr.

## Por qué
**Pregunta del autor:** la célula atacada, ¿avisa al resto del cuerpo? ¿El cuerpo se defiende, sacrifica la parte o la reconstruye?

En la Tierra, las primeras defensas de los cuerpos fueron simples, mucho antes que los anticuerpos:
- reconocer lo propio;
- avisar por contacto;
- llevar recursos a la herida;
- soltar la parte dañada;
- regenerar.

**Fragmentación:** el [peldaño 3](2026-10-31-fase13-linea-germinal-prerregistro.md) mostró que los cuerpos casi nunca sueltan hijos. Antes de agregar mecanismos hay que ver si se reproducen partiéndose en pedazos de varias células, como muchos organismos reales.

**No se agrega física.** El genoma ya puede:
- sentir la caída de su energía (`delta_e`);
- pasar señales por contacto (los morfógenos de la red regulatoria);
- compartir energía;
- soltarse;
- dividirse unido.

## Medidas nuevas (código)
- **Por célula:**
  - `fundador`: id de la célula que fundó su cuerpo; un hijo unido lo hereda, uno suelto funda uno nuevo;
  - `ultimo_ataque`: paso del último ataque recibido.
- **Respuesta al ataque.** En cuerpos de 3 o más se comparan las células atacadas en los últimos 20 pasos con las no atacadas **que tienen la misma cantidad de enlaces**. Las del borde se atacan más y ya son distintas por estar en el borde. Medidas:
  - `ayuda_herida`: energía recibida de sus socias, atacada − no atacada;
  - `senal_herida`: desvío de sus morfógenos respecto de la media de su cuerpo;
  - `senal_vecinas`: lo mismo para las socias no atacadas de una célula atacada, contra el resto. Responde si el aviso se propaga;
  - `soltarse_herida`: fracción que eligió soltarse.
- **Fragmentación:**
  - `frac_pedazos_fragmentados`: fracción de los pedazos (grupos de 2 o más) cuyo fundador tiene otro pedazo vivo;
  - `fundadores_partidos`.
  - Incluye los cortes por una célula que se suelta y por una célula del medio que muere.

Tests: 211 pasan, 1 omitido. Huellas iguales a la referencia: las medidas no tocan el azar de la simulación.

## Diseño
- **Universo:** `natural.toml`, desde LUCA.
- **Condiciones:**
  - **red:** el universo tal cual;
  - **inerte:** los genes no leen la red, así que la señal por contacto no puede guiar ninguna acción.
- **Semillas:** 39–48, nuevas. **Pasos:** 300 000. Medición desde el paso 200 000.
- **Regla de datos** (aprendida del peldaño 3): una semilla cuenta solo si la medida existe en al menos 30 de las 100 mediciones del último tercio. Un criterio con menos de 6 semillas con dato queda "sin dato suficiente".
- **Ejecución:** Docker (`experiments/fase13/respuesta.py`, contenedor `fase13-respuesta`), al terminar `fase13-cancer`. **Salida:** `runs/fase13/respuesta.json`.

## Criterios
| | Medida | Cumple si |
|---|---|---|
| **R1, ayuda a la herida** | `ayuda_herida` en red | > 0, permutación de signos exacta, p ≤ 0,05 |
| **R2, aviso por contacto** | `senal_vecinas` red − inerte | > 0, permutación pareada, p ≤ 0,05 |

**Exploratorias:**
- `senal_herida` (red − inerte);
- `senal_vecinas` en red;
- `soltarse_herida`;
- `ayuda_herida` (red − inerte);
- fragmentación (descriptiva).

## Qué significaría cada resultado
- **R1:** el cuerpo lleva energía a la célula atacada. Es la primera respuesta fisiológica a una herida.
- **R2:** la célula atacada avisa a sus vecinas por contacto, y eso se sostiene por selección (en el inerte el aviso no sirve para nada).
- **Ninguno:** el cuerpo no reacciona; cada célula enfrenta sola el ataque. Sería otra señal de que el cuerpo todavía es una colonia.
- **Fragmentación alta:** los cuerpos podrían reproducirse partiéndose. Habría que separar la ruptura activa (soltarse) de la pasiva (una muerte en el medio).

## Enmienda (2026-10-31, antes de ver ningún dato)
El experimento se reinició a los pocos segundos de arrancar para sumar una exploratoria: `supresion_cancer_atacantes`, la supresión del cáncer con el azar ciego pesado por cuánto ataca cada célula. Corrige la reserva geométrica del [experimento del cáncer](2026-10-31-fase13-cancer-prerregistro.md). Los criterios R1 y R2 no cambian.

## Resultado (2026-11-01)
10 semillas por condición, 300 000 pasos, sin extinciones. Todas las semillas cumplen la regla de datos. Salida: `runs/fase13/respuesta.json`.

| Criterio | Resultado | ¿Cumple? |
|---|---|---|
| **R1** `ayuda_herida` en red > 0 | 4 de 10 positivas, del orden de 0,0001 de energía, p = 0,63 | **No** |
| **R2** `senal_vecinas` red − inerte > 0 | 6 de 10 positivas, p = 0,12 | **No** |

**Exploratorias:**
- **`soltarse_herida` = 0 en las 20 corridas.** Ninguna célula de un cuerpo usa nunca `soltarse`.
- **`senal_herida`** red − inerte: p = 0,20. La célula atacada no cambia su estado más que en el control.
- **Supresión del cáncer con el azar ciego pesado por atacantes** (corrige la geometría del borde):
  - en red, 9 de 10 positivas (media 0,09), p = 0,003;
  - en inerte, 10 de 10 positivas (media 0,13).
  - **La supresión es real después de la corrección, pero no depende de la red regulatoria.** Alcanza con los sensores, por ejemplo `similitud_frente`.
- **Fragmentación** (hallazgo principal):
  - En 17 de 20 corridas, `frac_pedazos_fragmentados` ≈ 1 y `fundadores_partidos` ≈ 1.
  - Eso significa que **casi todos los cuerpos vivos descienden, por divisiones unidas, de un mismo fundador, y se multiplicaron partiéndose**.
  - Las otras 3 corridas (red 39, inerte 39 e inerte 48) tienen menos enlazados y muchos fundadores, varios partidos.

## Conclusión
- **El cuerpo no responde a un ataque.** No avisa, no ayuda a la herida y no suelta la parte.
- **Pero los cuerpos sí se reproducen: por fragmentación pasiva.** Como no usan `soltarse`, los cortes vienen de células que mueren en el medio (por ataques o hambre) o de enlaces que se rompen al moverse.
  - Explica por qué no hubo línea germinal: los cuerpos no fundan cuerpos con una célula, se parten.
  - En la Tierra existe algo parecido: los filamentos de cianobacterias se parten donde muere una célula (necridios), y las esponjas y muchas algas se reproducen por fragmentos.
- **Una sola estirpe de cuerpos se queda con el mundo** en casi todas las semillas.

**Balance de la fase 13:**
- **Sí hay:** cuerpos clonales, que se reproducen partiéndose, suprimen el canibalismo interno y resisten.
- **No hay:** tipos celulares, línea germinal ni defensa coordinada.
- **La red regulatoria no aporta** a nada de lo medido, contra el control inerte.

Por la decisión del autor (2026-10-31, la naturaleza como inspiración), **la fase 14, un cerebro antes que un cuerpo, pasa al frente.**
