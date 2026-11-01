"""Fase 14, un cerebro antes que un cuerpo: ¿evolucionan los ojos? ¿Hacen que el cerebro (la red interna) se use?

Universo natural (natural.toml, con la red regulatoria como cerebro de cada organismo). Condiciones:
    vision:  el genoma puede tener ojos (alcance heredable, LUCA = 0) y paga por ellos
    cegada:  los ojos existen, mutan y cuestan igual, pero no informan (control: ¿la información vale lo que cuesta?)
    ciega:   sin ojos (el mundo de la fase 13)
Al terminar, prueba de lesión (como en neurociencia): la población final se copia y se sigue en paralelo, con el mismo
azar, intacta y lesionada. La lesión del cerebro hace que los genes dejen de leer la red (desarrollo.inerte); la de
los ojos los ciega sin quitarles el costo (vision.cegar). costo_lesion = (intacta − lesionada) / intacta, en
población media de los últimos pasos. > 0: la parte lesionada se usaba.
Preregistro: docs/bitacora/2026-11-01-fase14-ojos-prerregistro.md

Uso (en Docker): docker compose --profile experimentos run -d --name fase14-ojos experimento \
    experiments/fase14/ojos.py --pasos 300000 --procesos 4
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fase13"))
from piloto import RAIZ, permutacion_pareada  # noqa: E402

from simbio import config  # noqa: E402
from simbio.simulacion import Simulacion  # noqa: E402

BASE = ["sim.registrar_cada=1000"]
CONDICIONES = {"vision": ["vision.activa=true"], "cegada": ["vision.activa=true", "vision.cegar=true"],
               "ciega": []}
CLAVES = ["poblacion", "generacion_media", "alcance_medio", "frac_con_ojos", "con_gen_regulado",
          "peso_regulador_medio", "reg_medio_abs", "frac_enlazados", "frac_depredadores", "usa_atacar",
          "eta_media", "tasa_efectiva_media"]
PASOS_LESION = 20_000


def seguir(sim, pasos):
    pob = []
    for t in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            pob += [0] * (pasos - t - 1)
            break
        pob.append(sim.pob.n)
    return float(np.mean(pob[-pasos // 4:])) if pob else 0.0


def lesion(sim, ajuste):
    """Copia la simulación (mismo azar), aplica la lesión a una copia y sigue las dos en paralelo."""
    memo = {id(sim.xp): sim.xp}
    intacta, lesionada = copy.deepcopy(sim, memo), copy.deepcopy(sim, dict(memo))
    lesionada.cfg = copy.deepcopy(sim.cfg)
    ajuste(lesionada.cfg)
    a, b = seguir(intacta, PASOS_LESION), seguir(lesionada, PASOS_LESION)
    return round((a - b) / a, 5) if a > 0 else float("nan")


def correr(tarea):
    nombre, semilla, pasos = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/natural.toml", [*BASE, *CONDICIONES[nombre]])
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg)
    for _ in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            break
    serie = [{"t": f["t"], **{c: round(float(f[c]), 5) for c in CLAVES if c in f and f[c] == f[c]}}
             for f in sim.historial]
    out = {"condicion": nombre, "semilla": semilla, "extinta_en": sim.t if sim.pob.n == 0 else None, "serie": serie}
    if sim.pob.n:
        out["lesion_cerebro"] = lesion(sim, lambda c: setattr(c.desarrollo, "inerte", True))
        if nombre == "vision":
            out["lesion_ojos"] = lesion(sim, lambda c: setattr(c.vision, "cegar", True))
    return out


def final(r, clave, desde):
    v = [f[clave] for f in r["serie"] if f["t"] >= desde and clave in f]
    return float(np.mean(v)) if v and r["extinta_en"] is None else float("nan")


def prueba(valores):
    v = [x for x in valores if x == x]
    return {"valores": valores, "positivas": sum(x > 0 for x in v), "con_dato": len(v),
            "p_una_cola": permutacion_pareada(v) if len(v) >= 6 else float("nan")}


def evaluar(res, desde):
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({r["semilla"] for r in res})

    def v(c, f):
        return {s: f(por[(c, s)]) for s in semillas if (c, s) in por}

    val = {c: {**{k: v(c, lambda r, k=k: round(final(r, k, desde), 5)) for k in CLAVES},
               "lesion_cerebro": v(c, lambda r: r.get("lesion_cerebro", float("nan"))),
               "lesion_ojos": v(c, lambda r: r.get("lesion_ojos", float("nan")))} for c in CONDICIONES}

    def dif(k, a, b):
        return [round(val[a][k][s] - val[b][k][s], 5) for s in semillas if s in val[a][k] and s in val[b][k]]

    return {"valores": val,
            "V1_ojos_vision_menos_cegada": prueba(dif("alcance_medio", "vision", "cegada")),
            "V2_ojos_usados": prueba(list(val["vision"]["lesion_ojos"].values())),
            "V3_cerebro_vision_menos_ciega": prueba(dif("lesion_cerebro", "vision", "ciega")),
            "exploratorias": {"lesion_cerebro_vision": prueba(list(val["vision"]["lesion_cerebro"].values())),
                              "lesion_cerebro_ciega": prueba(list(val["ciega"]["lesion_cerebro"].values())),
                              "poblacion_vision_menos_ciega": prueba(dif("poblacion", "vision", "ciega"))},
            "extinciones": {c: sum(r["extinta_en"] is not None for r in res if r["condicion"] == c)
                            for c in CONDICIONES}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=int, default=300_000)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(49, 59)))
    ap.add_argument("--condiciones", nargs="+", default=list(CONDICIONES))
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--salida", default="runs/fase14/ojos.json")
    args = ap.parse_args()
    tareas = [(c, s, args.pasos) for c in args.condiciones for s in args.semillas]
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    parcial = salida.with_suffix(".parcial.json")
    res = json.loads(parcial.read_text(encoding="utf-8")) if parcial.exists() else []
    listas = {(r["condicion"], r["semilla"]) for r in res}
    with Pool(args.procesos) as pool:
        for r in pool.imap_unordered(correr, [t for t in tareas if (t[0], t[1]) not in listas]):
            res.append(r)
            parcial.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
            print("terminada", r["condicion"], r["semilla"], flush=True)
    ev = evaluar(res, args.pasos - args.pasos // 3)
    print(json.dumps(ev, indent=2, ensure_ascii=False))
    salida.write_text(json.dumps({"config": vars(args), "evaluacion": ev, "corridas": res}, ensure_ascii=False),
                      encoding="utf-8")


if __name__ == "__main__":
    main()
