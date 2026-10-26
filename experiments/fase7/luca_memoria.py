"""Fase 7c: ¿el mundo premia recordar? LUCA con un módulo de memoria contra LUCA, compitiendo desde cero.

Mitad LUCA (cepa 0) y mitad LUCA con cinco genes de memoria conectados (cepa 1): memoria = pista; comer
inhibido si el tipo no coincide con la memoria; avanzar si no coincide. LUCA también recibe los cinco genes,
con pesos y sesgo 0 (mismo costo). Sin mutación ni aprendizaje; la memoria de la cepa 1 arranca en la estación
vigente.

Uso:
    python experiments/fase7/luca_memoria.py [--semillas 6] [--pasos 20000] [--castigos 0.5 2.0] [--procesos 4]
        [--regulado] [--extra clave=valor ...]
"""

from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, genoma as gen
from simbio import dispositivo as dev
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "experiments" / "fase7"))
import evaluar as fase7  # noqa: E402
import invadir_memoria as inv  # noqa: E402  (los mismos cinco genes)

AJUSTES = fase7.MUNDO + ["memoria.activa=true", "memoria.tasa=1.0", "aprendizaje.activo=false",
                         "herencia.mutacion=false"]


def _correr(tarea):
    semilla, pasos, castigo, extra, regulado = tarea
    genes = inv.GENES_REGULADOS if regulado else inv.GENES
    cfg = config.cargar(fase7.CONFIG, AJUSTES + [f"estaciones.castigo={castigo}"] + list(extra))
    cfg.sim.semilla = semilla
    n = cfg.sim.poblacion_inicial
    g = gen.repetir(gen.luca(cfg.herencia), n)
    g["etiqueta"] = np.random.default_rng(semilla).random((n, 2))
    cepas = np.zeros(n, dtype=np.int16)
    cepas[: n // 2] = 1
    a = {k: v[: n // 2] for k, v in g.items()}
    inv.agregar(a, True, genes)
    b = {k: v[n // 2:] for k, v in g.items()}
    inv.agregar(b, False, genes)
    for k in g:
        g[k][: n // 2], g[k][n // 2:] = a[k], b[k]
    sim = Simulacion(cfg, g, cepas)
    m = dev.a_cpu(sim.pob["cepa"]) == 1
    sim.pob["memoria"][sim.xp.asarray(np.flatnonzero(m)), 0] = 1.0 if sim.estacion() > 0 else 0.0
    serie = []
    for _ in range(pasos):
        sim.paso()
        if sim.t % 1000 == 0:
            c = dev.a_cpu(sim.pob["cepa"])
            serie.append([int((c == 0).sum()), int((c == 1).sum())])
    n0, n1 = serie[-1]
    return {"semilla": semilla, "castigo": castigo, "extra": list(extra), "serie": serie,
            "frac_memoria": n1 / (n0 + n1) if n0 + n1 else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semillas", type=int, default=6)
    ap.add_argument("--pasos", type=int, default=20000)
    ap.add_argument("--castigos", type=float, nargs="*", default=[0.5, 2.0])
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--regulado", action="store_true", help="fase 9: el módulo de memoria con genes condicionados")
    args = ap.parse_args()
    with Pool(args.procesos) as pool:
        rs = pool.map(_correr, [(s, args.pasos, c, tuple(args.extra), args.regulado) for c in args.castigos
                                for s in range(1, args.semillas + 1)])
    for r in rs:
        print(r["castigo"], r["semilla"], "memoria:", r["frac_memoria"], "serie (LUCA, memoria):", r["serie"][::5] + r["serie"][-1:])


if __name__ == "__main__":
    main()
