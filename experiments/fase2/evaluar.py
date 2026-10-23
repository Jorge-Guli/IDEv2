"""Evaluación de la fase 2 (asociación): criterios C1–C4 y condiciones exploratorias.

Uso:
    python experiments/fase2/evaluar.py --salida runs/fase2 [--procesos 4] [--pasos 30000] [--semillas 5]
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
CONFIGS = RAIZ / "experiments" / "configs"

CONDICIONES = {
    # nombre: (archivo, ajustes)
    "base": ("base.toml", []),
    "variable": ("variable.toml", []),
    "base_elastico": ("base.toml", ["asociacion.adhesion=false"]),
    "base_sin_beneficio": ("base.toml", ["asociacion.eficiencia_compartir=0.0"]),
    # control con el mismo espectro mutacional: las primitivas existen y cuestan, pero no hacen nada
    "base_inerte": ("base.toml", ["asociacion.inerte=true"]),
    # control positivo: compartir crea energía (eficiencia 2); si ni así aparece, el protocolo no la detectaría
    "base_positivo": ("base.toml", ["asociacion.eficiencia_compartir=2.0"]),
}
METRICAS = ["poblacion", "frac_enlazados", "grupos_de_3_o_mas", "tamano_grupo_medio", "tamano_grupo_max",
            "compartido_por_org_paso", "frac_aprovechados", "tiene_unirse", "tiene_compartir",
            "tiene_dividirse_unido", "tiene_conjugar", "tiene_soltarse", "usa_unirse", "usa_compartir",
            "usa_dividirse_unido", "usa_conjugar", "recibido_por_org_paso", "dist_etiqueta_enlazados", "dist_etiqueta_azar", "genes_medios"]


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    archivo, ajustes = CONDICIONES[nombre]
    cfg = config.cargar(CONFIGS / archivo, ajustes + ["sim.registrar_cada=200"])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}")
    h = sim.historial
    ultimo = [r for r in h if r["t"] >= 0.75 * pasos]
    res = {"nombre": nombre, "semilla": semilla, "pasos": sim.t, "poblacion_final": sim.pob.n}
    for m in METRICAS:
        vals = [r.get(m, np.nan) for r in ultimo]
        res[m] = float(np.nanmean(vals)) if ultimo and not np.all(np.isnan(vals)) else float("nan")
    res["tamano_grupo_max_total"] = max((r.get("tamano_grupo_max", 0) for r in h), default=0)
    res["frac_enlazados_max"] = max((r.get("frac_enlazados", 0) for r in h), default=0)
    return res


def _forzar_asociacion(sim):
    p = sim.pob
    for k, prim in enumerate([gen.UNIRSE, gen.COMPARTIR, gen.DIVIDIRSE_UNIDO, gen.CONJUGAR, gen.SOLTARSE]):
        p["activo"][:, 4 + k] = True
        p["prim"][:, 4 + k] = prim
        p["w"][:, 4 + k, gen.S_RUIDO] = 2.0


def _huella(_):
    """Huella de una corrida con asociación forzada (ejercita compartir, conjugar y división unida)."""
    sim = Simulacion(config.cargar(CONFIGS / "base.toml", ["mundo.alto=64", "mundo.ancho=64"]))
    _forzar_asociacion(sim)
    h = hashlib.sha256(repr(sim.correr(1500)).encode())
    for k in sorted(sim.pob.d):
        h.update(np.ascontiguousarray(sim.pob.d[k]).tobytes())
    return h.hexdigest()


def _invariantes(_):
    """Corrida con asociación forzada: un organismo por celda, enlaces vecinos, simétricos y a vivos."""
    cfg = config.cargar(CONFIGS / "base.toml", ["mundo.alto=64", "mundo.ancho=64", "sim.poblacion_inicial=800"])
    sim = Simulacion(cfg)
    _forzar_asociacion(sim)
    violaciones, enlaces = 0, 0
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
    cfg = config.cargar(CONFIGS / "base.toml", ["mundo.alto=150", "mundo.ancho=150", "sim.poblacion_inicial=1500",
                                               "sim.registrar_cada=100000"])
    sim = Simulacion(cfg)
    sim.correr(1500)
    n0 = sim.pob.n
    t0 = time.time()
    sim.correr(500)
    return {"pasos_por_segundo": round(500 / (time.time() - t0), 1), "poblacion": int((n0 + sim.pob.n) / 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase2")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=30000)
    ap.add_argument("--semillas", type=int, default=5)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(1, args.semillas + 1))
    tareas = [(str(args.salida), n, s, args.pasos) for n in CONDICIONES for s in semillas]
    t0 = time.time()
    with Pool(args.procesos) as pool:
        resultados = pool.map(_correr, tareas)
        huellas = pool.map(_huella, range(2))
        invariantes = pool.map(_invariantes, range(1))[0]
    rendimiento = _rendimiento()

    por = {}
    for r in resultados:
        por.setdefault(r["nombre"], []).append(r)
    persisten = {n: sum(r["pasos"] >= args.pasos and r["poblacion_final"] > 0 for r in por[n])
                 for n in ("base", "variable")}
    umbral = int(np.ceil(0.8 * len(semillas)))
    resumen = {}
    for n, rs in por.items():
        resumen[n] = {m: {"media": float(np.nanmean([r[m] for r in rs])),
                          "por_semilla": [round(r[m], 4) for r in rs]} for m in METRICAS}
        resumen[n]["tamano_grupo_max_total"] = [r["tamano_grupo_max_total"] for r in rs]
        resumen[n]["frac_enlazados_max"] = [round(r["frac_enlazados_max"], 4) for r in rs]
    informe = {
        "parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
        "criterios": {
            "C1_persistencia": {"aprobado": all(v >= umbral for v in persisten.values()),
                                **{n: f"{v}/{len(semillas)}" for n, v in persisten.items()}},
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
