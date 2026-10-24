"""Fase 3d: ablación y sensibilidad del efecto de la percepción de los socios (movimiento por fuerza).

Parte A, ablación. Usa las poblaciones que evolucionaron con `fuerza05_ambos` en la réplica de la fase 3c
(`--replica runs/fase3c_replica`, semillas 71–90). Para cada semilla se siembran 600 genomas de esa población en un
mundo con refugio 3 fijo, sin mutación, y se corren brazos que difieren solo en qué información reciben:
    intacto        rumbo y señales, como evolucionaron
    cero           sin sensores de rumbo ni señales (valen 0) y sin emitir señal
    barajado       rumbo y señales de otro enlazado al azar
    solo_rumbo     sin señales
    solo_senales   sin rumbo
    sin_aprendizaje  intacto, pero sin aprendizaje y con los ajustes plásticos en 0
en dos momentos:
    formacion      los brazos parten de la siembra (los grupos tienen que formarse)
    mantenimiento  los brazos parten de un mismo estado, tras 5000 pasos intactos (grupos ya formados)
Todos los brazos de una semilla y un momento comparten el estado de partida y el generador (diseño pareado).

Parte B, sensibilidad. Usa `experiments/fase3c/evaluar.py` con semillas nuevas (91–100): α = 1/3 y α = 0,75
(ambos contra barajado), y solo rumbo contra barajado con α = 0,5.

Uso:
    python experiments/fase3d/evaluar.py --salida runs/fase3d --replica runs/fase3c_replica [--procesos 8]
        [--partes ablacion sensibilidad]
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, genoma as gen, persistencia
from simbio import dispositivo as dev
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("evaluar_fase3c", RAIZ / "experiments" / "fase3c" / "evaluar.py")
fase3c = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase3c"] = fase3c
_spec.loader.exec_module(fase3c)

CONFIG = RAIZ / "experiments" / "configs" / "coordinacion.toml"
AJUSTES_ABLACION = ['asociacion.movimiento="fuerza"', "asociacion.exponente_arrastre=0.5",
                    "coordinacion.rumbo=true", "coordinacion.senales=true", "herencia.mutacion=false",
                    "depredacion.refugio=3", "depredacion.refugio_final=0", "sim.registrar_cada=100"]
SEMILLAS_ABLACION = list(range(71, 91))
CALENTAMIENTO, PASOS_BRAZO = 5000, 15000
BRAZOS = ["intacto", "cero", "barajado", "solo_rumbo", "solo_senales", "sin_aprendizaje"]
BRAZOS_FORMACION = ["intacto", "cero", "barajado", "sin_aprendizaje"]
SENSIBILIDAD = ["fuerza033_ambos", "fuerza033_barajado", "fuerza075_ambos", "fuerza075_barajado",
                "fuerza05_rumbo", "fuerza05_barajado"]
SEMILLAS_SENSIBILIDAD = list(range(91, 101))


def clonar(sim: Simulacion) -> Simulacion:
    """Copia profunda de una simulación (estado, población, entorno y generadores), compartiendo el módulo de
    arreglos (NumPy o CuPy), que no se puede copiar."""
    return copy.deepcopy(sim, {id(sim.xp): sim.xp})


def aplicar_brazo(sim: Simulacion, brazo: str) -> None:
    """Modifica la información que recibe la población (in situ). Sin mutación, el genoma no cambia."""
    c = sim.cfg.coordinacion
    if brazo in ("cero", "solo_senales"):
        c.rumbo = False
    if brazo in ("cero", "solo_rumbo"):
        c.senales = False
    if brazo == "barajado":
        c.barajar = True
    if brazo == "sin_aprendizaje":
        sim.cfg.aprendizaje.activo = False
        sim.pob["P"][:] = 0.0
        sim.pob["p"][:] = 0.0
    if not c.senales:  # sin canal: los genes de señal no emiten (ni cuestan)
        sim.bloqueadas[gen.SENALAR] = True
        sim.pob["senal"][:] = 0.0


def _medir(historial, desde):
    filas = [r for r in historial if r["t"] >= desde]
    out = {}
    for m in ("grupos_de_3_o_mas", "frac_enlazados", "poblacion", "exito_empuje_grupos3"):
        v = np.array([r.get(m, np.nan) for r in filas], dtype=float)
        out[m] = float(np.nanmean(v)) if v.size and not np.isnan(v).all() else float("nan")
    al = [r["alineacion_enlazados"] for r in filas
          if r.get("frac_enlazados", 0) * r.get("poblacion", 0) / 2 >= 20 and r["alineacion_enlazados"] == r["alineacion_enlazados"]]
    out["alineacion_enlazados"] = float(np.mean(al)) if len(al) >= 0.5 * len(filas) else float("nan")
    return out


def _ablacion(tarea):
    replica, semilla = tarea
    ruta = Path(replica) / "fuerza05_ambos" / f"semilla_{semilla}" / "poblacion.npz"
    g = persistencia.cargar_genomas(ruta)
    if len(g["mu"]) == 0:
        return {"semilla": semilla, "sin_poblacion": True}
    idx = np.random.default_rng(semilla).integers(0, len(g["mu"]), 600)
    cfg = config.cargar(CONFIG, AJUSTES_ABLACION)
    cfg.sim.semilla = semilla
    inicial = Simulacion(cfg, {k: v[idx] for k, v in g.items()})
    res = {"semilla": semilla, "sin_poblacion": False, "formacion": {}, "mantenimiento": {}}
    for brazo in BRAZOS_FORMACION:
        sim = clonar(inicial)
        aplicar_brazo(sim, brazo)
        sim.correr(PASOS_BRAZO)
        res["formacion"][brazo] = {**_medir(sim.historial, PASOS_BRAZO * 2 / 3), "poblacion_final": sim.pob.n}
    inicial.correr(CALENTAMIENTO)
    res["al_ramificar"] = _medir(inicial.historial, CALENTAMIENTO - 1000)
    for brazo in BRAZOS:
        sim = clonar(inicial)
        aplicar_brazo(sim, brazo)
        n0 = len(sim.historial)
        sim.correr(PASOS_BRAZO)
        res["mantenimiento"][brazo] = {**_medir(sim.historial[n0:], CALENTAMIENTO + PASOS_BRAZO * 2 / 3),
                                       "poblacion_final": sim.pob.n}
    return res


def permutacion_pareada(dif) -> float:
    """p de una cola (media > 0) por inversión de signos exacta (hasta 20 pares)."""
    d = np.asarray([x for x in dif if x == x], dtype=float)
    n = d.size
    if n == 0:
        return float("nan")
    signos = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1) * 2 - 1
    medias = (signos * d).mean(axis=1)
    return float((medias >= d.mean() - 1e-12).mean())


def hipotesis_ablacion(res):
    """Reglas prerregistradas (docs/bitacora/2026-10-24-fase3d-prerregistro.md)."""
    rs = [r for r in res if not r["sin_poblacion"]]

    def dif(momento, a, b, m, filtro=None):
        out = []
        for r in rs:
            if filtro is not None and not filtro(r):
                continue
            va, vb = r[momento][a][m], r[momento][b][m]
            if va == va and vb == vb:
                out.append(va - vb)
        return out

    con_grupos = lambda r: r["mantenimiento"]["intacto"]["grupos_de_3_o_mas"] >= 0.1  # noqa: E731
    h = {}
    for clave, (momento, a, b, filtro) in {
        "A1_mantenimiento_intacto_vs_cero": ("mantenimiento", "intacto", "cero", con_grupos),
        "A2_formacion_intacto_vs_cero": ("formacion", "intacto", "cero", None),
        "A5_mantenimiento_rumbo_vs_senales": ("mantenimiento", "solo_rumbo", "solo_senales", con_grupos),
        "A6_poblacion_intacto_vs_cero": ("mantenimiento", "intacto", "cero", None),
    }.items():
        d = dif(momento, a, b, "poblacion" if clave.startswith("A6") else "grupos_de_3_o_mas", filtro)
        p = permutacion_pareada(d)
        h[clave] = {"n": len(d), "media_dif": round(float(np.mean(d)), 4) if d else None,
                    "diferencias": [round(x, 3) for x in d], "p_una_cola": round(p, 4), "cumple": p < 0.05}
    for clave, (a, b) in {"A3_alineacion_intacto_vs_cero": ("intacto", "cero"),
                          "A4_alineacion_sin_aprendizaje_vs_cero": ("sin_aprendizaje", "cero")}.items():
        d = dif("mantenimiento", a, b, "alineacion_enlazados")
        h[clave] = {"n": len(d), "diferencias": [round(x, 3) for x in d],
                    "cumple": bool(d) and sum(x >= 0.2 for x in d) >= 0.7 * len(d)}
    return h


def hipotesis_sensibilidad(por):
    def g3(n):
        return {r["semilla"]: (0.0 if r["extinta"] else r["grupos_de_3_o_mas"]) for r in por.get(n, [])}
    h = {}
    for clave, (a, b) in {"S1_alfa033_ambos_vs_barajado": ("fuerza033_ambos", "fuerza033_barajado"),
                          "S2_alfa075_ambos_vs_barajado": ("fuerza075_ambos", "fuerza075_barajado"),
                          "S3_alfa05_rumbo_vs_barajado": ("fuerza05_rumbo", "fuerza05_barajado")}.items():
        va, vb = g3(a), g3(b)
        comunes = sorted(set(va) & set(vb))
        d = [va[s] - vb[s] for s in comunes]
        p = permutacion_pareada(d)
        h[clave] = {"n": len(d), "media_a": round(float(np.mean([va[s] for s in comunes])), 3) if d else None,
                    "media_b": round(float(np.mean([vb[s] for s in comunes])), 3) if d else None,
                    "diferencias": [round(x, 3) for x in d], "p_una_cola": round(p, 4), "cumple": p < 0.05}
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase3d")
    ap.add_argument("--replica", type=Path, default=RAIZ / "runs" / "fase3c_replica")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--partes", nargs="*", default=["ablacion", "sensibilidad"])
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    informe = {"parametros": {"partes": args.partes}}
    with Pool(args.procesos) as pool:
        if "ablacion" in args.partes:
            faltan = [s for s in SEMILLAS_ABLACION
                      if not (args.replica / "fuerza05_ambos" / f"semilla_{s}" / "poblacion.npz").exists()]
            if faltan:
                sys.exit(f"faltan poblaciones de la réplica en {args.replica} (semillas {faltan})")
            res = pool.map(_ablacion, [(str(args.replica), s) for s in SEMILLAS_ABLACION])
            informe["ablacion"] = {"hipotesis": hipotesis_ablacion(res), "corridas": res}
        if "sensibilidad" in args.partes:
            sal = str(args.salida / "sensibilidad")
            Path(sal).mkdir(parents=True, exist_ok=True)
            anc = pool.map(fase3c.fase3._ancestro, [(sal, s) for s in SEMILLAS_SENSIBILIDAD])
            rs = pool.map(fase3c._correr, [(sal, n, s, 60000) for n in SENSIBILIDAD for s in SEMILLAS_SENSIBILIDAD])
            por = {}
            for r in rs:
                por.setdefault(r["nombre"], []).append(r)
            informe["sensibilidad"] = {"ancestros": anc, "hipotesis": hipotesis_sensibilidad(por),
                                       "corridas": rs}
    informe["parametros"]["minutos"] = round((time.time() - t0) / 60, 1)
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v["hipotesis"] for k, v in informe.items() if isinstance(v, dict) and "hipotesis" in v},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
