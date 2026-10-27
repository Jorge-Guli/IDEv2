"""Fase 12, etapa 4: ¿la depredación evolucionada mantiene viva la innovación? Exploratorio, desde LUCA puro.

Mundo de vivo.toml (fase 11), con mutación. Condiciones:
    ataque:  la primitiva atacar existe; si se usa, lo decide la evolución
    fijo:    el depredador fijo de la fase 2c (no evoluciona; refugio por tamaño de grupo)
    sin:     sin depredación (el universo vivo de la etapa 1)
La hipótesis de la Reina Roja: con un ambiente que evoluciona, la tasa de mutación no colapsa y la diversidad de
genomas se mantiene. Se reportan series cada 20 000 pasos y extinciones.

Uso (desde la raíz):  python experiments/fase12/reina_roja.py --pasos 200000 --semillas 1 2
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
    "ataque": ["ataque.activo=true"],
    "fijo": ["depredacion.activa=true", "depredacion.rampa=20000"],
    "sin": [],
}
CLAVES = ["poblacion", "generacion_media", "tasa_efectiva_media", "mu_media", "perfiles_distintos", "genes_medios",
          "tiene_atacar", "usa_atacar", "muertes_por_ataque", "frac_enlazados", "grupos_de_3_o_mas",
          "acierto_comida", "tiene_memoria_a"]


def correr(tarea):
    nombre, semilla, pasos, ajustes = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/vivo.toml",
                        CONDICIONES[nombre] + ["sim.registrar_cada=1000"] + list(ajustes))
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg)
    for _ in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            break
    serie = []
    for k in range(20, len(sim.historial) + 1, 20):  # promedio de cada bloque de 20 mediciones
        bloque = sim.historial[k - 20:k]
        fila = {"t": bloque[-1]["t"]}
        for c in CLAVES:
            v = [f[c] for f in bloque if c in f and f[c] == f[c]]
            if v:
                fila[c] = round(float(np.mean(v)), 5)
        serie.append(fila)
    return {"condicion": nombre, "semilla": semilla, "ajustes": list(ajustes),
            "extinta_en": sim.t if sim.pob.n == 0 else None, "serie": serie}


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--pasos", type=int, default=200_000)
    a.add_argument("--semillas", type=int, nargs="+", default=[1, 2])
    a.add_argument("--condiciones", nargs="+", default=list(CONDICIONES))
    a.add_argument("--set", action="append", default=[])
    a.add_argument("--procesos", type=int, default=6)
    a.add_argument("--salida", default="runs/fase12/reina_roja.json")
    args = a.parse_args()
    tareas = [(c, s, args.pasos, tuple(args.set)) for c in args.condiciones for s in args.semillas]
    with Pool(args.procesos) as pool:
        res = pool.map(correr, tareas)
    for r in res:
        f = r["serie"][-1] if r["serie"] else {}
        print(r["condicion"], r["semilla"], "extinta" if r["extinta_en"] else "viva",
              {k: f.get(k) for k in ("poblacion", "generacion_media", "tasa_efectiva_media", "perfiles_distintos",
                                     "tiene_atacar", "usa_atacar", "frac_enlazados")})
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
