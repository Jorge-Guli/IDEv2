"""Fase 13: ¿el cuerpo responde cuando atacan a una de sus células? ¿Los cuerpos se parten en pedazos?

Pregunta del autor (2026-10-31): la célula atacada, ¿avisa al resto? ¿El cuerpo se defiende, se sacrifica la parte o
la reconstruye? No se agrega física: se mide si el genoma actual ya responde (señal por contacto, compartir energía,
soltarse). Condiciones (universo natural):
    red:    la red regulatoria existe y los genes la leen
    inerte: la red existe pero los genes no la leen (la señal por contacto no puede guiar ninguna acción)
Regla de datos (aprendida del peldaño 3): una semilla cuenta solo si la medida existe en al menos 30 de las 100
mediciones del último tercio.
Preregistro: docs/bitacora/2026-10-31-fase13-respuesta-ataque-prerregistro.md

Uso (en Docker): docker compose --profile experimentos run -d --name fase13-respuesta experimento \
    experiments/fase13/respuesta.py --pasos 300000 --procesos 4
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from piloto import RAIZ, correr, permutacion_pareada

MEDIDAS = ["ayuda_herida", "senal_herida", "senal_vecinas", "soltarse_herida", "frac_heridas",
           "frac_pedazos_fragmentados", "fundadores_partidos", "frac_enlazados", "poblacion", "frac_depredadores",
           "con_gen_regulado"]
MIN_FILAS = 30


def final(r, clave, desde):
    """Media en el último tercio, o NaN si la medida existe en menos de MIN_FILAS mediciones o la corrida se extinguió."""
    v = [f[clave] for f in r["serie"] if f["t"] >= desde and clave in f]
    return float(np.mean(v)) if len(v) >= MIN_FILAS and r["extinta_en"] is None else float("nan")


def prueba(valores):
    v = [x for x in valores if x == x]
    return {"valores": valores, "con_dato": len(v), "positivas": sum(x > 0 for x in v),
            "p_una_cola": permutacion_pareada(v) if len(v) >= 6 else float("nan")}


def evaluar(res, desde):
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({r["semilla"] for r in res})
    val = {c: {m: {s: round(final(por[(c, s)], m, desde), 5) for s in semillas if (c, s) in por} for m in MEDIDAS}
           for c in ("red", "inerte")}

    def dif(m):
        return [round(val["red"][m][s] - val["inerte"][m][s], 5) for s in semillas
                if s in val["red"][m] and s in val["inerte"][m]]

    return {"valores": val,
            "R1_ayuda_red": prueba(list(val["red"]["ayuda_herida"].values())),
            "R2_aviso_red_menos_inerte": prueba(dif("senal_vecinas")),
            "exploratorias": {"senal_herida_red_menos_inerte": prueba(dif("senal_herida")),
                              "senal_vecinas_red": prueba(list(val["red"]["senal_vecinas"].values())),
                              "soltarse_herida_red": prueba(list(val["red"]["soltarse_herida"].values())),
                              "ayuda_herida_red_menos_inerte": prueba(dif("ayuda_herida"))},
            "extinciones": {c: sum(r["extinta_en"] is not None for r in res if r["condicion"] == c)
                            for c in ("red", "inerte")}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=int, default=300_000)
    ap.add_argument("--semillas", type=int, nargs="+", default=list(range(39, 49)))
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--salida", default="runs/fase13/respuesta.json")
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
