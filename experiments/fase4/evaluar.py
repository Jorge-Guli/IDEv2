"""Fase 4a: ¿la restricción flagelar produce división del trabajo reproductivo dentro de los grupos?

Ancestros en dos etapas (por semilla):
    1. LUCA evoluciona 30 000 pasos en la ecología de la fase 2c (como en la fase 3);
    2. 60 000 pasos con el modelo adoptado en la fase 3c (fuerza, α = 0,5, rumbo y señales, refugio de 2 a 3).
De esa población se siembran 600 genomas en cada condición (refugio 3 fijo, con mutación), 60 000 pasos:
    sin        sin restricción
    r10, r20   tras dividirse, progenitor e hijo no pueden avanzar durante 10 o 20 pasos
    r20a       control: períodos de 20 pasos sorteados con la misma frecuencia, sin relación con dividirse

Uso:
    python experiments/fase4/evaluar.py --salida runs/fase4 [--procesos 8] [--semillas 10] [--semilla-inicial 101]
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

from simbio import config, corrida, persistencia

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("evaluar_fase3c", RAIZ / "experiments" / "fase3c" / "evaluar.py")
fase3c = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase3c"] = fase3c
_spec.loader.exec_module(fase3c)

CONFIG = RAIZ / "experiments" / "configs" / "coordinacion.toml"
MODELO = ['asociacion.movimiento="fuerza"', "asociacion.exponente_arrastre=0.5", "coordinacion.rumbo=true",
          "coordinacion.senales=true", "depredacion.refugio=3", "depredacion.refugio_final=0"]
CONDICIONES = {
    "sin": [],
    "r10": ["fisica.refractario_division=10"],
    "r20": ["fisica.refractario_division=20"],
    "r20a": ["fisica.refractario_division=20", 'fisica.refractario_modo="aleatorio"'],
    # fase 4c: costo privado de dividirse, sin inmovilidad (costo_division por defecto: 2)
    "c6": ["fisica.costo_division=6.0"],
    "c12": ["fisica.costo_division=12.0"],
}
CONDICIONES_4A = ["sin", "r10", "r20", "r20a"]
METRICAS = ["poblacion", "grupos_de_3_o_mas", "frac_enlazados", "concentracion_reproductiva", "corr_avanzar_dividir",
            "frac_nunca_dividio", "frac_refractarios", "alineacion_enlazados", "exito_empuje_grupos3"]


def _ancestro(tarea):
    salida, semilla = tarea
    fase3c.fase3._ancestro((salida, semilla))
    destino = Path(salida) / "fuerza05_ambos" / f"semilla_{semilla}" / "poblacion.npz"
    if not destino.exists():
        fase3c._correr((salida, "fuerza05_ambos", semilla, 60000))
    g = persistencia.cargar_genomas(destino)
    h = persistencia.leer_historial(destino.parent / "metricas.csv")
    return {"semilla": semilla, "poblacion": len(g["mu"]), "grupos_de_3_o_mas": h[-1].get("grupos_de_3_o_mas")}


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    g = persistencia.cargar_genomas(Path(salida) / "fuerza05_ambos" / f"semilla_{semilla}" / "poblacion.npz")
    res = {"nombre": nombre, "semilla": semilla}
    if len(g["mu"]) == 0:
        return {**res, "extinta": True, **{m: float("nan") for m in METRICAS}}
    idx = np.random.default_rng(semilla).integers(0, len(g["mu"]), 600)
    cfg = config.cargar(CONFIG, MODELO + CONDICIONES[nombre] + ["sim.registrar_cada=200"])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / "fase4" / nombre / f"semilla_{semilla}", {k: v[idx] for k, v in g.items()})
    ultimo = [r for r in sim.historial if r["t"] >= 0.75 * pasos]
    res["extinta"] = sim.pob.n == 0
    for m in METRICAS:
        v = np.array([r.get(m, np.nan) for r in ultimo], dtype=float)
        res[m] = float(np.nanmean(v)) if v.size and not np.isnan(v).all() else float("nan")
    if res["extinta"]:
        res["poblacion"] = 0.0
    return res


def permutacion_pareada(dif) -> float:
    """p de una cola (media > 0) por inversión de signos exacta."""
    d = np.asarray([x for x in dif if x == x], dtype=float)
    if d.size == 0:
        return float("nan")
    signos = ((np.arange(2 ** d.size)[:, None] >> np.arange(d.size)) & 1) * 2 - 1
    return float(((signos * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def evaluar_hipotesis(por):
    """Reglas prerregistradas (docs/bitacora/2026-10-24-fase4-prerregistro.md)."""
    def val(n, m):
        return {r["semilla"]: r[m] for r in por.get(n, []) if not r["extinta"]}

    def prueba(a, b, m, signo=1):
        va, vb = val(a, m), val(b, m)
        comunes = sorted(s for s in set(va) & set(vb) if va[s] == va[s] and vb[s] == vb[s])
        d = [signo * (va[s] - vb[s]) for s in comunes]
        p = permutacion_pareada(d)
        return {"n": len(d), "media_a": round(float(np.mean([va[s] for s in comunes])), 3) if d else None,
                "media_b": round(float(np.mean([vb[s] for s in comunes])), 3) if d else None,
                "p_una_cola": round(p, 4), "cumple": p < 0.05}

    return {
        "E1_corr_r20_mas_negativa_que_r20a": prueba("r20", "r20a", "corr_avanzar_dividir", signo=-1),
        "E2_nunca_dividio_r20_mayor_que_r20a": prueba("r20", "r20a", "frac_nunca_dividio"),
        "E3_concentracion_r20_mayor_que_r20a": prueba("r20", "r20a", "concentracion_reproductiva"),
        "E4_enlazados_r20_mayor_que_r20a": prueba("r20", "r20a", "frac_enlazados"),
        "E5_dosis_nunca_dividio_r20_mayor_que_r10": prueba("r20", "r10", "frac_nunca_dividio"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase4")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=60000)
    ap.add_argument("--semillas", type=int, default=10)
    ap.add_argument("--semilla-inicial", type=int, default=101)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    t0 = time.time()
    with Pool(args.procesos) as pool:
        ancestros = pool.map(_ancestro, [(str(args.salida), s) for s in semillas])
        rs = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in CONDICIONES_4A for s in semillas])
    por = {}
    for r in rs:
        por.setdefault(r["nombre"], []).append(r)
    resumen = {n: {m: {"media": float(np.nanmean([r[m] for r in v])), "por_semilla": [round(r[m], 4) for r in v]}
                   for m in METRICAS} for n, v in por.items()}
    informe = {"parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
               "ancestros": ancestros, "persistencia": {n: f"{sum(not r['extinta'] for r in v)}/{len(v)}"
                                                        for n, v in por.items()},
               "hipotesis": evaluar_hipotesis(por), "exploratorios": resumen}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: informe[k] for k in ("ancestros", "persistencia", "hipotesis")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
