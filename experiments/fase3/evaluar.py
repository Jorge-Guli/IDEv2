"""Evaluación de la fase 3 (coordinación del grupo): criterios C1–C4, hipótesis prerregistradas y exploratorios.

Para cada semilla se genera primero un ancestro: LUCA evoluciona 30 000 pasos en la ecología de la fase 2c con
depredador gradual (sin los sensores nuevos). De su población final se siembran 600 organismos en cada
condición, con el refugio escalando de 2 a 3 (diseño pareado: todas las condiciones parten del mismo ancestro).

Uso:
    python experiments/fase3/evaluar.py --salida runs/fase3 [--procesos 4] [--pasos 60000] [--semillas 10]
        [--semilla-inicial 41] [--condiciones ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, corrida, genoma as gen, persistencia
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_ANCESTRO = RAIZ / "experiments" / "configs" / "depredacion.toml"
AJUSTES_ANCESTRO = ["depredacion.rampa=8000", "sim.registrar_cada=500"]
PASOS_ANCESTRO = 30_000
CONFIG = RAIZ / "experiments" / "configs" / "coordinacion.toml"
SIEMBRA = 600

CONDICIONES = {
    "base": [],  # control negativo: sin percepción nueva
    "rumbo": ["coordinacion.rumbo=true"],
    "senales": ["coordinacion.senales=true"],
    "ambos": ["coordinacion.rumbo=true", "coordinacion.senales=true"],
    # control de información: los mismos sensores con los valores de otro organismo al azar
    "barajado": ["coordinacion.rumbo=true", "coordinacion.senales=true", "coordinacion.barajar=true"],
    # control positivo de la física: mover al grupo no exige alinearse (basta el 10 % del tamaño)
    "facil": ["asociacion.fraccion_empuje=0.1"],
}
METRICAS = ["poblacion", "frac_en_refugio", "tamano_grupo_medio", "grupos_de_3_o_mas", "frac_enlazados",
            "alineacion_enlazados", "exito_empuje_grupos", "exito_empuje_grupos3", "senal_media",
            "tiene_senalar", "tiene_dividirse_unido", "tiene_compartir", "usa_compartir", "depredados",
            "energia_media", "genes_medios", "dist_etiqueta_enlazados", "dist_etiqueta_azar"]


def _ancestro(tarea):
    salida, semilla = tarea
    destino = Path(salida) / "ancestros" / f"semilla_{semilla}"
    if not (destino / "poblacion.npz").exists():
        cfg = config.cargar(CONFIG_ANCESTRO, AJUSTES_ANCESTRO)
        cfg.sim.semilla, cfg.sim.pasos = semilla, PASOS_ANCESTRO
        corrida.correr(cfg, destino, imagenes=False)
    h = persistencia.leer_historial(destino / "metricas.csv")
    final = h[-1]
    return {"semilla": semilla, "poblacion": final["poblacion"], "frac_en_refugio": final.get("frac_en_refugio")}


def siembra(salida, semilla):
    """600 genomas del ancestro, con pesos nulos sobre los sensores nuevos (que el ancestro no tenía)."""
    g = persistencia.cargar_genomas(Path(salida) / "ancestros" / f"semilla_{semilla}" / "poblacion.npz")
    if len(g["mu"]) == 0:
        return None
    idx = np.random.default_rng(semilla).integers(0, len(g["mu"]), SIEMBRA)
    g = {k: v[idx].copy() for k, v in g.items()}
    g["w"][..., np.r_[gen.SENS_RUMBO, gen.SENS_SENAL]] = 0.0
    return g


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    res = {"nombre": nombre, "semilla": semilla}
    g = siembra(salida, semilla)
    if g is None:
        return {**res, "sin_ancestro": True, "extinta": True, "paso_extincion": 0,
                **{m: float("nan") for m in METRICAS}, "poblacion": 0.0}
    cfg = config.cargar(CONFIG, CONDICIONES[nombre])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{semilla}", g)
    h = sim.historial
    ultimo = [r for r in h if r["t"] >= 0.75 * pasos]
    extinta = sim.pob.n == 0
    res.update({"pasos": sim.t, "poblacion_final": sim.pob.n, "extinta": extinta,
                "paso_extincion": sim.t if extinta else None, "sin_ancestro": False})
    for m in METRICAS:
        vals = np.array([r.get(m, np.nan) for r in ultimo], dtype=float)
        res[m] = float(np.nanmean(vals)) if vals.size and not np.all(np.isnan(vals)) else float("nan")
    if extinta:
        res["poblacion"] = 0.0
    res["tamano_grupo_max_total"] = max((r.get("tamano_grupo_max", 0) for r in h), default=0)
    return res


def evaluar_hipotesis(por: dict) -> dict:
    """Reglas prerregistradas (docs/bitacora/2026-10-24-fase3-prerregistro.md). Variable principal:
    fracción de la población en grupos de tamaño ≥ refugio (3) en el último cuarto; las extinciones cuentan
    como 0 (sin grupos)."""
    def frac(n):
        return {r["semilla"]: (0.0 if r["extinta"] or r["frac_en_refugio"] != r["frac_en_refugio"] else r["frac_en_refugio"])
                for r in por.get(n, [])}

    def comparar(a, b, umbral=0.2):
        fa, fb = frac(a), frac(b)
        comunes = sorted(set(fa) & set(fb))
        dif = [fa[s] - fb[s] for s in comunes]
        gana = sum(d >= umbral for d in dif)
        return {"semillas": comunes, "diferencias": [round(d, 3) for d in dif], "superan_por_0.2": gana,
                "media_dif": round(float(np.mean(dif)), 3) if dif else None,
                "cumple": bool(comunes) and gana >= 0.7 * len(comunes)}

    h = {}
    if "facil" in por and "base" in por:
        h["H1_facil_vs_base"] = comparar("facil", "base")
    for n in ("rumbo", "senales", "ambos"):
        if n in por and "base" in por:
            h[f"H2_{n}_vs_base"] = comparar(n, "base")
    if "ambos" in por and "barajado" in por:
        h["H3_ambos_vs_barajado"] = comparar("ambos", "barajado")
    # secundaria: ¿evoluciona la alineación del rumbo entre enlazados?
    for n in ("rumbo", "ambos"):
        if n in por and "base" in por:
            al = {k: {r["semilla"]: r["alineacion_enlazados"] for r in por[k] if not r["extinta"]} for k in (n, "base")}
            comunes = sorted(s for s in set(al[n]) & set(al["base"]) if al[n][s] == al[n][s] and al["base"][s] == al["base"][s])
            dif = [al[n][s] - al["base"][s] for s in comunes]
            h[f"H4_alineacion_{n}_vs_base"] = {"semillas": comunes, "diferencias": [round(d, 3) for d in dif],
                                               "cumple": bool(comunes) and sum(d >= 0.2 for d in dif) >= 0.7 * len(comunes)}
    if "base" in por:
        fb = list(frac("base").values())
        h["H0_base_sin_grupos"] = {"frac_en_refugio": [round(f, 3) for f in fb],
                                   "cumple": bool(fb) and sum(f < 0.1 for f in fb) >= 0.7 * len(fb)}
    return h


def _forzar_asociacion(sim):
    p = sim.pob
    for k, prim in enumerate([gen.UNIRSE, gen.COMPARTIR, gen.DIVIDIRSE_UNIDO, gen.SOLTARSE, gen.SENALAR]):
        p["activo"][:, 4 + k] = True
        p["prim"][:, 4 + k] = prim
        p["w"][:, 4 + k, gen.S_RUIDO] = 2.0
    p["w"][:, 4:9, gen.S_RUMBO_SOCIOS_SIN] = 1.0
    p["w"][:, 4:9, gen.S_SENAL_SOCIOS] = 1.0


def _huella(_):
    cfg = config.cargar(CONFIG, CONDICIONES["ambos"] + ["mundo.alto=64", "mundo.ancho=64", "sim.dispositivo=cpu",
                                                         "sim.poblacion_inicial=300", "depredacion.escalada_inicio=300",
                                                         "depredacion.escalada_pasos=1000"])
    sim = Simulacion(cfg)
    _forzar_asociacion(sim)
    h = hashlib.sha256(repr(sim.correr(2000)).encode())
    for k in sorted(sim.pob.d):
        h.update(np.ascontiguousarray(sim.pob.d[k]).tobytes())
    return h.hexdigest()


def _invariantes(_):
    """Con señales y rumbo: señal en [0, 1], celdas únicas y enlaces simétricos."""
    from simbio.simulacion import OPUESTA
    cfg = config.cargar(CONFIG, CONDICIONES["ambos"] + ["mundo.alto=64", "mundo.ancho=64",
                                                         "sim.poblacion_inicial=800", "sim.dispositivo=cpu"])
    sim = Simulacion(cfg)
    _forzar_asociacion(sim)
    violaciones = enlaces = 0
    for _ in range(3000):
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
        ok = ok and bool(np.all((p["senal"] >= 0) & (p["senal"] <= 1)))
        violaciones += int(not ok)
    return {"violaciones": violaciones, "enlaces_observados": enlaces}


def _rendimiento():
    cfg = config.cargar(CONFIG, CONDICIONES["ambos"] + ["mundo.alto=180", "mundo.ancho=180",
                                                         "sim.poblacion_inicial=1500", "sim.registrar_cada=100000",
                                                         "sim.dispositivo=cpu", "depredacion.inicio=100000"])
    # sin depredador: desde LUCA, un depredador activo desde el paso 0 extingue la población y se mediría un
    # mundo vacío (error de la primera evaluación)
    sim = Simulacion(cfg)
    sim.correr(1500)
    n0 = sim.pob.n
    t0 = time.time()
    sim.correr(500)
    return {"pasos_por_segundo": round(500 / (time.time() - t0), 1), "poblacion": int((n0 + sim.pob.n) / 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase3")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=60000)
    ap.add_argument("--semillas", type=int, default=10)
    ap.add_argument("--semilla-inicial", type=int, default=41)  # los pilotos usaron 101–103 y 201–202
    ap.add_argument("--condiciones", nargs="*", default=None)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    condiciones = args.condiciones or list(CONDICIONES)
    t0 = time.time()
    with Pool(args.procesos) as pool:
        ancestros = pool.map(_ancestro, [(str(args.salida), s) for s in semillas])
        resultados = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in condiciones for s in semillas])
        huellas = pool.map(_huella, range(2))
        invariantes = pool.map(_invariantes, range(1))[0]
    rendimiento = _rendimiento()
    por = {}
    for r in resultados:
        por.setdefault(r["nombre"], []).append(r)
    persistencia_ = {n: f"{sum(not r['extinta'] for r in rs)}/{len(rs)}" for n, rs in por.items()}
    umbral = int(np.ceil(0.7 * len(semillas)))
    c1 = all(sum(not r["extinta"] for r in rs) >= umbral for rs in por.values())
    resumen = {n: {**{m: {"media": float(np.nanmean([r[m] for r in rs])),
                          "por_semilla": [round(r[m], 4) for r in rs]} for m in METRICAS},
                   "extinciones": [r["paso_extincion"] for r in rs if r["extinta"]],
                   "tamano_grupo_max_total": [r.get("tamano_grupo_max_total") for r in rs]}
               for n, rs in por.items()}
    informe = {
        "parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
        "ancestros": ancestros,
        "criterios": {
            "C1_persistencia": {"aprobado": c1, **persistencia_},
            "C2_invariantes": {"aprobado": invariantes["violaciones"] == 0 and invariantes["enlaces_observados"] > 0,
                               **invariantes},
            "C3_reproducibilidad": {"aprobado": huellas[0] == huellas[1]},
            "C4_rendimiento": {"aprobado": rendimiento["pasos_por_segundo"] >= 40 and rendimiento["poblacion"] >= 1000,
                               **rendimiento},
        },
        "hipotesis": evaluar_hipotesis(por),
        "exploratorios": resumen,
    }
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ancestros": ancestros, "criterios": informe["criterios"], "hipotesis": informe["hipotesis"]},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
