# 2026-10-31 · Fase 13: forma de la curva del tamaño, según la realidad (prerregistro)

Escrito antes de leer la literatura. Responde al resultado de los [controles del cuerpo](2026-10-30-fase13-cuerpo-controles-prerregistro.md): con r²/(1+r²) hay cuerpos, con r/(1+r) no. La curva no se elige por el resultado; se elige por los datos.

## Qué se compara
En el modelo, la fracción del daño que logra un ataque es f(r), con r = tamaño (en células, o sea volumen) del atacante sobre el del atacado. Las dos curvas valen 0,5 entre iguales y difieren en la pendiente:

| r (volumen) | 1/4 | 1/2 | 1 | 2 | 4 |
|---|---|---|---|---|---|
| r²/(1+r²) | 0,06 | 0,20 | 0,50 | 0,80 | 0,94 |
| r/(1+r) | 0,20 | 0,33 | 0,50 | 0,67 | 0,80 |

Equivalente real: la eficacia con que un depredador unicelular (fagótrofo: ciliado, flagelado, ameba, dinoflagelado) captura e ingiere presas según su razón de volumen, relativa a la máxima.

## Fuentes
Revisiones y datos de laboratorio sobre tamaño óptimo de presa y espectro de tamaños de presa en protistas fagótrofos (por ejemplo, la compilación de Hansen, Bjørnsen y Hansen, 1994, y trabajos posteriores). Se usan valores publicados; no se ajusta nada a mano.

## Regla de decisión
Pasando las razones de longitud a volumen (volumen ∝ longitud³):
1. Se estima, para el conjunto de taxones, la eficacia relativa a la máxima con presas de **igual volumen** (r = 1) y de **doble volumen** que el depredador (r = 1/2).
2. **Se queda r²/(1+r²)** si la típica (mediana de los taxones) es ≤ 0,33 en r = 1/2, es decir, más empinada que la suave.
3. **Se pasa a r/(1+r)** si la típica es > 0,33 en r = 1/2 y, además, comer presas de igual o mayor volumen es común (más de la mitad de los taxones lo hace con eficacia ≥ 0,5 de su máxima).
4. **Si los datos son más empinados que las dos curvas** (comer a un igual es raro), se queda r², la más cercana de las dos, y se anota que la realidad es aún más empinada. No se agrega otra curva sin otro prerregistro.
5. Si los datos no alcanzan para decidir, se dice así, y el resultado de los cuerpos sigue condicionado a la suposición.

Se registran también las excepciones conocidas (depredadores que comen presas más grandes que ellos) y qué fracción representan.

## Resultado (2026-10-31)
### Qué se encontró
- **Hansen, Bjørnsen y Hansen (1994),** *Limnology and Oceanography* 39: 395–403. Compararon el espectro de tamaños de presa de 28 depredadores planctónicos (18 estudios). Razón de longitud óptima depredador:presa:
  - dinoflagelados ~1:1;
  - otros flagelados ~3:1;
  - ciliados ~8:1;
  - rotíferos y copépodos ~18:1.

  En volumen (∝ longitud³), el óptimo de un flagelado es una presa ~27 veces más chica, y el de un ciliado, ~500 veces.
- **Regla general de los textos de ecología microbiana:** los protistas comen presas de diámetro ~10 veces menor que el suyo (~1000 veces en volumen).
- **Excepciones:** dinoflagelados que comen presas de su tamaño o mayores (por ejemplo, con palio o pedúnculo), amebas que prefieren diatomeas grandes, y casos aislados de presas mucho mayores. Los datos de óptimo 1:1 de dinoflagelados heterótrofos se basan en solo 11 observaciones.
- **Ancho del espectro:** los modelos de plancton suelen usar una preferencia log-normal centrada en 10:1 de longitud con desvío ~0,5. Con ese ancho, una presa de igual tamaño se come con un 10–20 % de la eficacia máxima para el depredador típico (óptimo 8–10:1), y una de doble volumen, con menos de 10 %.

### Aplicación de la regla
- La típica a r = 1/2 queda ≤ 0,33 (≲ 0,1 para el depredador típico): **no se pasa a la suave** (punto 3).
- Comer a un igual con eficacia ≥ 0,5 de la máxima no es lo común; lo hacen sobre todo los dinoflagelados. La realidad es **más empinada que las dos curvas**: en el modelo, entre iguales el daño es 0,5, y en la realidad es mucho menor.
- **Decisión (punto 4): se queda r²/(1+r²),** la más cercana de las dos. Se anota que la realidad es todavía más empinada. No se agrega otra curva sin otro prerregistro.

### Límites
- Las tablas de Hansen et al. son imágenes escaneadas y no se pudieron leer por máquina. Se usaron los valores del resumen y de las citas posteriores, no los datos especie por especie.
- El ancho del espectro (desvío ~0,5) viene de modelos de plancton, no de una medición directa leída aquí.
- El modelo mide el tamaño en número de células de un grupo, no en tamaño celular. Un grupo de N células equivale a N volúmenes.
- Los datos son de plancton acuático. Hay depredadores que rompen la regla (dinoflagelados, *Didinium*), y en la naturaleza conviven con los demás.

### Consecuencia
Los cuerpos de la fase 13 dejan de estar "condicionados a una suposición elegida": están condicionados a una suposición **respaldada por los datos**, y del lado conservador, porque la física real protege todavía más a lo grande. El resultado de la curva suave queda como sensibilidad: muestra qué pasaría en un mundo donde comerse a un igual fuera fácil, que no es el nuestro.

### Fuentes
- Hansen, B., Bjørnsen, P. K. y Hansen, P. J. (1994). *The size ratio between planktonic predators and their prey.* Limnology and Oceanography 39(2): 395–403.
- Resumen de la regla 10:1 para protistas: *Processes in Microbial Ecology* (Kirchman, Oxford University Press), capítulo de protistas.
- *Planktonic prey size selection reveals an emergent keystone predator effect and niche partitioning*, PLOS ONE (2023), PMC9925011: modelo con preferencia log-normal y revisión de inversiones de tamaño en protistas.
- *On the sensitivity of plankton ecosystem models to the formulation of zooplankton grazing*, PLOS ONE (2021): preferencia log-normal centrada en 10:1, desvío 0,5.
