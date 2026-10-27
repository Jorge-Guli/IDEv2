"""Fase 12, etapa 4: ¿la depredación evolucionada mantiene viva la innovación? Exploratorio, desde LUCA puro.

Mundo de vivo.toml (fase 11), con mutación. Condiciones:
    ataque:  la primitiva atacar existe; si se usa, lo decide la evolución
    fijo:    el depredador fijo de la fase 2c (no evoluciona; refugio por tamaño de grupo)
    sin:     sin depredación (el universo vivo de la etapa 1)
La hipótesis de la Reina Roja: con un ambiente que evoluciona, la tasa de mutación no colapsa y la diversidad de
genomas se mantiene. Se reportan series cada 20 000 pasos y extinciones.

Uso (desde la raíz):  python experiments/fase12/reina_roja.py --pasos 200000 --semillas 1 2
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
CONDICIONES = {
    "ataque": ["ataque.activo=true"],
    "fijo": ["depredacion.activa=true", "depredacion.rampa=20000"],
    "sin": [],
}
CLAVES = ["poblacion", "generacion_media", "tasa_efectiva_media", "mu_media", "perfiles_distintos", "genes_medios",
          "tiene_atacar", "usa_atacar", "muertes_por_ataque", "frac_enlazados", "grupos_de_3_o_mas",
          "acierto_comida", "tiene_memoria_a", "frac_depredadores", "uso_comer_depredadores", "uso_comer_presas"]


def correr(tarea):
    nombre, semilla, pasos, ajustes = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/vivo.toml",
                        CONDICIONES[nombre] + ["sim.registrar_cada=1000"] + list(ajustes))
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg)
    for _ in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            break
    serie = []
    for k in range(20, len(sim.historial) + 1, 20):  # promedio de cada bloque de 20 mediciones
        bloque = sim.historial[k - 20:k]
        fila = {"t": bloque[-1]["t"]}
        for c in CLAVES:
            v = [f[c] for f in bloque if c in f and f[c] == f[c]]
            if v:
                fila[c] = round(float(np.mean(v)), 5)
        serie.append(fila)
    return {"condicion": nombre, "semilla": semilla, "ajustes": list(ajustes),
            "extinta_en": sim.t if sim.pob.n == 0 else None, "serie": serie}


def permutacion_pareada(dif) -> float:
    """p de una cola (media > 0) por inversión de signos exacta."""
    d = np.asarray([x for x in dif if x == x], dtype=float)
    if d.size == 0:
        return float("nan")
    signos = ((np.arange(2 ** d.size)[:, None] >> np.arange(d.size)) & 1) * 2 - 1
    return float(((signos * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def final(r, clave, desde):
    """Media de una medida en los bloques con t ≥ desde (NaN si la corrida se extinguió)."""
    v = [f[clave] for f in r["serie"] if f["t"] >= desde and clave in f]
    return float(np.mean(v)) if v and r["extinta_en"] is None else float("nan")


def evaluar(res: list[dict], desde: int) -> dict:
    """Reglas prerregistradas (docs/bitacora/2026-10-27-fase12-reina-roja-prerregistro.md)."""
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({s for _, s in por})

    def prueba(a, b, clave):
        d = [final(por[a, s], clave, desde) - final(por[b, s], clave, desde) for s in semillas
             if (a, s) in por and (b, s) in por]
        d = [x for x in d if x == x]
        p = permutacion_pareada(d)
        return {"n": len(d), "diferencias": [round(x, 5) for x in d], "p_una_cola": round(p, 4),
                "cumple": bool(d) and p < 0.05}

    ext = {c: sum(por[c, s]["extinta_en"] is not None for s in semillas if (c, s) in por)
           for c in CONDICIONES}
    return {
        "R1_mutacion_ataque_vs_sin": prueba("ataque", "sin", "tasa_efectiva_media"),
        "R2_diversidad_ataque_vs_sin": prueba("ataque", "sin", "perfiles_distintos"),
        "R3_extinciones_ataque_max_2": {"extinciones": ext, "cumple": ext.get("ataque", 99) <= 2},
        "R4_mutacion_ataque_vs_fijo": prueba("ataque", "fijo", "tasa_efectiva_media"),
        "E_ataque_presente": {s: round(final(por["ataque", s], "tiene_atacar", desde), 3)
                              for s in semillas if ("ataque", s) in por},
        "E_genes_ataque_vs_sin": prueba("ataque", "sin", "genes_medios"),
    }


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--pasos", type=int, default=200_000)
    a.add_argument("--semillas", type=int, nargs="+", default=[1, 2])
    a.add_argument("--condiciones", nargs="+", default=list(CONDICIONES))
    a.add_argument("--set", action="append", default=[])
    a.add_argument("--procesos", type=int, default=6)
    a.add_argument("--salida", default="runs/fase12/reina_roja.json")
    args = a.parse_args()
    tareas = [(c, s, args.pasos, tuple(args.set)) for c in args.condiciones for s in args.semillas]
    with Pool(args.procesos) as pool:
        res = pool.map(correr, tareas)
    for r in res:
        f = r["serie"][-1] if r["serie"] else {}
        print(r["condicion"], r["semilla"], "extinta" if r["extinta_en"] else "viva",
              {k: f.get(k) for k in ("poblacion", "generacion_media", "tasa_efectiva_media", "perfiles_distintos",
                                     "tiene_atacar", "usa_atacar", "frac_enlazados")})
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    if set(args.condiciones) == set(CONDICIONES):
        informe = evaluar(res, desde=args.pasos - args.pasos // 3)  # el último tercio
        print(json.dumps(informe, ensure_ascii=False, indent=2))
        salida.with_name(salida.stem + "_informe.json").write_text(
            json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
