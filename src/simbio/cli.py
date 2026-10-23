"""Línea de comandos.

    python -m simbio correr [CONFIG] --salida runs/x --semilla 1 --pasos 20000 --set mundo.alto=256
    python -m simbio competir A.npz B.npz [CONFIG] --pasos 3000 --salida runs/comp
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import config, corrida, genoma as gen, persistencia


def _cfg(args) -> config.Config:
    cfg = config.cargar(args.config, args.set)
    if args.semilla is not None:
        cfg.sim.semilla = args.semilla
    if args.pasos is not None:
        cfg.sim.pasos = args.pasos
    return cfg


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="simbio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre in ("correr", "competir"):
        sp = sub.add_parser(nombre)
        if nombre == "competir":
            sp.add_argument("pob_a", help="población A (.npz) o 'luca'")
            sp.add_argument("pob_b", help="población B (.npz) o 'luca'")
        sp.add_argument("config", nargs="?", default=None)
        sp.add_argument("--salida", type=Path, default=None)
        sp.add_argument("--semilla", type=int, default=None)
        sp.add_argument("--pasos", type=int, default=None)
        sp.add_argument("--set", action="append", default=[], metavar="seccion.clave=valor")
    args = ap.parse_args(argv)
    cfg = _cfg(args)

    if args.cmd == "correr":
        sim = corrida.correr(cfg, args.salida, verbose=True)
        print(json.dumps({"pasos": sim.t, "poblacion_final": sim.pob.n}))
    else:
        def cargar(origen):
            return gen.luca(cfg.herencia) if origen == "luca" else persistencia.cargar_genomas(Path(origen))
        frac_b = corrida.competir(cfg, cargar(args.pob_a), cargar(args.pob_b), args.salida,
                                  imagenes=args.salida is not None)
        print(json.dumps({"fraccion_b": frac_b}))


if __name__ == "__main__":
    main()
