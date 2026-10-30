"""Fase 13, desarrollo (peldaños 1 y 2): ¿la evolución usa la red regulatoria? ¿Aparecen tipos celulares?

Universo de la fase 3 (coordinacion.toml: depredador que solo come grupos chicos, con escalada; movimiento de grupo
por fuerza, α = 0,5, adoptado en la fase 3c), desde LUCA. Condiciones:
    red:    la red regulatoria existe y los genes la leen
    inerte: la red existe, muta y cambia de estado igual, pero los genes no la leen (control de deriva)
Se mide en el último tercio:
    - uso: fracción de organismos con algún gen que lee la red con peso > 0,5 (con_gen_regulado) y peso medio
    - diferenciación: desvío del estado regulatorio dentro de los grupos de 3 o más, relativo al de la población
    - roles: dispersión del rol (comer contra avanzar) dentro de los grupos

Uso (desde la raíz):  python experiments/fase13/piloto.py --pasos 100000 --semillas 1 2 3 4 --procesos 6
Cada corrida se guarda al terminar en <salida>.parcial.json; si se corta, el mismo comando sigue desde ahí.
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
BASE = ['asociacion.movimiento="fuerza"', "asociacion.exponente_arrastre=0.5", "desarrollo.activo=true",
        "sim.registrar_cada=1000"]
CONDICIONES = {"red": [], "inerte": ["desarrollo.inerte=true"]}
CLAVES = ["poblacion", "generacion_media", "genes_medios", "grupos_de_3_o_mas", "tamano_grupo_medio",
          "con_gen_regulado", "peso_regulador_medio", "reg_medio_abs", "dispersion_reg_grupos",
          "dispersion_reg_poblacion", "corr_reg_rol_max", "dispersion_roles_grupos", "dispersion_roles_poblacion",
          "tasa_efectiva_media"]


def correr(tarea):
    nombre, semilla, pasos, ajustes = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/coordinacion.toml", [*BASE, *ajustes, *CONDICIONES[nombre]])
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg)
    for _ in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            break
    serie = [{"t": f["t"], **{c: round(float(f[c]), 5) for c in CLAVES if c in f and f[c] == f[c]}}
             for f in sim.historial]
    return {"condicion": nombre, "semilla": semilla, "extinta_en": sim.t if sim.pob.n == 0 else None,
            "serie": serie}


def permutacion_pareada(dif) -> float:
    """p de una cola (media > 0) por inversión de signos exacta."""
    d = np.asarray([x for x in dif if x == x], dtype=float)
    if d.size == 0:
        return float("nan")
    signos = ((np.arange(2 ** d.size)[:, None] >> np.arange(d.size)) & 1) * 2 - 1
    return float(((signos * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def final(r, clave, desde):
    v = [f[clave] for f in r["serie"] if f["t"] >= desde and clave in f]
    return float(np.mean(v)) if v and r["extinta_en"] is None else float("nan")


def evaluar(res, desde):
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({r["semilla"] for r in res})
    out = {}

    def rel(r):  # diferenciación: desvío dentro de los grupos relativo al de la población
        g, p = final(r, "dispersion_reg_grupos", desde), final(r, "dispersion_reg_poblacion", desde)
        return g / p if p and p == p and p > 1e-9 else float("nan")

    medidas = {c: (lambda r, c=c: final(r, c, desde)) for c in ("con_gen_regulado", "peso_regulador_medio",
                                                                "dispersion_roles_grupos", "poblacion")}
    medidas["diferenciacion_relativa"] = rel
    for nombre, f in medidas.items():
        dif = [round(f(por[("red", s)]) - f(por[("inerte", s)]), 5)
               for s in semillas if ("red", s) in por and ("inerte", s) in por]
        out[nombre] = {"red": {s: round(f(por[("red", s)]), 4) for s in semillas if ("red", s) in por},
                       "inerte": {s: round(f(por[("inerte", s)]), 4) for s in semillas if ("inerte", s) in por},
                       "diferencias": dif, "p_una_cola": permutacion_pareada(dif)}
    out["extinciones"] = {c: sum(r["extinta_en"] is not None for r in res if r["condicion"] == c)
                          for c in CONDICIONES}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=int, default=100_000)
    ap.add_argument("--semillas", type=int, nargs="+", default=[1, 2, 3, 4])
    ap.add_argument("--condiciones", nargs="+", default=list(CONDICIONES))
    ap.add_argument("--procesos", type=int, default=6)
    ap.add_argument("--salida", default="runs/fase13/piloto.json")
    ap.add_argument("--set", action="append", default=[], metavar="seccion.clave=valor")
    args = ap.parse_args()
    tareas = [(c, s, args.pasos, tuple(args.set)) for c in args.condiciones for s in args.semillas]
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    parcial = salida.with_suffix(".parcial.json")
    # cada corrida se guarda al terminar: un corte (luz, cierre de la app) no borra las que ya terminaron
    hechas = json.loads(parcial.read_text(encoding="utf-8")) if parcial.exists() else []
    listas = {(r["condicion"], r["semilla"]) for r in hechas}
    res = list(hechas)
    with Pool(args.procesos) as pool:
        for r in pool.imap_unordered(correr, [t for t in tareas if (t[0], t[1]) not in listas]):
            res.append(r)
            parcial.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
            print("terminada", r["condicion"], r["semilla"], flush=True)
    for r in sorted(res, key=lambda r: (r["condicion"], r["semilla"])):
        print(r["condicion"], r["semilla"], "extinta" if r["extinta_en"] else "viva", r["serie"][-1] if r["serie"] else {})
    ev = evaluar(res, args.pasos - args.pasos // 3)
    print(json.dumps(ev, indent=2, ensure_ascii=False))
    salida.write_text(json.dumps({"config": vars(args), "evaluacion": ev, "corridas": res}, ensure_ascii=False),
                      encoding="utf-8")


if __name__ == "__main__":
    main()
