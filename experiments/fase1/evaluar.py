"""Evaluación de la fase 1: criterios de éxito (C1–C4) y experimentos exploratorios (E1–E2).

Uso:
    python experiments/fase1/evaluar.py --salida runs/fase1 [--procesos 4] [--pasos 20000] [--semillas 5]

Para una prueba rápida: --pasos 3000 --semillas 2.
"""

from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, corrida, genoma as gen, persistencia
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
CONFIGS = RAIZ / "experiments" / "configs"


def _correr(tarea: tuple[str, str, int, int, list[str]]) -> dict:
    nombre, archivo, semilla, pasos, ajustes = tarea
    cfg = config.cargar(CONFIGS / archivo, ajustes)
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    salida = SALIDA / nombre / f"semilla_{semilla}"
    sim = corrida.correr(cfg, salida)
    h = sim.historial
    return {"nombre": nombre, "semilla": semilla, "pasos": sim.t, "poblacion_final": sim.pob.n,
            "salida": str(salida), "historial": h}


def _competir(tarea: tuple[str, int, int]) -> float:
    ruta_pob, semilla, pasos = tarea
    cfg = config.cargar(CONFIGS / "base.toml", ["herencia.mutacion=false", "sim.registrar_cada=500"])
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    evolucionada = persistencia.cargar_genomas(Path(ruta_pob))
    return corrida.competir(cfg, gen.luca(cfg.herencia), evolucionada)


def _rendimiento() -> dict:
    cfg = config.cargar(CONFIGS / "base.toml", ["mundo.alto=150", "mundo.ancho=150", "sim.poblacion_inicial=1500",
                                               "sim.registrar_cada=100000"])
    sim = Simulacion(cfg)
    sim.correr(1500)  # llegar a una población estable
    n_inicio = sim.pob.n
    inicio = time.time()
    sim.correr(500)
    pps = 500 / (time.time() - inicio)
    return {"pasos_por_segundo": round(pps, 1), "poblacion": int((n_inicio + sim.pob.n) / 2)}


def serie(historial: list[dict], clave: str) -> np.ndarray:
    return np.array([h.get(clave, np.nan) for h in historial], dtype=float)


def resumen_tramo(historial, clave, desde, hasta=None):
    t = serie(historial, "t")
    v = serie(historial, clave)
    sel = (t >= desde) & (t < (hasta if hasta is not None else np.inf))
    return float(np.nanmean(v[sel])) if sel.any() else float("nan")


def main() -> None:
    global SALIDA
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase1")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=20000)
    ap.add_argument("--semillas", type=int, default=5)
    ap.add_argument("--pasos-competencia", type=int, default=3000)
    args = ap.parse_args()
    SALIDA = args.salida
    SALIDA.mkdir(parents=True, exist_ok=True)
    semillas = list(range(1, args.semillas + 1))
    P = args.pasos
    cambio = P // 2

    tareas = []
    tareas += [("base", "base.toml", s, P, []) for s in semillas]
    # E1: estrés en entorno variable (estacional + cambio abrupto a mitad de corrida)
    variable = [f"mundo.cambio_en_paso={cambio}"]
    tareas += [("variable_estres", "variable.toml", s, P, variable) for s in semillas]
    tareas += [("variable_sin_estres", "variable.toml", s, P, variable + ["herencia.estres=false"]) for s in semillas]
    # E2: aprendizaje
    tareas += [("base_sin_aprendizaje", "base.toml", s, P, ["aprendizaje.activo=false"]) for s in semillas]
    # control: sin mutación (LUCA congelado)
    tareas += [("base_sin_mutacion", "base.toml", s, P, ["herencia.mutacion=false"]) for s in semillas]

    t0 = time.time()
    with Pool(args.procesos) as pool:
        resultados = pool.map(_correr, tareas)
        por_nombre: dict[str, list[dict]] = {}
        for r in resultados:
            por_nombre.setdefault(r["nombre"], []).append(r)
        comp_tareas = [(str(Path(r["salida"]) / "poblacion.npz"), r["semilla"], args.pasos_competencia)
                       for r in por_nombre["base"] if r["poblacion_final"] > 0]
        competencias = pool.map(_competir, comp_tareas)
    rendimiento = _rendimiento()

    # ---------------- criterios
    base = por_nombre["base"]
    persistentes = sum(r["pasos"] >= P and r["poblacion_final"] > 0 for r in base)
    c1 = persistentes >= int(np.ceil(0.8 * len(base)))
    ganadas = sum(f > 0.8 for f in competencias if not np.isnan(f))
    c2 = ganadas >= int(np.ceil(0.8 * len(base)))
    a = Simulacion(config.cargar(CONFIGS / "base.toml", ["sim.pasos=300"])).correr(300)
    b = Simulacion(config.cargar(CONFIGS / "base.toml", ["sim.pasos=300"])).correr(300)
    c3 = a == b
    c4 = rendimiento["pasos_por_segundo"] >= 50

    def tabla(nombre: str) -> dict:
        rs = por_nombre[nombre]
        final = P * 0.75
        return {
            "persistieron": f"{sum(r['poblacion_final'] > 0 for r in rs)}/{len(rs)}",
            "poblacion_final_media": float(np.mean([r["poblacion_final"] for r in rs])),
            "comido_por_org_paso_final": float(np.nanmean([resumen_tramo(r["historial"], "comido_por_org_paso", final)
                                                           for r in rs])),
            "genes_medios_final": float(np.nanmean([resumen_tramo(r["historial"], "genes_medios", final) for r in rs])),
            "mu_final": float(np.nanmean([resumen_tramo(r["historial"], "mu_media", final) for r in rs])),
            "sens_final": float(np.nanmean([resumen_tramo(r["historial"], "sens_media", final) for r in rs])),
            "eta_final": float(np.nanmean([resumen_tramo(r["historial"], "eta_media", final) for r in rs])),
            "generacion_max": float(np.mean([max(serie(r["historial"], "generacion_max")) for r in rs])),
        }

    def recuperacion(nombre: str) -> dict:
        """Tras el cambio abrupto: población mínima relativa y eficiencia de forrajeo posterior."""
        rs = por_nombre[nombre]
        minimos, eficiencia = [], []
        for r in rs:
            h = r["historial"]
            antes = resumen_tramo(h, "poblacion", cambio - P // 10, cambio)
            t, pob = serie(h, "t"), serie(h, "poblacion")
            despues = pob[(t >= cambio) & (t < cambio + P // 5)]
            minimos.append(float(despues.min() / antes) if despues.size and antes > 0 else 0.0)
            eficiencia.append(resumen_tramo(h, "comido_por_org_paso", cambio, cambio + P // 5))
        return {"minimo_relativo_tras_cambio": float(np.mean(minimos)),
                "comido_por_org_paso_tras_cambio": float(np.nanmean(eficiencia))}

    informe = {
        "parametros": {"pasos": P, "semillas": semillas, "pasos_competencia": args.pasos_competencia,
                       "minutos": round((time.time() - t0) / 60, 1)},
        "criterios": {
            "C1_persistencia": {"aprobado": bool(c1), "persistieron": f"{persistentes}/{len(base)}"},
            "C2_adaptacion": {"aprobado": bool(c2), "fraccion_evolucionada": [round(f, 3) for f in competencias]},
            "C3_reproducibilidad": {"aprobado": bool(c3)},
            "C4_rendimiento": {"aprobado": bool(c4), **rendimiento},
        },
        "exploratorios": {
            "condiciones": {n: tabla(n) for n in por_nombre},
            "E1_estres_recuperacion": {n: recuperacion(n) for n in ("variable_estres", "variable_sin_estres")},
        },
    }
    (SALIDA / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
