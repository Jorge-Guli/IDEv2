# Design

## Context

Se extiende el simulador validado en la fase 1 (`openspec/specs/`, `docs/odd/modelo.md`). Ver `proposal.md` (Why). Rendimiento actual: ~50 pasos/s con ~1800 organismos. Las nuevas operaciones deben ser vectorizadas sobre arreglos `(n, 8)`.

## Goals / Non-Goals

**Goals:**
- Que la asociación sea **posible, costosa y opcional**: ningún beneficio impuesto por regla. Los beneficios físicos que existen son llevar energía a un socio que no tiene recurso y repartir el riesgo de morir. Como señaló la revisión, el tope de energía no desperdicia recurso: lo que no se toma queda en la celda.
- Que el camino clonal (hijo que queda pegado) y el camino "agregativo" (unirse a extraños) estén ambos disponibles.
- Medir organización y conflicto (aprovechados).

**Non-Goals:**
- Reproducción del grupo como unidad (fase 3).
- Señales y comunicación explícitas (fase 4).
- Consentimiento para enlazarse: unirse es unilateral y la defensa es soltarse. Esto deja abierta la explotación, que es parte de lo que se quiere observar.

## Decisions

### D1. Enlaces guardados por dirección con identidad del socio
`socio (n, 8)` guarda el `id` del enlazado en la dirección `k`, o −1. Validación en cada paso: el enlace vale si en la celda vecina `k` hay un organismo con ese `id`. Así, si ambos se mueven igual el enlace sobrevive (movimiento en grupo posible), y si uno se aleja, muere o es reemplazado, el enlace se rompe para ambos. La simetría se conserva porque ambos extremos validan la misma geometría.
- *Alternativa: lista de aristas.* Más flexible, pero obliga a reindexar en cada alta o baja.
- *Alternativa: movimiento rígido del grupo.* Impondría coordinación; se prefiere que la coordinación evolucione.

### D1b. Movimiento simultáneo y adhesión (corregido tras la revisión)
- Se puede entrar a una celda libre o a una que deja, en el mismo paso, alguien que avanza en la misma dirección. Así una fila se desplaza entera; antes, el de atrás quedaba frenado y el enlace se rompía.
- **Adhesión** (`asociacion.adhesion`, activada por defecto): un enlazado solo avanza si todos sus enlazados efectivamente avanzan en su misma dirección. Se resuelve por punto fijo: el grupo se mueve junto o no se mueve. Quien queda frenado por la adhesión no paga el costo de avanzar. La versión anterior le cobraba sin que se moviera y sin que pudiera percibirlo, lo que volvía letal cualquier enlace.
- El hijo de una división unida nace con la orientación de su progenitor, para que el camino clonal no nazca descoordinado.
- Sin adhesión (modo "elástico"), el enlace se rompe si los organismos dejan de estar en la misma posición relativa.

### D2. Orden del paso
1. Regenerar recursos.
2. Aprender.
3. Validar enlaces.
4. Sensar.
5. Decidir.
6. Costos: basal, genoma, acción y `costo_enlace · enlaces`.
7. Muerte antes de actuar.
8. Girar.
9. **Compartir**: antes de comer, para que quien recibe ajuste lo que toma y el recurso sobrante quede en la celda. Una versión anterior compartía después de comer y destruía energía cuando el receptor ya estaba lleno.
10. Comer.
11. Avanzar (D1b).
12. **Validar enlaces**: se rompen los estirados.
13. **Soltarse**.
14. **Unirse**: con el de enfrente según la posición y orientación nuevas.
15. **Conjugar**.
16. Estrés.
17. Dividirse y dividirse unido.
18. Altas.

### D3. Primitivas, costos y parámetros por defecto
| Primitiva | Costo | Efecto |
|---|---|---|
| unirse | 0.1 | enlace con el de enfrente si existe y no hay ya enlace en esa dirección |
| soltarse | 0.05 | rompe todos los enlaces propios |
| compartir | 0.05 | cede 20 % de E en partes iguales a los enlazados, que reciben ×0.9 |
| dividirse unido | igual que dividirse | el hijo queda enlazado al progenitor |
| conjugar | 0.5 | copia un gen activo al azar en una ranura libre de un enlazado al azar |

Mantenimiento: 0.02 por enlace y paso para cada extremo, con hasta 8 enlaces.

### D4. Sensores nuevos
Se agregan al final, de modo que los índices de la fase 1 no cambian:
- `enlaces/8`;
- `energía media de los enlazados / E_max` (0 sin enlaces);
- `enlazado_al_frente` (0/1);
- `similitud_etiqueta_frente = 1 − ‖t_i − t_j‖/√2`, que vale 0 si no hay nadie enfrente.

### D5. Etiqueta
Dos números en [0, 1], heredables. Mutan con probabilidad `min(1, 10·m)`, con ruido N(0, 0.05) y recorte. Al sembrar, cada organismo recibe una etiqueta al azar.

### D6. Aprendizaje
Se excluyen del refuerzo, de la línea base y del sensor de ΔE las acciones dividirse, dividirse unido, compartir y conjugar. **La energía recibida de otros se descuenta del ΔE** con el que aprende el receptor: no es resultado de su acción, y sin descontarla se reforzaba lo que estuviera haciendo, típicamente avanzar frenado. El gen recibido por conjugación no participa del refuerzo del paso siguiente.

### D7. Métricas
- Grupos: componentes conexas, por propagación de etiquetas mínimas sobre las aristas (`np.minimum.at` hasta converger), calculadas solo en los pasos de registro.
- Aprovechados: organismos con enlaces cuyo `recibido > 2·dado + 5` acumulado en su vida.
- Parentesco: distancia media de etiqueta entre enlazados, contra la de pares al azar.

### D8. Desactivación
`asociacion.activa = false` excluye las 5 primitivas de la mutación y de la decisión. `asociacion.conjugacion = false` excluye solo conjugar. Los 4 sensores sociales siguen existiendo y valen 0, incluida la similitud de etiqueta.

Controles experimentales:
- **Inerte** (`asociacion.inerte = true`): las primitivas existen, aparecen por mutación y cuestan, pero no tienen efecto (la división unida es una división común). Conserva el espectro mutacional de la condición con asociación, cosa que no hace `activa = false`.
- **Sin beneficio**: eficiencia de compartir 0.
- **Positivo**: eficiencia de compartir 2. Si la asociación no aparece ni siquiera así, el protocolo no tendría poder para detectarla.

## Risks / Trade-offs

- [La asociación no aparece porque no rinde] → es un resultado válido. El control "eficiencia 0" permite separar el "no rinde" del "no se descubre".
- [Unirse unilateral favorece la explotación] → buscado. Se mide con la métrica de aprovechados.
- [La conjugación puede propagar genes egoístas] → buscado como fenómeno. Se puede apagar como control.
- [Rendimiento por bucles de conjugación] → la conjugación es un bucle en Python; si se vuelve frecuente, se vectoriza.
- [Las poblaciones `.npz` de la fase 1 no se pueden cargar] → aceptado, porque cambia la forma de los pesos.
