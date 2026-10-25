"""Fase 4b: jardín común. ¿La especialización de la fase 4a está en los genomas o es mecánica?

Toma las poblaciones finales de la fase 4a (`--fase4 runs/fase4`: evolucionadas sin restricción, con r20 y con el
control r20a) y corre cada una, sin mutación, en dos ambientes comunes: sin restricción y con r20. Si los genomas
evolucionados con la restricción muestran más especialización que los otros **en el mismo ambiente**, la diferencia
es heredada y no un efecto directo de la regla.

Uso:
    python experiments/fase4/jardin_comun.py --fase4 runs/fase4 --salida runs/fase4b [--procesos 8]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
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

ORIGENES = ["sin", "r20", "r20a"]
AMBIENTES = {"amb_sin": [], "amb_r20": ["fisica.refractario_division=20"]}
SEMILLAS = list(range(101, 111))
PASOS, CALENTAMIENTO = 15000, 3000


class Posicion:
    """Fracción de miembros de grupos ≥ 3 (edad ≥ 100) que nunca se dividieron, según su número de socios
    (borde: 1; interior: 2 o más), para separar la especialización de la posición."""

    def __init__(self):
        self.cuenta = {"borde": [0, 0], "interior": [0, 0]}

    def __call__(self, sim):
        if sim.t < CALENTAMIENTO or sim.t % 200:
            return
        p = sim.pob
        lab, _, _ = sim.grupos()
        lab = dev.a_cpu(lab)
        tam = np.bincount(lab, minlength=p.n)[lab]
        edad = sim.t - dev.a_cpu(p["nacimiento"])
        nsoc = dev.a_cpu((p["socio"] >= 0).sum(axis=1))
        nunca = dev.a_cpu(p["n_divisiones"]) == 0
        ok = (tam >= 3) & (edad >= 100)
        for nombre, m in (("borde", ok & (nsoc == 1)), ("interior", ok & (nsoc >= 2))):
            self.cuenta[nombre][0] += int((nunca & m).sum())
            self.cuenta[nombre][1] += int(m.sum())


def _correr(tarea):
    fase4_dir, origen, ambiente, semilla = tarea
    g = persistencia.cargar_genomas(Path(fase4_dir) / "fase4" / origen / f"semilla_{semilla}" / "poblacion.npz")
    res = {"origen": origen, "ambiente": ambiente, "semilla": semilla}
    if len(g["mu"]) == 0:
        return {**res, "extinta": True}
    idx = np.random.default_rng(semilla).integers(0, len(g["mu"]), 600)
    cfg = config.cargar(fase4.CONFIG, fase4.MODELO + AMBIENTES[ambiente] +
                        ["herencia.mutacion=false", "sim.registrar_cada=200"])
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg, {k: v[idx] for k, v in g.items()})
    obs = Posicion()
    sim.correr(PASOS, al_paso=obs)
    ultimo = [r for r in sim.historial if r["t"] >= CALENTAMIENTO]
    res["extinta"] = sim.pob.n == 0
    for m in fase4.METRICAS:
        v = np.array([r.get(m, np.nan) for r in ultimo], dtype=float)
        res[m] = float(np.nanmean(v)) if v.size and not np.isnan(v).all() else float("nan")
    for nombre, (a, b) in obs.cuenta.items():
        res[f"nunca_dividio_{nombre}"] = a / b if b >= 50 else float("nan")
    return res


def hipotesis(rs):
    """Reglas prerregistradas (docs/bitacora/2026-10-25-fase4b-prerregistro.md)."""
    def val(origen, ambiente, m):
        return {r["semilla"]: r[m] for r in rs if r["origen"] == origen and r["ambiente"] == ambiente
                and not r["extinta"] and r[m] == r[m]}

    def prueba(m, a, b, ambiente, signo=1):
        va, vb = val(a, ambiente, m), val(b, ambiente, m)
        comunes = sorted(set(va) & set(vb))
        d = [signo * (va[s] - vb[s]) for s in comunes]
        p = fase4.permutacion_pareada(d)
        return {"n": len(d), "media_a": round(float(np.mean([va[s] for s in comunes])), 3) if d else None,
                "media_b": round(float(np.mean([vb[s] for s in comunes])), 3) if d else None,
                "p_una_cola": round(p, 4), "cumple": p < 0.05}

    h = {}
    for amb in AMBIENTES:
        for b in ("sin", "r20a"):
            h[f"G1_corr_{amb}_r20_vs_{b}"] = prueba("corr_avanzar_dividir", "r20", b, amb, signo=-1)
            h[f"G2_nunca_{amb}_r20_vs_{b}"] = prueba("frac_nunca_dividio", "r20", b, amb)
            h[f"G3_nunca_borde_{amb}_r20_vs_{b}"] = prueba("nunca_dividio_borde", "r20", b, amb)
            h[f"G4_grupos_{amb}_r20_vs_{b}"] = prueba("grupos_de_3_o_mas", "r20", b, amb)
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase4", type=Path, default=RAIZ / "runs" / "fase4")
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase4b")
    ap.add_argument("--procesos", type=int, default=4)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    faltan = [(o, s) for o in ORIGENES for s in SEMILLAS
              if not (args.fase4 / "fase4" / o / f"semilla_{s}" / "poblacion.npz").exists()]
    if faltan:
        sys.exit(f"faltan poblaciones de la fase 4a en {args.fase4}: {faltan[:5]}...")
    t0 = time.time()
    with Pool(args.procesos) as pool:
        rs = pool.map(_correr, [(str(args.fase4), o, a, s) for o in ORIGENES for a in AMBIENTES for s in SEMILLAS])
    informe = {"parametros": {"pasos": PASOS, "semillas": SEMILLAS, "minutos": round((time.time() - t0) / 60, 1)},
               "hipotesis": hipotesis(rs), "corridas": rs}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["hipotesis"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
