"""Línea de comandos.

    python -m simbio correr [CONFIG] --salida runs/x --semilla 1 --pasos 20000 --set mundo.alto=256
    python -m simbio competir A.npz B.npz [CONFIG] --pasos 3000 --salida runs/comp
    python -m simbio dispositivo [--rapido]
    python -m simbio vivir [CONFIG] --salida runs/vivo [--guardar-cada 10000] [--pasos N] [--sin-resembrar]
    python -m simbio mirar runs/vivo
    python -m simbio estimular runs/vivo/clima --texto "hola" | --luz Y X RADIO [--repetir N --cada PASOS]
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
    sp = sub.add_parser("dispositivo", help="detecta CPU/GPU, mide rendimiento y compara")
    sp.add_argument("--rapido", action="store_true")
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
    sp = sub.add_parser("vivir", help="universo continuo: corre sin plazo, guarda su estado y retoma tras un corte")
    sp.add_argument("config", nargs="?", default=None)
    sp.add_argument("--salida", type=Path, required=True)
    sp.add_argument("--semilla", type=int, default=None)
    sp.add_argument("--pasos", type=int, default=None, help="pasos totales (por defecto, sin plazo)")
    sp.add_argument("--guardar-cada", type=int, default=10_000)
    sp.add_argument("--sin-resembrar", action="store_true", help="detenerse si la población se extingue")
    sp.add_argument("--set", action="append", default=[], metavar="seccion.clave=valor")
    sp = sub.add_parser("mirar", help="resumen del estado de un universo continuo (sin detenerlo)")
    sp.add_argument("salida", type=Path)
    sp = sub.add_parser("estimular", help="le da un estímulo (texto o luz) a un universo continuo mientras corre")
    sp.add_argument("salida", type=Path)
    sp.add_argument("--texto", default=None, help="mensaje: cada letra es un pulso de luz")
    sp.add_argument("--luz", nargs=3, type=float, default=None, metavar=("Y", "X", "RADIO"))
    sp.add_argument("--intensidad", type=float, default=1.0)
    sp.add_argument("--repetir", type=int, default=1)
    sp.add_argument("--cada", type=int, default=0, help="pasos entre repeticiones")
    args = ap.parse_args(argv)
    if args.cmd == "estimular":
        from . import estimulos

        if (args.texto is None) == (args.luz is None):
            ap.error("estimular: indicar --texto o --luz (uno de los dos)")
        if args.texto is not None:
            dato = {"tipo": "texto", "texto": args.texto}
        else:
            y, x, r = args.luz
            dato = {"tipo": "luz", "y": int(y), "x": int(x), "radio": r, "intensidad": args.intensidad,
                    "repetir": args.repetir, "cada": args.cada}
        print(f"enviado: {estimulos.enviar(args.salida, dato)}")
        return
    if args.cmd == "mirar":
        from . import continuo

        print(continuo.resumen(args.salida))
        return
    if args.cmd == "vivir":
        from . import continuo

        cfg = config.cargar(args.config, args.set)
        if args.semilla is not None:
            cfg.sim.semilla = args.semilla
        sim = continuo.vivir(cfg, args.salida, args.guardar_cada, args.pasos, not args.sin_resembrar)
        print(json.dumps({"pasos": sim.t, "poblacion": sim.pob.n}))
        return
    if args.cmd == "dispositivo":
        from . import verificar

        verificar.main(args.rapido)
        return
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
