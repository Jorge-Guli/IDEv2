"""Calibración del bien público (fase 2b), con objetivo prerregistrado.

Un secretor quieto, solo, en un campo uniforme de recurso complejo C (política: come si hay alimento
libre en su celda, si no secreta). Se mide:
  b_propio/c = lo que come él / lo que gastó en secretar
  b_total/c  = lo digerido en total / lo que gastó
  grupo/c    = lo que come cada uno de un bloque 3×3 de secretores idénticos / lo que gastó cada uno

Objetivo (dilema con ventaja para la agrupación): b_propio/c < 1 < grupo/c, con b_total/c > 1.
Basado en el script de la revisión científica de la fase 2b.

Uso: python experiments/fase2b/calibrar.py
"""

from __future__ import annotations

import itertools

import numpy as np

from simbio.config import BienPublicoCfg, MundoCfg
from simbio.entorno import Entorno


def medir(C, k, deg_z, costo, de=0.1, dl=0.2, pasos=400, bloque=1, umbral=0.05):
    bp = BienPublicoCfg(activo=True, tasa_digestion=k, degradacion_enzima=deg_z, costo_secretar=costo,
                        difusion_enzima=de, difusion_libre=dl)
    e = Entorno(MundoCfg(alto=48, ancho=48, capacidad_max=0.0), np.random.default_rng(0), bp=bp)
    e.Kc[:] = C
    e.C[:] = C
    r = bloque // 2
    celdas = [(24 + a, 24 + b) for a in range(-r, r + 1) for b in range(-r, r + 1)]
    comido = secreciones = producido = 0.0
    for t in range(pasos):
        e.paso(t)
        producido += e.digerido
        for c in celdas:
            if e.A[c] >= umbral:
                q = min(e.A[c], 4.0)
                e.A[c] -= q
                comido += q
            else:
                e.Z[c] += bp.enzima_por_secrecion
                secreciones += 1
    gasto = costo * max(secreciones, 1)
    return comido / gasto, producido / gasto


def main():
    print(f"{'C':>5} {'k':>5} {'degZ':>5} {'costo':>5} | {'propio/c':>8} {'total/c':>8} {'grupo3x3/c':>10}  objetivo")
    for C, k, deg_z, costo in itertools.product((5.0, 10.0), (0.02, 0.05, 0.1, 0.5), (0.1, 0.3), (0.3, 1.0)):
        propio, total = medir(C, k, deg_z, costo)
        grupo, _ = medir(C, k, deg_z, costo, bloque=3)
        ok = propio < 1.0 < grupo and total > 1.0
        print(f"{C:5.1f} {k:5.2f} {deg_z:5.2f} {costo:5.2f} | {propio:8.2f} {total:8.2f} {grupo:10.2f}  {'✔' if ok else ''}")


if __name__ == "__main__":
    main()
