"""Fase 11: modulación por el estado interno. ¿La memoria evolucionada se recluta para decidir?

Mundo de la fase 10 (mosaico, toxicidad diferida, pista 0,01, memoria tipo cerrojo, digestión inducible con inercia),
con dos cambios:
    modulación     la condición de un gen puede ser "entrada modulada por la memoria A/B": z = b + (2m − 1)·w·s.
                   Un solo gen "avanzar si el tipo de comida no coincide con la memoria" cabe en un gen
    memoria inicial 0,5 (sin información, el estado digestivo queda neutro en cada estación; en la fase 10, con 0,
                   los controles sin memoria absorbían más veneno en una estación y se extinguían)
Competencias previas (poblaciones evolucionadas de la fase 10, sin mutación): dos genes modulados de avanzar ganan
en 7/8; con uno de comer, 8/8; uno solo de avanzar, 2/8; sin modulación, el módulo equivalente ganaba 0–2/8.

Parte A (desde las poblaciones finales de `sem_induccion` de la fase 10 que tienen memoria, `resultados/fase10/`):
    a_mod           con modulación
    a_sin_mod       sin modulación (control)
    a_mod_softmax, a_sin_mod_softmax   lo mismo con decisión estocástica (softmax, temperatura 0,25): un cambio chico
                   de impulso cambia un poco la probabilidad de cada acción (gradiente para la selección)
Parte B (desde LUCA sembrado con un gen de memoria A conectado a la pista, como la fase 10):
    b_mod           con modulación
    b_sin_mod       sin modulación (control)
    b_ruido_mod     con modulación y la pista aleatoria (control: la memoria no informa)

Uso:
    python experiments/fase11/evaluar.py --salida runs/fase11 [--procesos 8] [--pasos-a 300000] [--pasos-b 300000]
        [--semillas 8] [--semilla-inicial 191] [--partes A] [--extra ...]
        [--mu-inicial 0.02] [--condiciones-a a_mod a_sin_mod]
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
_spec = importlib.util.spec_from_file_location("evaluar_fase10", RAIZ / "experiments" / "fase10" / "evaluar.py")
fase10 = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase10"] = fase10
_spec.loader.exec_module(fase10)
fase9 = fase10.fase9

MUNDO = fase9.BASE + fase10.CERROJO + fase10.INDUCCION + ["memoria.inicial=0.5"]
MOD = ["herencia.modulacion=true"]
RUIDO = ["estaciones.pista_informativa=false"]
SOFTMAX = ['fisica.decision="softmax"', "fisica.temperatura=0.25"]
CONDICIONES_A = {"a_mod": MOD, "a_sin_mod": [], "a_mod_softmax": MOD + SOFTMAX, "a_sin_mod_softmax": SOFTMAX}
CONDICIONES_B = {"b_mod": MOD, "b_sin_mod": [], "b_ruido_mod": MOD + RUIDO}
# poblaciones de la fase 10 cuya memoria sigue a la pista (la 182 evolucionó el atajo del tipo; la 185 se extinguió)
POBLACIONES_A = [181, 183, 184, 186, 187, 188]


def _correr_a(tarea):
    salida, nombre, pob, pasos, extra, mu = tarea
    g = persistencia.cargar_genomas(RAIZ / "resultados" / "fase10" / f"sem_induccion_semilla_{pob}.npz")
    if mu:  # etapa 0 de la fase 12: tasa de mutación reiniciada (en las poblaciones de partida había colapsado)
        g["mu"][:] = mu
    idx = np.random.default_rng(pob).integers(0, len(g["mu"]), 600)
    cfg = config.cargar(fase9.fase7.CONFIG, MUNDO + CONDICIONES_A[nombre] + ["estaciones.rampa_toxicidad=0"] + list(extra))
    cfg.sim.semilla, cfg.sim.pasos = pob, pasos
    sim = corrida.correr(cfg, Path(salida) / nombre / f"semilla_{pob}", genomas={k: v[idx] for k, v in g.items()},
                         imagenes=False)
    return resumen(sim, nombre, pob, pasos)


def _correr_b(tarea):
    salida, nombre, semilla, pasos, extra = tarea
    return fase9.correr_condicion(salida, nombre, semilla, pasos, MUNDO + CONDICIONES_B[nombre] + list(extra), True)


def resumen(sim, nombre, semilla, pasos):
    h = sim.historial
    res = {"nombre": nombre, "semilla": semilla, "extinta": sim.pob.n == 0,
           "generacion_final": float(h[-1].get("generacion_media", np.nan))}

    def media(v):
        return float(np.nanmean(v)) if v.size and not np.isnan(v).all() else float("nan")
    for parte, (a, b) in (("final", (0.75, 1.0)), ("medio", (0.25, 0.5))):
        filas = [r for r in h if a * pasos <= r["t"] <= b * pasos]
        f = lambda k: np.array([r.get(k, np.nan) for r in filas], dtype=float)  # noqa: E731
        res[f"acierto_{parte}"] = media(f("acierto_comida"))
        res[f"poblacion_{parte}"] = media(f("poblacion"))
        res[f"seguimiento_{parte}"] = max([fase9.fase7.fase_seguimiento(f(f"memoria_alineada_{c}"), f("estacion"))
                                           for c in "ab"], key=lambda v: abs(v) if v == v else -1.0)
        per = sim.cfg.estaciones.periodo  # versión sin el aliasing de muestreo (ver fase_seguimiento)
        res[f"seguimiento_corregido_{parte}"] = max(
            [fase9.fase7.fase_seguimiento(f(f"memoria_alineada_{c}"), f("estacion"), f("t"), per) for c in "ab"],
            key=lambda v: abs(v) if v == v else -1.0)
        res[f"con_gen_condicionado_{parte}"] = media(f("con_gen_condicionado"))
    return res


def hipotesis(rs):
    """Reglas prerregistradas (docs/bitacora/2026-10-26-fase11-prerregistro.md)."""
    def val(n, m):
        return {r["semilla"]: r[m] for r in rs if r["nombre"] == n and not r["extinta"] and r[m] == r[m]}

    def prueba(a, b, m):
        va, vb = val(a, m), val(b, m)
        comunes = sorted(set(va) & set(vb))
        d = [va[s] - vb[s] for s in comunes]
        p = fase9.fase7.fase4.permutacion_pareada(d)
        return {"n": len(d), "diferencias": [round(x, 3) for x in d], "p_una_cola": round(p, 4),
                "cumple": bool(d) and p < 0.05}

    def umbral(n, m, u, k):
        v = val(n, m)
        return {"valores": {s: round(x, 3) for s, x in v.items()}, "cumple": sum(x > u for x in v.values()) >= k}
    return {
        "A1_acierto_mod_vs_sin_mod": prueba("a_mod", "a_sin_mod", "acierto_final"),
        "A2_acierto_mod_mayor_a_060": umbral("a_mod", "acierto_final", 0.6, 3),
        "A3_acierto_mod_vs_sin_mod_softmax": prueba("a_mod_softmax", "a_sin_mod_softmax", "acierto_final"),
        "A4_acierto_mod_softmax_mayor_a_060": umbral("a_mod_softmax", "acierto_final", 0.6, 3),
        "B1_acierto_mod_vs_sin_mod": prueba("b_mod", "b_sin_mod", "acierto_final"),
        "B2_acierto_mod_vs_ruido": prueba("b_mod", "b_ruido_mod", "acierto_final"),
        "B3_acierto_mod_mayor_a_060": umbral("b_mod", "acierto_final", 0.6, 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase11")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos-a", type=int, default=300000)
    ap.add_argument("--pasos-b", type=int, default=300000)
    ap.add_argument("--semillas", type=int, default=8)
    ap.add_argument("--semilla-inicial", type=int, default=191)
    ap.add_argument("--partes", nargs="*", default=["A"])
    ap.add_argument("--poblaciones", type=int, nargs="*", default=POBLACIONES_A)
    ap.add_argument("--extra", nargs="*", default=[], help="ajustes seccion.clave=valor para todas las condiciones")
    ap.add_argument("--mu-inicial", type=float, default=0.0,
                    help="parte A: reiniciar la tasa de mutación de los genomas de partida (0 = la evolucionada)")
    ap.add_argument("--condiciones-a", nargs="*", default=list(CONDICIONES_A))
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    t0 = time.time()
    rs = []
    with Pool(args.procesos) as pool:
        if "A" in args.partes:
            rs += pool.map(_correr_a, [(str(args.salida), n, p, args.pasos_a, tuple(args.extra), args.mu_inicial)
                                       for n in args.condiciones_a
                                       for p in args.poblaciones])
        if "B" in args.partes:
            rs += pool.map(_correr_b, [(str(args.salida), n, s, args.pasos_b, tuple(args.extra)) for n in CONDICIONES_B for s in semillas])
    informe = {"parametros": {"pasos_a": args.pasos_a, "pasos_b": args.pasos_b, "semillas": semillas,
                              "poblaciones": args.poblaciones, "extra": args.extra,
                              "mu_inicial": args.mu_inicial, "condiciones_a": args.condiciones_a, "minutos": round((time.time() - t0) / 60, 1)},
               "hipotesis": hipotesis(rs), "corridas": rs}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["hipotesis"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
