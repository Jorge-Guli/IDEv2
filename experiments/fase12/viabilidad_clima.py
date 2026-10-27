"""Fase 12, etapa 2: ¿LUCA es viable con el clima real? Corre LUCA puro en el mundo de clima.toml y en sus
controles, varias semillas, y resume población, extinciones, acierto de comida y genes que leen la presión.

Uso (desde la raíz del repo):
    python experiments/fase12/viabilidad_clima.py --pasos 200000 --semillas 1 2 --procesos 8
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
CONDICIONES = {
    "clima": [],
    "dias_barajados": ["realidad.barajar_dias=true"],
    "presion_desacoplada": ["realidad.presion_desacoplada=true"],
    "sin_clima": ["realidad.activa=false"],  # el universo vivo de la etapa 1 (estaciones artificiales)
}


def correr(args):
    nombre, semilla, pasos, ajustes = args
    cfg = config.cargar(RAIZ / "experiments/configs/clima.toml",
                        CONDICIONES[nombre] + ["sim.registrar_cada=2000"] + list(ajustes))
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg)
    extinta_en = None
    for _ in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            extinta_en = sim.t
            break
    h = sim.historial
    ult = h[-10:]  # las últimas mediciones (20 000 pasos)

    def media(k):
        v = [f[k] for f in ult if k in f and f[k] == f[k]]
        return float(np.mean(v)) if v else float("nan")

    return {"condicion": nombre, "ajustes": list(ajustes), "semilla": semilla, "pasos": sim.t, "extinta_en": extinta_en,
            "poblacion_min": int(min(f["poblacion"] for f in h)), "poblacion_final": media("poblacion"),
            "acierto": media("acierto_comida"), "generacion": media("generacion_media"),
            "con_gen_presion": media("con_gen_presion"), "con_gen_memoria": media("tiene_memoria_a"),
            "tasa_mutacion": media("tasa_efectiva_media")}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pasos", type=int, default=200_000)
    p.add_argument("--semillas", type=int, nargs="+", default=[1, 2])
    p.add_argument("--condiciones", nargs="+", default=list(CONDICIONES))
    p.add_argument("--procesos", type=int, default=8)
    p.add_argument("--set", action="append", default=[], help="ajuste para todas las condiciones (repetible)")
    p.add_argument("--variante", action="append", default=[],
                   help="lista de ajustes separados por espacios; cada variante se corre aparte (repetible)")
    p.add_argument("--salida", default="runs/fase12/viabilidad_clima.json")
    a = p.parse_args()
    variantes = [v.split() for v in a.variante] or [[]]
    tareas = [(c, s, a.pasos, tuple(a.set + v)) for v in variantes for c in a.condiciones for s in a.semillas]
    with Pool(a.procesos) as pool:
        res = pool.map(correr, tareas)
    for r in res:
        print(json.dumps(r, ensure_ascii=False))
    salida = RAIZ / a.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
