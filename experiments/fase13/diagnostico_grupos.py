"""Fase 13, diagnóstico (sin prerregistro): ¿por qué desaparecen los grupos en el universo natural?

Corre natural.toml y cuenta, cada 1 000 pasos:
    - a quién se ataca: a un socio enlazado, a un pariente suelto (etiqueta parecida) o a un extraño
    - cuántos enlaces nacen por dividirse unido y cuántos por unirse
    - energía y muertes (por ataque) de enlazados y sueltos
No cambia la simulación: solo observa (subclase que cuenta antes de llamar al ataque original).

Uso (desde la raíz):  python experiments/fase13/diagnostico_grupos.py --pasos 30000 --semillas 1 2
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, dispositivo as dev
from simbio import genoma as gen
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]


class Observada(Simulacion):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.obs = {"ataque_socio": 0, "ataque_pariente": 0, "ataque_extrano": 0,
                    "muertes_enlazados": 0, "muertes_sueltos": 0}

    def _atacar(self, act, occ, socios):
        xp, p = self.xp, self.pob
        H, W = self.entorno.alto, self.entorno.ancho
        i = xp.flatnonzero(act == gen.ATACAR)
        if i.size:
            d = p["dir"][i].astype(xp.int64)
            j = occ[(p["y"][i] + self.DY[d]) % H, (p["x"][i] + self.DX[d]) % W]
            hay = (j >= 0) & (j != i)
            i, j = i[hay], j[hay]
            socio = (socios[i] == j[:, None]).any(axis=1)
            dist = xp.abs(p["etiqueta"][i] - p["etiqueta"][j]).sum(axis=1)
            pariente = ~socio & (dist < 0.1)
            self.obs["ataque_socio"] += int(socio.sum())
            self.obs["ataque_pariente"] += int(pariente.sum())
            self.obs["ataque_extrano"] += int((~socio & ~pariente).sum())
        enl = (socios >= 0).any(axis=1)
        muertos = super()._atacar(act, occ, socios)
        if muertos is not None:
            self.obs["muertes_enlazados"] += int((muertos & enl).sum())
            self.obs["muertes_sueltos"] += int((muertos & ~enl).sum())
        return muertos


def correr(tarea):
    semilla, pasos, ajustes = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/natural.toml", ["sim.registrar_cada=1000", *ajustes])
    cfg.sim.semilla = semilla
    sim = Observada(cfg)
    filas = []
    for t in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            break
        if sim.t % 1000 == 0:
            p = sim.pob
            occ = sim.ocupacion()
            enl = dev.a_cpu((sim.vecinos_enlazados(occ) >= 0).any(axis=1))
            E = dev.a_cpu(p["E"])
            f = sim.historial[-1]
            filas.append({"t": sim.t, "n": p.n, "frac_enlazados": round(float(enl.mean()), 4),
                          "E_enlazados": round(float(E[enl].mean()), 2) if enl.any() else None,
                          "E_sueltos": round(float(E[~enl].mean()), 2) if (~enl).any() else None,
                          "enlaces_por_division": f.get("enlaces_por_division"),
                          "enlaces_por_union": f.get("enlaces_por_union"),
                          **sim.obs})
            sim.obs = dict.fromkeys(sim.obs, 0)
    return {"semilla": semilla, "filas": filas}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=int, default=30_000)
    ap.add_argument("--semillas", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--procesos", type=int, default=6)
    ap.add_argument("--salida", default="runs/fase13/diagnostico_grupos.json")
    ap.add_argument("--set", action="append", default=[], metavar="seccion.clave=valor")
    args = ap.parse_args()
    with Pool(min(args.procesos, len(args.semillas))) as pool:
        res = pool.map(correr, [(s, args.pasos, tuple(args.set)) for s in args.semillas])
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    for r in res:
        print("semilla", r["semilla"])
        for f in r["filas"][:: max(1, len(r["filas"]) // 15)]:
            print(" ", f)


if __name__ == "__main__":
    main()
