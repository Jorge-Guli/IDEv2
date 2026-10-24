"""Evaluación de la fase 3c (movimiento de grupos por fuerza): hipótesis prerregistradas y exploratorios.

Mismo diseño pareado que la fase 3 (un ancestro por semilla, 600 genomas sembrados en cada condición, refugio de
2 a 3), cruzando la regla de movimiento (empuje con umbral, como hasta ahora, o fuerza con α = 1 y α = 0,5) con la
percepción (ninguna, rumbo y señales, o los mismos sensores barajados).

Uso:
    python experiments/fase3c/evaluar.py --salida runs/fase3c [--procesos 8] [--semillas 10] [--semilla-inicial 61]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import importlib.util

from simbio import config, corrida

RAIZ = Path(__file__).resolve().parents[2]
# el script de la fase 3 también se llama evaluar.py: se carga por ruta con otro nombre
_spec = importlib.util.spec_from_file_location("evaluar_fase3", RAIZ / "experiments" / "fase3" / "evaluar.py")
fase3 = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase3"] = fase3
_spec.loader.exec_module(fase3)  # ancestros, siembra y métricas

CONFIG = RAIZ / "experiments" / "configs" / "coordinacion.toml"
PERCEPCION = {
    "base": [],
    "ambos": ["coordinacion.rumbo=true", "coordinacion.senales=true"],
    "barajado": ["coordinacion.rumbo=true", "coordinacion.senales=true", "coordinacion.barajar=true"],
}
MOVIMIENTO = {
    "empuje": [],
    "fuerza": ['asociacion.movimiento="fuerza"', "asociacion.exponente_arrastre=1.0"],
    "fuerza05": ['asociacion.movimiento="fuerza"', "asociacion.exponente_arrastre=0.5"],
}
CONDICIONES = {f"{m}_{p}": MOVIMIENTO[m] + PERCEPCION[p] for m in MOVIMIENTO for p in PERCEPCION}
METRICAS = fase3.METRICAS


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    res = {"nombre": nombre, "semilla": semilla}
    g = fase3.siembra(salida, semilla)
    if g is None:
        return {**res, "extinta": True, "paso_extincion": 0, **{m: float("nan") for m in METRICAS}, "poblacion": 0.0,
                "pares_enlazados": 0.0}
    cfg = config.cargar(CONFIG, CONDICIONES[nombre])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}", g)
    h = sim.historial
    ultimo = [r for r in h if r["t"] >= 0.75 * pasos]
    extinta = sim.pob.n == 0
    res.update({"pasos": sim.t, "poblacion_final": sim.pob.n, "extinta": extinta,
                "paso_extincion": sim.t if extinta else None})
    for m in METRICAS:
        vals = np.array([r.get(m, np.nan) for r in ultimo], dtype=float)
        res[m] = float(np.nanmean(vals)) if vals.size and not np.all(np.isnan(vals)) else float("nan")
    # pares enlazados medios por registro (para exigir un mínimo al medir la alineación)
    res["pares_enlazados"] = float(np.mean([r.get("frac_enlazados", 0) * r.get("poblacion", 0) / 2 for r in ultimo])) \
        if ultimo else 0.0
    if extinta:
        res["poblacion"] = 0.0
    res["tamano_grupo_max_total"] = max((r.get("tamano_grupo_max", 0) for r in h), default=0)
    return res


def evaluar_hipotesis(por: dict) -> dict:
    """Reglas prerregistradas (docs/bitacora/2026-10-24-fase3c-prerregistro.md). Variable principal: fracción en
    grupos de 3 o más en el último cuarto (extinta = 0). Alineación: solo con ≥ 20 pares enlazados."""
    def val(n, m="frac_en_refugio"):
        out = {}
        for r in por.get(n, []):
            v = r.get(m, float("nan"))
            if m == "frac_en_refugio":
                out[r["semilla"]] = 0.0 if r["extinta"] or v != v else v
            elif not r["extinta"] and r.get("pares_enlazados", 0) >= 20 and v == v:
                out[r["semilla"]] = v
        return out

    def comparar(a, b, umbral, m="frac_en_refugio"):
        va, vb = val(a, m), val(b, m)
        comunes = sorted(set(va) & set(vb))
        dif = [va[s] - vb[s] for s in comunes]
        return {"semillas": comunes, "diferencias": [round(d, 3) for d in dif],
                "superan": sum(d >= umbral for d in dif), "media_dif": round(float(np.mean(dif)), 3) if dif else None,
                "cumple": bool(comunes) and sum(d >= umbral for d in dif) >= 0.7 * len(comunes)}

    h = {}
    for m in ("fuerza", "fuerza05"):
        if f"{m}_base" in por and "empuje_base" in por:
            h[f"F1_{m}_base_vs_empuje_base"] = comparar(f"{m}_base", "empuje_base", 0.2)
        if f"{m}_ambos" in por and f"{m}_barajado" in por:
            h[f"F2_{m}_ambos_vs_barajado"] = comparar(f"{m}_ambos", f"{m}_barajado", 0.1)
            h[f"F4_{m}_alineacion_ambos_vs_barajado"] = comparar(f"{m}_ambos", f"{m}_barajado", 0.2,
                                                                 "alineacion_enlazados")
            if "empuje_ambos" in por and "empuje_barajado" in por:
                fa, fb = val(f"{m}_ambos"), val(f"{m}_barajado")
                ea, eb = val("empuje_ambos"), val("empuje_barajado")
                comunes = sorted(set(fa) & set(fb) & set(ea) & set(eb))
                dd = [(fa[s] - fb[s]) - (ea[s] - eb[s]) for s in comunes]
                h[f"F3_{m}_interaccion"] = {"diferencias": [round(d, 3) for d in dd],
                                            "media": round(float(np.mean(dd)), 3) if dd else None,
                                            "cumple": bool(dd) and sum(d >= 0.1 for d in dd) >= 0.7 * len(dd)}
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase3c")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=60000)
    ap.add_argument("--semillas", type=int, default=10)
    ap.add_argument("--semilla-inicial", type=int, default=61)  # piloto: 301
    ap.add_argument("--condiciones", nargs="*", default=None)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    condiciones = args.condiciones or list(CONDICIONES)
    t0 = time.time()
    with Pool(args.procesos) as pool:
        ancestros = pool.map(fase3._ancestro, [(str(args.salida), s) for s in semillas])
        resultados = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in condiciones for s in semillas])
    por = {}
    for r in resultados:
        por.setdefault(r["nombre"], []).append(r)
    resumen = {n: {**{m: {"media": float(np.nanmean([r[m] for r in rs])),
                          "por_semilla": [round(r[m], 4) for r in rs]} for m in METRICAS},
                   "pares_enlazados": [round(r.get("pares_enlazados", 0), 1) for r in rs],
                   "extinciones": [r["paso_extincion"] for r in rs if r["extinta"]],
                   "tamano_grupo_max_total": [r.get("tamano_grupo_max_total") for r in rs]}
               for n, rs in por.items()}
    persistencia_ = {n: f"{sum(not r['extinta'] for r in rs)}/{len(rs)}" for n, rs in por.items()}
    informe = {"parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
               "ancestros": ancestros, "persistencia": persistencia_, "hipotesis": evaluar_hipotesis(por),
               "exploratorios": resumen}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ancestros": ancestros, "persistencia": persistencia_, "hipotesis": informe["hipotesis"]},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
