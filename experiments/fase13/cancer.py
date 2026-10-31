"""Fase 13: ¿la evolución suprime el "cáncer"? (observación del autor, 2026-10-31)

Atacar a una hermana del propio cuerpo es como un cáncer: una célula gana energía a costa del cuerpo. Si el cuerpo
empieza a ser una unidad de la evolución, las células deberían atacar a sus hermanas menos de lo que lo harían a
ciegas. supresion_cancer = frac_frente_hermana (ataques internos esperados a ciegas) − frac_ataques_intragrupo.
Condiciones (universo natural):
    red:       el universo tal cual: atacar a una hermana le quita energía (cáncer posible)
    sin_intra: control: los ataques a hermanas no tienen efecto (no hay cáncer que suprimir)
Prerregistro: docs/bitacora/2026-10-31-fase13-cancer-prerregistro.md

Uso (en Docker): docker compose --profile experimentos run -d --name fase13-cancer experimento \
    experiments/fase13/cancer.py --pasos 300000 --procesos 4
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

from piloto import RAIZ, correr, final, permutacion_pareada

MEDIDAS = ["supresion_cancer", "frac_frente_hermana", "frac_ataques_intragrupo", "frac_enlazados", "poblacion",
           "frac_depredadores", "usa_atacar", "parentesco_relativo"]


def evaluar(res, desde):
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({r["semilla"] for r in res})
    val = {c: {m: {s: round(final(por[(c, s)], m, desde), 4) for s in semillas if (c, s) in por} for m in MEDIDAS}
           for c in ("red", "sin_intra")}
    sup = [v for v in val["red"]["supresion_cancer"].values() if v == v]
    dif = [round(val["red"]["supresion_cancer"][s] - val["sin_intra"]["supresion_cancer"][s], 5)
           for s in semillas if s in val["red"]["supresion_cancer"] and s in val["sin_intra"]["supresion_cancer"]]
    return {"valores": val,
            "C1_supresion_red": {"valores": sup, "positivas": sum(v > 0 for v in sup),
                                 "p_una_cola": permutacion_pareada(sup)},
            "C2_red_menos_sin_intra": {"diferencias": dif, "p_una_cola": permutacion_pareada(dif)},
            "extinciones": {c: sum(r["extinta_en"] is not None for r in res if r["condicion"] == c)
                            for c in ("red", "sin_intra")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=int, default=300_000)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(29, 39)))
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--salida", default="runs/fase13/cancer.json")
    args = ap.parse_args()
    tareas = [(c, s, args.pasos, ()) for c in ("red", "sin_intra") for s in args.semillas]
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
