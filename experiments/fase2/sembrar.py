"""Experimento E: ¿la asociación es inestable o solo difícil de descubrir?

Se siembra una población "colonial": LUCA que se divide quedando unido (en vez de dividirse suelto) y
que comparte energía cuando tiene más que sus socios. Se mide si la evolución conserva esos genes.

Uso:
    python experiments/fase2/sembrar.py --salida runs/sembrar [--pasos 20000] [--semillas 5] [--procesos 4]
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, corrida, genoma as gen

RAIZ = Path(__file__).resolve().parents[2]
CONDICIONES = {
    "colonial": [],
    "colonial_inerte": ["asociacion.inerte=true"],  # mismos genes, sin efecto: tasa de pérdida por deriva
    "colonial_elastico": ["asociacion.adhesion=false"],
    "colonial_positivo": ["asociacion.eficiencia_compartir=2.0"],
}
SERIES = ["poblacion", "frac_enlazados", "tamano_grupo_medio", "tiene_dividirse_unido", "tiene_dividirse",
          "tiene_compartir", "usa_compartir", "frac_aprovechados"]


def genoma_colonial(cfg) -> dict:
    g = gen.luca(cfg.herencia)
    g["prim"][g["prim"] == gen.DIVIDIRSE] = gen.DIVIDIRSE_UNIDO
    k = int(np.flatnonzero(~g["activo"][0])[0])
    g["activo"][0, k] = True
    g["prim"][0, k] = gen.COMPARTIR  # compartir solo si tengo socios y más energía que ellos
    g["b"][0, k] = -3.0
    g["w"][0, k, gen.S_ENLACES] = 20.0
    g["w"][0, k, gen.S_ENERGIA] = 4.0
    g["w"][0, k, gen.S_ENERGIA_SOCIOS] = -6.0
    return g


def verificar_viabilidad() -> None:
    """El genoma colonial tiene que reproducirse y formar enlaces en un mundo sin mutación."""
    cfg = config.cargar(RAIZ / "experiments" / "configs" / "base.toml",
                        ["herencia.mutacion=false", "mundo.alto=64", "mundo.ancho=64", "sim.registrar_cada=500"])
    g = gen.repetir(genoma_colonial(cfg), cfg.sim.poblacion_inicial)
    sim = corrida.correr(cfg, None, genomas=g)
    sim.correr(1500)
    h = sim.historial[-1]
    assert h["poblacion"] > 0 and h["nacimientos"] > 0 and h["frac_enlazados"] > 0.1, h
    print(f"viabilidad: población {h['poblacion']}, enlazados {h['frac_enlazados']:.2f}")


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    cfg = config.cargar(RAIZ / "experiments" / "configs" / "base.toml", CONDICIONES[nombre] + ["sim.registrar_cada=250"])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    g = gen.repetir(genoma_colonial(cfg), cfg.sim.poblacion_inicial)
    g["etiqueta"] = np.random.default_rng(semilla).random((cfg.sim.poblacion_inicial, 2))
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}", genomas=g)
    return {"nombre": nombre, "semilla": semilla, "pasos": sim.t,
            "serie": {m: [h.get(m, float("nan")) for h in sim.historial] for m in SERIES + ["t"]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "sembrar")
    ap.add_argument("--pasos", type=int, default=20000)
    ap.add_argument("--semillas", type=int, default=5)
    ap.add_argument("--procesos", type=int, default=4)
    args = ap.parse_args()
    verificar_viabilidad()
    tareas = [(str(args.salida), n, s, args.pasos) for n in CONDICIONES for s in range(1, args.semillas + 1)]
    with Pool(args.procesos) as pool:
        res = pool.map(_correr, tareas)
    informe = {"parametros": vars(args) | {"salida": str(args.salida)}, "condiciones": {}}
    for n in CONDICIONES:
        rs = [r for r in res if r["nombre"] == n]
        t = rs[0]["serie"]["t"]
        cortes = [i for i, x in enumerate(t) if x in (0, 1000, 2500, 5000, 10000, 20000) or x == t[-1]]
        informe["condiciones"][n] = {
            m: {str(int(t[i])): round(float(np.nanmean([r["serie"][m][i] for r in rs if len(r["serie"][m]) > i])), 4)
                for i in cortes} for m in SERIES}
        informe["condiciones"][n]["extinciones"] = sum(r["serie"]["poblacion"][-1] == 0 for r in rs)
    args.salida.mkdir(parents=True, exist_ok=True)
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
