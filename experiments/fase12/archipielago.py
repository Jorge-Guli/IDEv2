"""Fase 12, etapa 5: ¿la migración entre islas mantiene viva la innovación? Archipiélago contra islas aisladas.

Mundo de vivo.toml (fase 11), desde LUCA, partido en `--islas` islas de lado `--lado`. El área total queda cerca de la
de un universo de 128 × 128. Condiciones:
    migracion: cada `--cada` pasos, `--migrantes` organismos de cada isla pasan a la siguiente (anillo)
    aisladas:  las mismas islas, con las mismas semillas, sin migración (control)
Medidas: promedio de las islas vivas en cada bloque de 20 mediciones; extinciones de islas.

Uso (desde la raíz):  python experiments/fase12/archipielago.py --pasos 60000 --semillas 1 2
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config
from simbio.archipielago import Archipielago
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
CLAVES = ["poblacion", "generacion_media", "tasa_efectiva_media", "mu_media", "perfiles_distintos", "genes_medios",
          "acierto_comida", "tiene_memoria_a", "frac_enlazados", "grupos_de_3_o_mas"]


def correr(tarea):
    nombre, semilla, pasos, islas, lado, migrantes, cada, ajustes = tarea
    sims = []
    for i in range(islas):
        cfg = config.cargar(RAIZ / "experiments/configs/vivo.toml",
                            [f"mundo.alto={lado}", f"mundo.ancho={lado}", "sim.registrar_cada=1000",
                             f"sim.poblacion_inicial={max(20, 200 * lado * lado // (128 * 128))}", *ajustes])
        cfg.sim.semilla = semilla * 100 + i
        sims.append(Simulacion(cfg))
    a = Archipielago(sims, migrantes if nombre == "migracion" else 0, cada, semilla)
    extinta_en = [None] * islas
    for _ in range(pasos):
        a.paso()
        for i, s in enumerate(sims):
            if s.pob.n == 0 and extinta_en[i] is None:
                extinta_en[i] = a.t
        if all(s.pob.n == 0 for s in sims):
            break
    serie = []
    largo = min(len(s.historial) for s in sims)
    for k in range(20, largo + 1, 20):
        fila = {"t": sims[0].historial[k - 1]["t"]}
        for c in CLAVES:
            v = [np.mean([f[c] for f in s.historial[k - 20:k] if c in f and f[c] == f[c]] or [np.nan])
                 for s in sims if s.historial[k - 1].get("poblacion", 0) > 0]
            v = [x for x in v if x == x]
            if v:
                fila[c] = round(float(np.mean(v)), 5)
        serie.append(fila)
    return {"condicion": nombre, "semilla": semilla, "migrados": a.migrados, "extinta_en": extinta_en,
            "vivas": sum(s.pob.n > 0 for s in sims), "serie": serie}


def permutacion_pareada(dif) -> float:
    """p de una cola (media > 0) por inversión de signos exacta."""
    d = np.asarray([x for x in dif if x == x], dtype=float)
    if d.size == 0:
        return float("nan")
    signos = ((np.arange(2 ** d.size)[:, None] >> np.arange(d.size)) & 1) * 2 - 1
    return float(((signos * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def final(r, clave, desde):
    v = [f[clave] for f in r["serie"] if f["t"] >= desde and clave in f]
    return float(np.mean(v)) if v else float("nan")


def evaluar(res, desde, reglas):
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({s for _, s in por})
    out = {}
    for nombre, clave in reglas:
        d = [final(por["migracion", s], clave, desde) - final(por["aisladas", s], clave, desde) for s in semillas
             if ("migracion", s) in por and ("aisladas", s) in por]
        d = [x for x in d if x == x]
        p = permutacion_pareada(d)
        out[nombre] = {"n": len(d), "diferencias": [round(x, 5) for x in d], "p_una_cola": round(p, 4),
                       "cumple": bool(d) and p < 0.05}
    out["islas_extintas"] = {c: sum(sum(e is not None for e in por[c, s]["extinta_en"]) for s in semillas
                                    if (c, s) in por) for c in ("migracion", "aisladas")}
    return out


REGLAS = [("R1_acierto_comida", "acierto_comida"), ("R2_tasa_mutacion", "tasa_efectiva_media"),
          ("E_perfiles", "perfiles_distintos"), ("E_genes", "genes_medios"), ("E_poblacion", "poblacion"),
          ("E_enlazados", "frac_enlazados")]


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--pasos", type=int, default=60_000)
    a.add_argument("--semillas", type=int, nargs="+", default=[1, 2])
    a.add_argument("--islas", type=int, default=3)
    a.add_argument("--lado", type=int, default=74)
    a.add_argument("--migrantes", type=int, default=2)
    a.add_argument("--cada", type=int, default=1000)
    a.add_argument("--set", action="append", default=[])
    a.add_argument("--procesos", type=int, default=6)
    a.add_argument("--salida", default="runs/fase12/archipielago.json")
    args = a.parse_args()
    tareas = [(c, s, args.pasos, args.islas, args.lado, args.migrantes, args.cada, tuple(args.set))
              for c in ("migracion", "aisladas") for s in args.semillas]
    with Pool(args.procesos) as pool:
        res = pool.map(correr, tareas)
    for r in res:
        f = r["serie"][-1] if r["serie"] else {}
        print(r["condicion"], r["semilla"], "vivas", r["vivas"], "migrados", r["migrados"],
              {k: f.get(k) for k in ("poblacion", "acierto_comida", "tasa_efectiva_media", "perfiles_distintos",
                                     "genes_medios")})
    informe = evaluar(res, args.pasos - args.pasos // 3, REGLAS)  # el último tercio
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps({"corridas": res, "reglas": informe}, ensure_ascii=False, indent=2),
                      encoding="utf-8")


if __name__ == "__main__":
    main()
