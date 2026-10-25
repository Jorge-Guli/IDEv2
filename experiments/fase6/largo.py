"""Fase 6 (paso C + D): corridas largas con memoria interna. ¿Aparecen tipos celulares (división del trabajo)?

Ancestros como en la fase 4a (LUCA → ecología de la fase 2c → modelo adoptado de la fase 3c). De cada ancestro se
siembran 600 genomas en cuatro condiciones (refugio 3, movimiento por fuerza α = 0,5, rumbo, con mutación),
corridas largas:
    base           sin memoria
    memoria        con memoria interna
    eco            sin memoria, con retornos crecientes (γ = 2) y puentes citoplasmáticos (κ = 0,5)
    eco_memoria    ídem con memoria

Uso:
    python experiments/fase6/largo.py --salida runs/fase6 [--procesos 8] [--pasos 150000] [--semillas 5]
        [--semilla-inicial 131]
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
_spec = importlib.util.spec_from_file_location("evaluar_fase4", RAIZ / "experiments" / "fase4" / "evaluar.py")
fase4 = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase4"] = fase4
_spec.loader.exec_module(fase4)

CONDICIONES = {
    "base": [],
    "memoria": ["memoria.activa=true"],
    "eco": ["fisica.maquinaria_gamma=2.0", "asociacion.difusion_energia=0.5"],
    "eco_memoria": ["fisica.maquinaria_gamma=2.0", "asociacion.difusion_energia=0.5", "memoria.activa=true"],
}
METRICAS = ["poblacion", "grupos_de_3_o_mas", "frac_enlazados", "dispersion_roles_grupos", "dispersion_roles_poblacion",
            "tiene_memoria_a", "tiene_memoria_b", "memoria_media", "dispersion_memoria_grupos", "corr_memoria_rol",
            "generacion_media", "energia_media"]


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    g = persistencia.cargar_genomas(Path(salida) / "fuerza05_ambos" / f"semilla_{semilla}" / "poblacion.npz")
    res = {"nombre": nombre, "semilla": semilla}
    if len(g["mu"]) == 0:
        return {**res, "extinta": True}
    idx = np.random.default_rng(semilla).integers(0, len(g["mu"]), 600)
    cfg = config.cargar(fase4.CONFIG, fase4.MODELO + CONDICIONES[nombre] + ["sim.registrar_cada=1000"])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / "fase6" / nombre / f"semilla_{semilla}",
                         {k: v[idx] for k, v in g.items()}, imagenes=False)
    h = sim.historial
    res["extinta"] = sim.pob.n == 0
    for parte, desde in (("final", 0.9), ("medio", 0.45)):
        filas = [r for r in h if desde * pasos <= r["t"] <= (desde + 0.1) * pasos]
        for m in METRICAS:
            v = np.array([r.get(m, np.nan) for r in filas], dtype=float)
            res[f"{m}_{parte}"] = float(np.nanmean(v)) if v.size and not np.isnan(v).all() else float("nan")
    return res


def hipotesis(rs):
    """Reglas prerregistradas (docs/bitacora/2026-10-25-fase6-prerregistro.md)."""
    def val(n, m):
        return {r["semilla"]: r.get(m, np.nan) for r in rs if r["nombre"] == n and not r["extinta"]}
    h = {}
    for eco in ("", "eco_"):
        con, sin = f"{eco}memoria", (eco.rstrip("_") or "base")
        va, vb = val(con, "dispersion_roles_grupos_final"), val(sin, "dispersion_roles_grupos_final")
        comunes = sorted(s for s in set(va) & set(vb) if va[s] == va[s] and vb[s] == vb[s])
        d = [va[s] - vb[s] for s in comunes]
        h[f"L1_roles_{con}_vs_{sin}"] = {"diferencias": [round(x, 3) for x in d],
                                         "p_una_cola": round(fase4.permutacion_pareada(d), 4) if d else None,
                                         "cumple": bool(d) and fase4.permutacion_pareada(d) < 0.05}
        dm = val(con, "dispersion_memoria_grupos_final")
        h[f"L2_memoria_diferenciada_{con}"] = {"valores": {s: round(v, 3) for s, v in dm.items()},
                                               "cumple": sum(v > 0.1 for v in dm.values() if v == v) >= 3}
        cm = val(con, "corr_memoria_rol_final")
        h[f"L3_memoria_ligada_al_rol_{con}"] = {"valores": {s: round(v, 3) for s, v in cm.items()},
                                                "cumple": sum(abs(v) > 0.3 for v in cm.values() if v == v) >= 3}
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase6")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=150000)
    ap.add_argument("--semillas", type=int, default=5)
    ap.add_argument("--semilla-inicial", type=int, default=131)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    t0 = time.time()
    sal = str(args.salida)
    with Pool(args.procesos) as pool:
        ancestros = pool.map(fase4._ancestro, [(sal, s) for s in semillas])
        rs = pool.map(_correr, [(sal, n, s, args.pasos) for n in CONDICIONES for s in semillas])
    informe = {"parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
               "ancestros": ancestros, "hipotesis": hipotesis(rs), "corridas": rs}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: informe[k] for k in ("ancestros", "hipotesis")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
