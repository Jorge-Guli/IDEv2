"""Fase 9: ¿evoluciona la regulación condicionada (genes que se expresan según la memoria)?

Mundo mosaico de la fase 8 (dos tipos de comida mezclados finamente, estación oculta cada 2000 pasos, toxicidad
diferida, pista con probabilidad 0,01). Sin aprendizaje. En el piloto desde LUCA puro (100 000 pasos) la memoria no
apareció: el gen de memoria cuesta y no sirve sin genes condicionados, y viceversa. Para separar los dos pasos, la
población arranca con LUCA más un gen de memoria ya conectado a la pista (memoria A = 1 en la estación A, 0 en la
B); lo que tiene que evolucionar es usarla. Condiciones:
    sem_info        LUCA + gen de memoria, pista informativa, regulación posible
    sem_ruido       igual, pista aleatoria (control: la memoria no informa)
    sem_sin_reg     igual a sem_info, pero las condiciones de los genes no mutan (control: sin regulación)
    luca_info       LUCA puro, pista informativa, regulación posible (¿aparece todo desde cero?)

Uso:
    python experiments/fase9/evaluar.py --salida runs/fase9 [--procesos 8] [--pasos 300000] [--semillas 6]
        [--semilla-inicial 171]
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

from simbio import config, corrida, genoma as gen

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("evaluar_fase7", RAIZ / "experiments" / "fase7" / "evaluar.py")
fase7 = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase7"] = fase7
_spec.loader.exec_module(fase7)

BASE = fase7.MUNDOS["mosaico"] + ["memoria.activa=true", "aprendizaje.activo=false"]
CONDICIONES = {
    "sem_info": [],
    "sem_ruido": ["estaciones.pista_informativa=false"],
    "sem_sin_reg": ["herencia.k_condicion=0.0"],
    "luca_info": [],
}
SEMBRADAS = {"sem_info", "sem_ruido", "sem_sin_reg"}


def genomas_iniciales(cfg, semilla):
    """LUCA con un gen de memoria A conectado a la pista (sesgo 0, peso 20: una pista fija la memoria)."""
    n = cfg.sim.poblacion_inicial
    g = gen.repetir(gen.luca(cfg.herencia), n)
    g["etiqueta"] = np.random.default_rng(semilla).random((n, 2))
    r = int(np.flatnonzero(~g["activo"][0])[0])
    g["activo"][:, r], g["prim"][:, r], g["b"][:, r], g["cond"][:, r] = True, gen.MEMORIA_A, 0.0, 0
    g["w"][:, r] = 0.0
    g["w"][:, r, gen.S_PISTA] = 20.0
    return g


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    cfg = config.cargar(fase7.CONFIG, BASE + CONDICIONES[nombre])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    g = genomas_iniciales(cfg, semilla) if nombre in SEMBRADAS else None
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}", genomas=g, imagenes=False)
    h = sim.historial
    res = {"nombre": nombre, "semilla": semilla, "extinta": sim.pob.n == 0,
           "generacion_final": float(h[-1].get("generacion_media", np.nan))}

    def media(v):  # sin avisos cuando no hay datos (corrida extinta antes de la ventana)
        return float(np.nanmean(v)) if v.size and not np.isnan(v).all() else float("nan")
    for parte, (a, b) in (("final", (0.75, 1.0)), ("medio", (0.25, 0.5))):
        filas = [r for r in h if a * pasos <= r["t"] <= b * pasos]
        f = lambda k: np.array([r.get(k, np.nan) for r in filas], dtype=float)  # noqa: E731
        res[f"acierto_{parte}"] = media(f("acierto_comida"))
        res[f"poblacion_{parte}"] = media(f("poblacion"))
        seg = [fase7.fase_seguimiento(f(f"memoria_alineada_{c}"), f("estacion")) for c in "ab"]
        res[f"seguimiento_{parte}"] = max(seg, key=lambda v: abs(v) if v == v else -1.0)
        res[f"genes_memoria_{parte}"] = media(f("tiene_memoria_a") + f("tiene_memoria_b"))
        res[f"con_gen_condicionado_{parte}"] = media(f("con_gen_condicionado"))
    return res


def hipotesis(rs):
    """Reglas prerregistradas (docs/bitacora/2026-10-26-fase9-prerregistro.md)."""
    def val(n, m):
        return {r["semilla"]: r[m] for r in rs if r["nombre"] == n and not r["extinta"] and r[m] == r[m]}

    def prueba(a, b, m):
        va, vb = val(a, m), val(b, m)
        comunes = sorted(set(va) & set(vb))
        d = [va[s] - vb[s] for s in comunes]
        p = fase7.fase4.permutacion_pareada(d)
        return {"n": len(d), "diferencias": [round(x, 3) for x in d], "p_una_cola": round(p, 4),
                "cumple": bool(d) and p < 0.05}
    ac = val("sem_info", "acierto_final")
    return {
        "R1_acierto_info_vs_ruido": prueba("sem_info", "sem_ruido", "acierto_final"),
        "R2_acierto_info_vs_sin_regulacion": prueba("sem_info", "sem_sin_reg", "acierto_final"),
        "R3_acierto_info_mayor_a_060": {"valores": {s: round(v, 3) for s, v in ac.items()},
                                        "cumple": sum(v > 0.6 for v in ac.values()) >= 4},
        "R4_luca_info_mayor_a_060": {"valores": {s: round(v, 3) for s, v in val("luca_info", "acierto_final").items()},
                                     "cumple": sum(v > 0.6 for v in val("luca_info", "acierto_final").values()) >= 4},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase9")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=300000)
    ap.add_argument("--semillas", type=int, default=6)
    ap.add_argument("--semilla-inicial", type=int, default=171)
    ap.add_argument("--condiciones", nargs="*", default=list(CONDICIONES))
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    t0 = time.time()
    with Pool(args.procesos) as pool:
        rs = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in args.condiciones for s in semillas])
    informe = {"parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
               "hipotesis": hipotesis(rs), "corridas": rs}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["hipotesis"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
