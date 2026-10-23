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
    # núcleo
    "refugio": [],
    "uniforme": ['depredacion.modo="uniforme"'],  # misma mortalidad por ataque, sin refugio
    # protección igualada pero independiente de los enlaces: si la asociación aparece solo en "refugio",
    # la causa es que la protección dependa de asociarse y no la menor mortalidad
    "aleatorio": ['depredacion.modo="aleatorio"', "depredacion.prob_perdon=0.9"],
    "sin_depredacion": ["depredacion.activa=false"],
    # dosis
    "refugio_p0125": ["depredacion.prob_ataque=0.0125"],
    "refugio_p0175": ["depredacion.prob_ataque=0.0175"],
    # exploratorios
    "refugio_sin_division_unida": ["asociacion.division_unida=false"],  # solo unirse crea enlaces
    "refugio_3": ["depredacion.refugio=3"],
}
NUCLEO = ["refugio", "uniforme", "aleatorio", "sin_depredacion"]
METRICAS = ["poblacion", "frac_en_refugio", "depredados_en_refugio", "frac_enlazados", "tamano_grupo_medio", "grupos_de_3_o_mas",
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
    extinta = sim.pob.n == 0
    res = {"nombre": nombre, "semilla": semilla, "pasos": sim.t, "poblacion_final": sim.pob.n,
           "extinta": extinta, "paso_extincion": sim.t if extinta else None}
    for m in METRICAS:
        vals = np.array([r.get(m, np.nan) for r in ultimo], dtype=float)
        res[m] = float(np.nanmean(vals)) if vals.size and not np.all(np.isnan(vals)) else float("nan")
    if extinta:
        res["poblacion"] = 0.0  # una corrida extinta tiene población 0; el resto de métricas no aplica
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
    violaciones = enlaces = en_refugio = 0
    for _ in range(4000):
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
        en_refugio += sim.cont["depredados_en_refugio"]
    # con refugio 2 y modo gradual, nadie en un grupo de 2 o más puede morir por ataque
    return {"violaciones": violaciones, "enlaces_observados": enlaces, "depredados_en_refugio": en_refugio}


def evaluar_hipotesis(por: dict) -> dict:
    """Reglas prerregistradas (docs/bitacora/2026-10-23-fase2c-prerregistro.md, versión 2): las fracciones se
    evalúan sobre las corridas que sobrevivieron; las extinciones se informan aparte."""
    def resumen(n, condicion):
        rs = por.get(n, [])
        vivas = [r for r in rs if not r["extinta"]]
        ok = sum(condicion(r["frac_en_refugio"]) for r in vivas)
        return {"corridas": len(rs), "sobrevivieron": len(vivas), "cumplen": ok,
                "frac_cumplen": round(ok / len(vivas), 3) if vivas else None,
                "frac_en_refugio": [None if r["extinta"] else round(r["frac_en_refugio"], 3) for r in rs]}
    alta, baja = (lambda f: f > 0.5), (lambda f: f < 0.1)
    h = {}
    if "refugio" in por:
        r = resumen("refugio", alta)
        h["P1_refugio"] = {**r, "cumple": r["sobrevivieron"] >= 0.7 * r["corridas"] and (r["frac_cumplen"] or 0) >= 0.8}
    for clave, n in (("P2_uniforme", "uniforme"), ("P3_aleatorio", "aleatorio")):
        if n in por:
            r = resumen(n, baja)
            h[clave] = {**r, "cumple": r["sobrevivieron"] > 0 and r["frac_cumplen"] >= 0.8}
    for n in ("refugio_p0125", "refugio_p0175"):
        if n in por:
            r = resumen(n, alta)
            h[f"P4_dosis_{n}"] = {**r, "cumple": r["sobrevivieron"] > 0 and r["frac_cumplen"] >= 0.8}
    return h


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
    ap.add_argument("--semilla-inicial", type=int, default=11)  # 1 y 2 se usaron para calibrar
    ap.add_argument("--condiciones", nargs="*", default=None)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    condiciones = args.condiciones or list(CONDICIONES)  # NUCLEO = las 4 imprescindibles
    t0 = time.time()
    with Pool(args.procesos) as pool:
        resultados = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in condiciones for s in semillas])
        huellas = pool.map(_huella, range(2))
        invariantes = pool.map(_invariantes, range(1))[0]
    rendimiento = _rendimiento()
    por = {}
    for r in resultados:
        por.setdefault(r["nombre"], []).append(r)
    persisten = sum(not r["extinta"] for r in por.get("refugio", []))
    umbral = int(np.ceil(0.7 * len(semillas)))
    resumen = {n: {**{m: {"media": float(np.nanmean([r[m] for r in rs])),
                          "por_semilla": [round(r[m], 4) for r in rs]} for m in METRICAS},
                   "t_enlazados_50": [r["t_enlazados_50"] for r in rs],
                   "extinciones": [r["paso_extincion"] for r in rs if r["extinta"]],
                   "tamano_grupo_max_total": [r["tamano_grupo_max_total"] for r in rs]}
               for n, rs in por.items()}
    informe = {
        "parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
        "criterios": {
            "C1_persistencia": {"aprobado": persisten >= umbral, "refugio": f"{persisten}/{len(semillas)}"},
            "C2_invariantes": {"aprobado": invariantes["violaciones"] == 0 and invariantes["enlaces_observados"] > 0
                               and invariantes["depredados_en_refugio"] == 0, **invariantes},
            "C3_reproducibilidad": {"aprobado": huellas[0] == huellas[1]},
            "C4_rendimiento": {"aprobado": rendimiento["pasos_por_segundo"] >= 40, **rendimiento},
        },
        "hipotesis": evaluar_hipotesis(por),
        "exploratorios": resumen,
    }
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"criterios": informe["criterios"], "hipotesis": informe["hipotesis"]}, indent=2,
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
