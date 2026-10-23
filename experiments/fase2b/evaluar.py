"""Evaluación de la fase 2b (bien público): criterios C1–C4 y condiciones exploratorias.

Uso:
    python experiments/fase2b/evaluar.py --salida runs/fase2b [--procesos 4] [--pasos 30000] [--semillas 5]
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
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
CONFIG = RAIZ / "experiments" / "configs" / "bien_publico.toml"

# nombre: (ajustes, genoma inicial). Los genomas sembrados responden a "¿se mantiene si ya está?",
# las corridas desde LUCA a "¿se descubre?".
CONDICIONES = {
    "publico": ([], "luca"),
    "publico_asoc_inerte": (["asociacion.inerte=true"], "luca"),
    "privado": (["bien_publico.privado=true"], "luca"),
    "secrecion_inerte": (["bien_publico.secrecion_inerte=true"], "luca"),
    "sembrado_secretor": ([], "secretor"),
    "sembrado_secretor_asoc_inerte": (["asociacion.inerte=true"], "secretor"),
    "sembrado_colonial": ([], "secretor_colonial"),
    # control del anterior: la división unida es una división común (sin grupos clonales)
    "sembrado_colonial_asoc_inerte": (["asociacion.inerte=true"], "secretor_colonial"),
}


def genoma_inicial(tipo: str, cfg) -> dict | None:
    if tipo == "luca":
        return None
    g = gen.luca(cfg.herencia)
    k = int(np.flatnonzero(~g["activo"][0])[0])
    g["activo"][0, k] = True
    g["prim"][0, k] = gen.SECRETAR  # secretar si hay recurso complejo y no hay comida aquí
    g["b"][0, k] = -0.5
    g["w"][0, k, gen.S_COMPLEJO_AQUI] = 3.0
    g["w"][0, k, gen.S_AQUI] = -3.0
    if tipo == "secretor_colonial":
        g["prim"][g["prim"] == gen.DIVIDIRSE] = gen.DIVIDIRSE_UNIDO
    n = cfg.sim.poblacion_inicial
    G = gen.repetir(g, n)
    G["etiqueta"] = np.random.default_rng(cfg.sim.semilla).random((n, 2))
    return G


METRICAS = ["poblacion", "tiene_secretar", "usa_secretar", "frac_no_secretores", "comido_libre_por_org_paso",
            "libre_por_secretores", "libre_por_no_secretores", "comido_por_org_paso", "enzima_total", "frac_enlazados",
            "grupos_de_3_o_mas", "tamano_grupo_medio", "frac_enlazados_secretores", "frac_enlazados_no_secretores",
            "energia_secretores", "energia_no_secretores", "tiene_dividirse_unido", "tiene_compartir",
            "tiene_unirse", "usa_compartir", "frac_aprovechados", "dist_etiqueta_enlazados", "dist_etiqueta_azar",
            "complejo_total", "libre_total"]


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    ajustes, tipo = CONDICIONES[nombre]
    cfg = config.cargar(CONFIG, ajustes + ["sim.registrar_cada=200"])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}", genomas=genoma_inicial(tipo, cfg))
    h = sim.historial
    ultimo = [r for r in h if r["t"] >= 0.75 * pasos]
    res = {"nombre": nombre, "semilla": semilla, "pasos": sim.t, "poblacion_final": sim.pob.n}
    for m in METRICAS:
        vals = np.array([r.get(m, np.nan) for r in ultimo], dtype=float)
        res[m] = float(np.nanmean(vals)) if vals.size and not np.all(np.isnan(vals)) else float("nan")
    # cuándo la secreción superó el 50 % de la población
    t50 = [r["t"] for r in h if r.get("tiene_secretar", 0) > 0.5]
    res["t_secrecion_50"] = t50[0] if t50 else None
    res["tamano_grupo_max_total"] = max((r.get("tamano_grupo_max", 0) for r in h), default=0)
    return res


def _huella(_):
    sim = Simulacion(config.cargar(CONFIG, ["mundo.alto=64", "mundo.ancho=64", "sim.dispositivo=cpu"]))
    h = hashlib.sha256(repr(sim.correr(1500)).encode())
    for k in sorted(sim.pob.d):
        h.update(np.ascontiguousarray(sim.pob.d[k]).tobytes())
    for campo in ("C", "Z", "A"):
        h.update(np.ascontiguousarray(getattr(sim.entorno, campo)).tobytes())
    return h.hexdigest()


def _conservacion(_):
    """Digestión en un mundo con enzima en todas partes, sin regeneración ni degradación del alimento libre:
    en cada paso ΔC = −digerido y ΔA = rendimiento·digerido (la ingesta se verifica en los tests)."""
    from simbio.entorno import Entorno

    cfg = config.cargar(CONFIG, ["mundo.alto=64", "mundo.ancho=64", "bien_publico.regeneracion_complejo=0.0",
                                 "bien_publico.degradacion_libre=0.0"])
    ent = Entorno(cfg.mundo, np.random.default_rng(0), bp=cfg.bien_publico)
    ent.Z[:] = np.random.default_rng(1).random(ent.Z.shape) * 2.0
    r, peor, digerido_total = cfg.bien_publico.rendimiento, 0.0, 0.0
    for t in range(500):
        C0, A0 = float(ent.C.sum()), float(ent.A.sum())
        ent.paso(t)
        digerido_total += ent.digerido
        escala = max(1.0, C0)
        peor = max(peor, abs((C0 - float(ent.C.sum())) - ent.digerido) / escala,
                   abs((float(ent.A.sum()) - A0) - r * ent.digerido) / escala)
    return {"error_relativo_maximo": peor, "digerido_total": round(digerido_total, 2)}


def _rendimiento():
    cfg = config.cargar(CONFIG, ["mundo.alto=260", "mundo.ancho=260", "sim.poblacion_inicial=1500",
                                 "sim.registrar_cada=100000", "sim.dispositivo=cpu"])
    sim = Simulacion(cfg)
    sim.correr(1500)
    n0 = sim.pob.n
    t0 = time.time()
    sim.correr(500)
    return {"pasos_por_segundo": round(500 / (time.time() - t0), 1), "poblacion": int((n0 + sim.pob.n) / 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase2b")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=30000)
    ap.add_argument("--semillas", type=int, default=5)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(1, args.semillas + 1))
    t0 = time.time()
    with Pool(args.procesos) as pool:
        resultados = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in CONDICIONES for s in semillas])
        huellas = pool.map(_huella, range(2))
        conservacion = pool.map(_conservacion, range(1))[0]
    rendimiento = _rendimiento()
    por = {}
    for r in resultados:
        por.setdefault(r["nombre"], []).append(r)
    persisten = sum(r["pasos"] >= args.pasos and r["poblacion_final"] > 0 for r in por["publico"])
    umbral = int(np.ceil(0.8 * len(semillas)))
    resumen = {n: {**{m: {"media": float(np.nanmean([r[m] for r in rs])),
                          "por_semilla": [round(r[m], 4) for r in rs]} for m in METRICAS},
                   "t_secrecion_50": [r["t_secrecion_50"] for r in rs],
                   "tamano_grupo_max_total": [r["tamano_grupo_max_total"] for r in rs]}
               for n, rs in por.items()}
    informe = {
        "parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
        "criterios": {
            "C1_persistencia": {"aprobado": persisten >= umbral, "publico": f"{persisten}/{len(semillas)}"},
            "C2_conservacion": {"aprobado": conservacion["error_relativo_maximo"] < 1e-9
                                and conservacion["digerido_total"] > 0, **conservacion},
            "C3_reproducibilidad": {"aprobado": huellas[0] == huellas[1]},
            "C4_rendimiento": {"aprobado": rendimiento["pasos_por_segundo"] >= 40, **rendimiento},
        },
        "exploratorios": resumen,
    }
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["criterios"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
