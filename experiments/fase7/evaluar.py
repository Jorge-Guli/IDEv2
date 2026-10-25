"""Fase 7: ¿evoluciona una memoria de contexto cuando el mundo la exige?

Mundo base desde LUCA, con dos tipos de comida en parches, una estación oculta que se alterna cada 2000 pasos y
decide cuál nutre, toxicidad diferida (sin aviso inmediato) y una pista de la estación con probabilidad 0,01 por
paso. Corridas largas. Condiciones:
    mem_info        memoria, pista informativa, sin aprendizaje
    mem_ruido       memoria, pista aleatoria (control: recordar no sirve), sin aprendizaje
    sin_memoria     sin memoria, pista informativa, sin aprendizaje
    mem_info_apr    memoria, pista informativa, con aprendizaje

Uso:
    python experiments/fase7/evaluar.py --salida runs/fase7 [--procesos 8] [--pasos 200000] [--semillas 6]
        [--semilla-inicial 141]
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

from simbio import config, corrida

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("evaluar_fase4", RAIZ / "experiments" / "fase4" / "evaluar.py")
fase4 = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase4"] = fase4
_spec.loader.exec_module(fase4)  # permutacion_pareada

CONFIG = RAIZ / "experiments" / "configs" / "base.toml"
MUNDO = ["estaciones.activa=true", "estaciones.castigo=0.5", 'estaciones.toxicidad="diferido"',
         "estaciones.p_pista=0.01", "estaciones.periodo=2000", "sim.registrar_cada=500"]
CONDICIONES = {
    "mem_info": ["memoria.activa=true", "aprendizaje.activo=false"],
    "mem_ruido": ["memoria.activa=true", "aprendizaje.activo=false", "estaciones.pista_informativa=false"],
    "sin_memoria": ["aprendizaje.activo=false"],
    "mem_info_apr": ["memoria.activa=true"],
}


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    cfg = config.cargar(CONFIG, MUNDO + CONDICIONES[nombre])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}", imagenes=False)
    h = sim.historial
    res = {"nombre": nombre, "semilla": semilla, "extinta": sim.pob.n == 0,
           "generacion_final": float(h[-1].get("generacion_media", np.nan))}
    for parte, (a, b) in (("final", (0.75, 1.0)), ("medio", (0.25, 0.5))):
        filas = [r for r in h if a * pasos <= r["t"] <= b * pasos]
        f = lambda k: np.array([r.get(k, np.nan) for r in filas], dtype=float)  # noqa: E731
        res[f"acierto_{parte}"] = float(np.nanmean(f("acierto_comida")))
        res[f"poblacion_{parte}"] = float(np.nanmean(f("poblacion")))
        seg = [float(np.nanmean(f(f"memoria_alineada_{c}"))) if f"memoria_alineada_{c}" in h[-1] else 0.0
               for c in "ab"]
        res[f"seguimiento_{parte}"] = max(seg, key=abs)  # memoria que sigue a la estación (signo constante)
        res[f"genes_memoria_{parte}"] = float(np.nanmean(f("tiene_memoria_a") + f("tiene_memoria_b")))
    return res


def hipotesis(rs):
    """Reglas prerregistradas (docs/bitacora/2026-10-25-fase7-prerregistro.md)."""
    def val(n, m):
        return {r["semilla"]: r[m] for r in rs if r["nombre"] == n and not r["extinta"] and r[m] == r[m]}

    def prueba(a, b, m):
        va, vb = val(a, m), val(b, m)
        comunes = sorted(set(va) & set(vb))
        d = [va[s] - vb[s] for s in comunes]
        p = fase4.permutacion_pareada(d)
        return {"n": len(d), "diferencias": [round(x, 3) for x in d], "p_una_cola": round(p, 4),
                "cumple": bool(d) and p < 0.05}
    seg = val("mem_info", "seguimiento_final")
    return {
        "M1_acierto_info_vs_ruido": prueba("mem_info", "mem_ruido", "acierto_final"),
        "M2_memoria_sigue_la_estacion": {"valores": {s: round(v, 3) for s, v in seg.items()},
                                         "cumple": sum(abs(v) > 0.3 for v in seg.values()) >= 4},
        "M3_acierto_info_vs_sin_memoria": prueba("mem_info", "sin_memoria", "acierto_final"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase7")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=200000)
    ap.add_argument("--semillas", type=int, default=6)
    ap.add_argument("--semilla-inicial", type=int, default=141)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    t0 = time.time()
    with Pool(args.procesos) as pool:
        rs = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in CONDICIONES for s in semillas])
    informe = {"parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
               "hipotesis": hipotesis(rs), "corridas": rs}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["hipotesis"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
