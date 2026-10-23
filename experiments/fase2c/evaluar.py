"""Evaluación de la fase 2c (depredación limitada por tamaño): criterios C1–C4 y exploratorios.

Uso:
    python experiments/fase2c/evaluar.py --salida runs/fase2c [--procesos 4] [--pasos 30000] [--semillas 10]
        [--semilla-inicial 1] [--condiciones ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, corrida, genoma as gen
from simbio.simulacion import OPUESTA, Simulacion

RAIZ = Path(__file__).resolve().parents[2]
CONFIG = RAIZ / "experiments" / "configs" / "depredacion.toml"

CONDICIONES = {
    "refugio": [],
    "uniforme": ['depredacion.modo="uniforme"'],  # misma mortalidad por ataque, sin refugio por tamaño
    "refugio_asoc_inerte": ["asociacion.inerte=true"],  # mismo espectro mutacional, la asociación no funciona
    "sin_depredacion": ["depredacion.activa=false"],
    "refugio_unanime": ['asociacion.movimiento="unanime"'],  # ¿importa cómo se mueven los grupos?
    "refugio_3": ["depredacion.refugio=3"],  # refugio más exigente (exploratorio)
}
METRICAS = ["poblacion", "frac_en_refugio", "frac_enlazados", "tamano_grupo_medio", "grupos_de_3_o_mas",
            "depredados", "tiene_dividirse_unido", "tiene_dividirse", "tiene_unirse", "tiene_soltarse",
            "tiene_compartir", "usa_compartir", "usa_dividirse_unido", "frac_aprovechados",
            "dist_etiqueta_enlazados", "dist_etiqueta_azar", "genes_medios", "energia_media"]


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    cfg = config.cargar(CONFIG, CONDICIONES[nombre] + ["sim.registrar_cada=200"])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}")
    h = sim.historial
    ultimo = [r for r in h if r["t"] >= 0.75 * pasos]
    res = {"nombre": nombre, "semilla": semilla, "pasos": sim.t, "poblacion_final": sim.pob.n}
    for m in METRICAS:
        vals = np.array([r.get(m, np.nan) for r in ultimo], dtype=float)
        res[m] = float(np.nanmean(vals)) if vals.size and not np.all(np.isnan(vals)) else float("nan")
    t50 = [r["t"] for r in h if r.get("frac_enlazados", 0) > 0.5]
    res["t_enlazados_50"] = t50[0] if t50 else None
    res["tamano_grupo_max_total"] = max((r.get("tamano_grupo_max", 0) for r in h), default=0)
    return res


def _forzar_asociacion(sim):
    p = sim.pob
    for k, prim in enumerate([gen.UNIRSE, gen.COMPARTIR, gen.DIVIDIRSE_UNIDO, gen.CONJUGAR, gen.SOLTARSE]):
        p["activo"][:, 4 + k] = True
        p["prim"][:, 4 + k] = prim
        p["w"][:, 4 + k, gen.S_RUIDO] = 2.0


def _huella(_):
    sim = Simulacion(config.cargar(CONFIG, ["mundo.alto=64", "mundo.ancho=64", "sim.dispositivo=cpu"]))
    _forzar_asociacion(sim)
    h = hashlib.sha256(repr(sim.correr(1500)).encode())
    for k in sorted(sim.pob.d):
        h.update(np.ascontiguousarray(sim.pob.d[k]).tobytes())
    return h.hexdigest()


def _invariantes(_):
    """Asociación forzada con empuje y depredación: celdas únicas, enlaces vecinos y simétricos."""
    cfg = config.cargar(CONFIG, ["mundo.alto=64", "mundo.ancho=64", "sim.poblacion_inicial=800", "sim.dispositivo=cpu"])
    sim = Simulacion(cfg)
    _forzar_asociacion(sim)
    violaciones = enlaces = 0
    for _ in range(2000):
        sim.paso()
        p = sim.pob
        if p.n == 0:
            break
        j = sim.vecinos_enlazados(sim.ocupacion())
        hay = p["socio"] >= 0
        enlaces += int(hay.sum())
        f, k = np.nonzero(hay)
        ok = (len(np.unique(p["y"] * 100000 + p["x"])) == p.n) and np.all(j[hay] >= 0)
        ok = ok and np.all(p["id"][j[hay]] == p["socio"][hay]) and np.all(p["socio"][j[f, k], OPUESTA[k]] == p["id"][f])
        violaciones += int(not ok)
    return {"violaciones": violaciones, "enlaces_observados": enlaces}


def _rendimiento():
    cfg = config.cargar(CONFIG, ["mundo.alto=180", "mundo.ancho=180", "sim.poblacion_inicial=1500",
                                 "sim.registrar_cada=100000", "sim.dispositivo=cpu"])
    sim = Simulacion(cfg)
    sim.correr(1500)
    n0 = sim.pob.n
    t0 = time.time()
    sim.correr(500)
    return {"pasos_por_segundo": round(500 / (time.time() - t0), 1), "poblacion": int((n0 + sim.pob.n) / 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase2c")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=30000)
    ap.add_argument("--semillas", type=int, default=10)
    ap.add_argument("--semilla-inicial", type=int, default=1)
    ap.add_argument("--condiciones", nargs="*", default=None)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    condiciones = args.condiciones or list(CONDICIONES)
    t0 = time.time()
    with Pool(args.procesos) as pool:
        resultados = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in condiciones for s in semillas])
        huellas = pool.map(_huella, range(2))
        invariantes = pool.map(_invariantes, range(1))[0]
    rendimiento = _rendimiento()
    por = {}
    for r in resultados:
        por.setdefault(r["nombre"], []).append(r)
    persisten = sum(r["pasos"] >= args.pasos and r["poblacion_final"] > 0 for r in por.get("refugio", []))
    umbral = int(np.ceil(0.8 * len(semillas)))
    resumen = {n: {**{m: {"media": float(np.nanmean([r[m] for r in rs])),
                          "por_semilla": [round(r[m], 4) for r in rs]} for m in METRICAS},
                   "t_enlazados_50": [r["t_enlazados_50"] for r in rs],
                   "tamano_grupo_max_total": [r["tamano_grupo_max_total"] for r in rs]}
               for n, rs in por.items()}
    informe = {
        "parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
        "criterios": {
            "C1_persistencia": {"aprobado": persisten >= umbral, "refugio": f"{persisten}/{len(semillas)}"},
            "C2_invariantes": {"aprobado": invariantes["violaciones"] == 0 and invariantes["enlaces_observados"] > 0,
                               **invariantes},
            "C3_reproducibilidad": {"aprobado": huellas[0] == huellas[1]},
            "C4_rendimiento": {"aprobado": rendimiento["pasos_por_segundo"] >= 40, **rendimiento},
        },
        "exploratorios": resumen,
    }
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["criterios"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
