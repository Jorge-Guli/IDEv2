"""Fase 13, peldaño 3: ¿los cuerpos se reproducen como unidad, con una línea germinal?

Antes de agregar mecanismos se mide si el genoma actual ya lo logra. Un cuerpo puede fundar otro con un propágulo
(un hijo que nace suelto, con dividirse) y crecer con dividirse unido. Hay línea germinal si pocas células de cada
cuerpo hacen los propágulos, más de lo que daría el azar (exceso_germinal > 0). Condiciones (universo natural):
    red:    la red regulatoria existe y los genes la leen
    inerte: la red existe pero los genes no la leen
Preregistro: docs/bitacora/2026-10-31-fase13-linea-germinal-prerregistro.md

Uso (en Docker): docker compose --profile experimentos run -d --name fase13-germinal experimento \
    experiments/fase13/germinal.py --pasos 300000 --semillas 19 20 21 22 23 24 25 26 27 28 --procesos 4
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

from piloto import RAIZ, correr, final, permutacion_pareada

MEDIDAS = ["exceso_germinal", "concentracion_propagulos", "concentracion_propagulos_azar",
           "concentracion_propagulos_lugar", "frac_sin_propagulos",
           "frac_propagulos_de_cuerpo", "frac_enlazados", "poblacion", "frac_depredadores", "parentesco_relativo", "eta_media",
           "frac_ataques_intragrupo", "frac_frente_hermana", "supresion_cancer"]


def evaluar(res, desde):
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({r["semilla"] for r in res})
    val = {c: {m: {s: round(final(por[(c, s)], m, desde), 4) for s in semillas if (c, s) in por} for m in MEDIDAS}
           for c in ("red", "inerte")}
    ex = [v for v in val["red"]["exceso_germinal"].values() if v == v]
    dif = [round(val["red"]["exceso_germinal"][s] - val["inerte"]["exceso_germinal"][s], 5)
           for s in semillas if s in val["red"]["exceso_germinal"] and s in val["inerte"]["exceso_germinal"]]
    return {"valores": val,
            "G1_exceso_red": {"valores": ex, "positivas": sum(v > 0 for v in ex), "p_una_cola": permutacion_pareada(ex)},
            "G2_red_menos_inerte": {"diferencias": dif, "p_una_cola": permutacion_pareada(dif)},
            "extinciones": {c: sum(r["extinta_en"] is not None for r in res if r["condicion"] == c)
                            for c in ("red", "inerte")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=int, default=300_000)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(19, 29)))
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--salida", default="runs/fase13/germinal.json")
    args = ap.parse_args()
    tareas = [(c, s, args.pasos, ()) for c in ("red", "inerte") for s in args.semillas]
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
