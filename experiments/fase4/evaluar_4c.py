"""Fase 4c: sesgo reproductivo frente a un modelo nulo, control de costo privado y réplica con semillas nuevas.

Parte 1 (nulo-4a): las 10 poblaciones finales de la fase 4a (`--fase4 runs/fase4`; sin, r20, r20a) corren sin
mutación en un ambiente común sin restricción. En cada medición, para cada grupo de 3 o más (miembros con edad
≥ 100), se compara el número observado de miembros que nunca se dividieron con el esperado si las divisiones del
grupo se repartieran con la misma tasa para todos (multinomial con pesos proporcionales a la edad):
    E[nunca] = Σ_i (1 − edad_i / Σ edad)^D, con D = divisiones del grupo.
El cociente observado/esperado (por tamaño de grupo y total) mide si la reproducción está más concentrada de lo que
daría el azar. También se compara la tasa de avanzar de quienes nunca se dividieron con la de quienes sí
(complementariedad).

Parte 2 (réplica): semillas nuevas (111–120), mismos ancestros en dos etapas que la fase 4a, condiciones sin, r20,
r20a y dos controles de costo privado de dividirse sin inmovilidad (c6, c12: costo de división 6 y 12, contra 2).
Al final, el mismo análisis nulo sobre sus poblaciones.

Uso:
    python experiments/fase4/evaluar_4c.py --fase4 runs/fase4 --salida runs/fase4c [--procesos 8]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, persistencia
from simbio import dispositivo as dev
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("evaluar_fase4", RAIZ / "experiments" / "fase4" / "evaluar.py")
fase4 = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase4"] = fase4
_spec.loader.exec_module(fase4)

SEMILLAS_4A = list(range(101, 111))
SEMILLAS_REPLICA = list(range(111, 121))
ORIGENES_4A = ["sin", "r20", "r20a"]
CONDICIONES_REPLICA = ["sin", "r20", "r20a", "c6", "c12"]
PASOS_NULO, DESDE_NULO = 8000, 2000


class Nulo:
    def __init__(self):
        self.obs = defaultdict(float)
        self.esp = defaultdict(float)
        self.avance = {"nunca": [0.0, 0.0], "si": [0.0, 0.0]}  # [avances, edad]

    def __call__(self, sim):
        if sim.t < DESDE_NULO or sim.t % 200:
            return
        p = sim.pob
        lab, _, _ = sim.grupos()
        lab = dev.a_cpu(lab)
        tam = np.bincount(lab, minlength=p.n)[lab]
        edad = (sim.t - dev.a_cpu(p["nacimiento"])).astype(float)
        nd = dev.a_cpu(p["n_divisiones"]).astype(float)
        na = dev.a_cpu(p["n_avances"]).astype(float)
        ok = (tam >= 3) & (edad >= 100)
        for g in np.unique(lab[ok]):
            m = ok & (lab == g)
            n = int(m.sum())
            if n < 3:
                continue
            clase = str(min(n, 5))
            D = nd[m].sum()
            w = edad[m] / edad[m].sum()
            for c in (clase, "total"):
                self.obs[c] += float((nd[m] == 0).sum())
                self.esp[c] += float(((1.0 - w) ** D).sum())
        for nombre, m in (("nunca", ok & (nd == 0)), ("si", ok & (nd > 0))):
            self.avance[nombre][0] += float(na[m].sum())
            self.avance[nombre][1] += float(edad[m].sum())

    def resumen(self):
        out = {f"cociente_{c}": (self.obs[c] / self.esp[c] if self.esp[c] >= 5 else float("nan")) for c in self.esp}
        out["obs_total"], out["esp_total"] = self.obs["total"], self.esp["total"]
        for k, (a, e) in self.avance.items():
            out[f"tasa_avanzar_{k}"] = a / e if e > 0 else float("nan")
        return out


def _nulo(tarea):
    ruta, etiqueta, semilla = tarea
    g = persistencia.cargar_genomas(Path(ruta))
    res = {"origen": etiqueta, "semilla": semilla}
    if len(g["mu"]) == 0:
        return {**res, "extinta": True}
    idx = np.random.default_rng(semilla).integers(0, len(g["mu"]), 600)
    cfg = config.cargar(fase4.CONFIG, fase4.MODELO + ["herencia.mutacion=false", "sim.registrar_cada=1000"])
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg, {k: v[idx] for k, v in g.items()})
    obs = Nulo()
    sim.correr(PASOS_NULO, al_paso=obs)
    return {**res, "extinta": sim.pob.n == 0, **obs.resumen()}


def hipotesis(nulo_4a, nulo_rep, replica):
    """Reglas prerregistradas (docs/bitacora/2026-10-25-fase4c-prerregistro.md)."""
    def pares(rs, a, b, m):
        va = {r["semilla"]: r.get(m, np.nan) for r in rs if r["origen"] == a and not r["extinta"]}
        vb = {r["semilla"]: r.get(m, np.nan) for r in rs if r["origen"] == b and not r["extinta"]}
        comunes = sorted(s for s in set(va) & set(vb) if va[s] == va[s] and vb[s] == vb[s])
        return [va[s] for s in comunes], [vb[s] for s in comunes]

    def prueba(rs, a, b, m):
        x, y = pares(rs, a, b, m)
        d = [i - j for i, j in zip(x, y)]
        p = fase4.permutacion_pareada(d)
        return {"n": len(d), "media_a": round(float(np.mean(x)), 3) if d else None,
                "media_b": round(float(np.mean(y)), 3) if d else None, "p_una_cola": round(p, 4),
                "cumple": bool(d) and p < 0.05}

    h = {}
    for etiqueta, rs in (("4a", nulo_4a), ("replica", nulo_rep)):
        for b in ("sin", "r20a"):
            h[f"N1_cociente_{etiqueta}_r20_vs_{b}"] = prueba(rs, "r20", b, "cociente_total")
        x, y = pares(rs, "r20", "r20", "tasa_avanzar_nunca")[0], pares(rs, "r20", "r20", "tasa_avanzar_si")[0]
        d = [i - j for i, j in zip(x, y)]
        h[f"N2_complementariedad_{etiqueta}_r20"] = {"n": len(d), "media_dif": round(float(np.mean(d)), 4) if d else None,
                                                    "p_una_cola": round(fase4.permutacion_pareada(d), 4)}
        if etiqueta == "replica":
            for c in ("c6", "c12"):
                h[f"N3_cociente_replica_r20_vs_{c}"] = prueba(rs, "r20", c, "cociente_total")
                h[f"N4_cociente_replica_{c}_vs_sin"] = prueba(rs, c, "sin", "cociente_total")
    rep = [{"origen": r["nombre"], **r} for r in replica]
    for b in ("r20a", "sin", "c6", "c12"):
        h[f"R1_grupos_replica_r20_vs_{b}"] = prueba(rep, "r20", b, "grupos_de_3_o_mas")
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase4", type=Path, default=RAIZ / "runs" / "fase4")
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase4c")
    ap.add_argument("--procesos", type=int, default=4)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    faltan = [(o, s) for o in ORIGENES_4A for s in SEMILLAS_4A
              if not (args.fase4 / "fase4" / o / f"semilla_{s}" / "poblacion.npz").exists()]
    if faltan:
        sys.exit(f"faltan poblaciones de la fase 4a en {args.fase4}: {faltan[:5]}...")
    t0 = time.time()
    sal = str(args.salida)
    with Pool(args.procesos) as pool:
        nulo_4a = pool.map(_nulo, [(str(args.fase4 / "fase4" / o / f"semilla_{s}" / "poblacion.npz"), o, s)
                                   for o in ORIGENES_4A for s in SEMILLAS_4A])
        ancestros = pool.map(fase4._ancestro, [(sal, s) for s in SEMILLAS_REPLICA])
        replica = pool.map(fase4._correr, [(sal, n, s, 60000) for n in CONDICIONES_REPLICA for s in SEMILLAS_REPLICA])
        nulo_rep = pool.map(_nulo, [(str(args.salida / "fase4" / n / f"semilla_{s}" / "poblacion.npz"), n, s)
                                    for n in CONDICIONES_REPLICA for s in SEMILLAS_REPLICA])
    informe = {"parametros": {"minutos": round((time.time() - t0) / 60, 1)}, "ancestros": ancestros,
               "hipotesis": hipotesis(nulo_4a, nulo_rep, replica),
               "nulo_4a": nulo_4a, "nulo_replica": nulo_rep, "replica": replica}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["hipotesis"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
