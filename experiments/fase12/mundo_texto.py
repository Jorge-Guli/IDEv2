"""Fase 12: mundo del texto. ¿La evolución aprovecha la estructura de un texto real para predecir la letra vigente?

Mundo de vivo.toml (fase 11), desde LUCA. La estación la decide un texto: vocal nutre el tipo A, consonante el B; cada
letra dura `--pasos-por-letra` pasos y el sensor "pista" muestra la letra anterior. Condiciones:
    texto:    las letras en su orden
    barajado: las mismas letras en orden al azar (control: mismas frecuencias, sin secuencia)
En los textos en castellano, una vocal sigue a una consonante (y al revés) ~76 % de las veces. Quien "invierte" la
pista acierta ~0,76 en el texto; en el barajado nada supera la frecuencia base (~0,55). Seguir la pista da ~0,24.

Uso (desde la raíz):  python experiments/fase12/mundo_texto.py --pasos 100000 --semillas 1 2 --archivos docs/00-hipotesis-fundacional.md
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
CONDICIONES = {"texto": [], "barajado": ["texto.barajar=true"]}
CLAVES = ["poblacion", "generacion_media", "tasa_efectiva_media", "genes_medios", "acierto_comida",
          "tiene_memoria_a", "memoria_alineada_a", "perfiles_distintos"]


def correr(tarea):
    nombre, semilla, pasos, archivos, ppl, ajustes = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/vivo.toml",
                        ["texto.activo=true", f"texto.archivos={archivos}", f"texto.pasos_por_letra={ppl}",
                         "sim.registrar_cada=1000", *ajustes, *CONDICIONES[nombre]])
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg)
    for _ in range(pasos):
        sim.paso()
        if sim.pob.n == 0:
            break
    serie = []
    for k in range(20, len(sim.historial) + 1, 20):
        bloque = sim.historial[k - 20:k]
        fila = {"t": bloque[-1]["t"]}
        for c in CLAVES:
            v = [f[c] for f in bloque if c in f and f[c] == f[c]]
            if v:
                fila[c] = round(float(np.mean(v)), 5)
        serie.append(fila)
    return {"condicion": nombre, "semilla": semilla, "textos": sim.texto.meta,
            "extinta_en": sim.t if sim.pob.n == 0 else None, "serie": serie}


def permutacion_pareada(dif) -> float:
    """p de una cola (media > 0) por inversión de signos exacta."""
    d = np.asarray([x for x in dif if x == x], dtype=float)
    if d.size == 0:
        return float("nan")
    signos = ((np.arange(2 ** d.size)[:, None] >> np.arange(d.size)) & 1) * 2 - 1
    return float(((signos * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def final(r, clave, desde):
    v = [f[clave] for f in r["serie"] if f["t"] >= desde and clave in f]
    return float(np.mean(v)) if v and r["extinta_en"] is None else float("nan")


def evaluar(res, desde):
    por = {(r["condicion"], r["semilla"]): r for r in res}
    semillas = sorted({s for _, s in por})
    out = {}
    for regla, clave in (("R1_acierto_comida", "acierto_comida"), ("E_memoria_tiene", "tiene_memoria_a"),
                         ("E_genes", "genes_medios"), ("E_poblacion", "poblacion")):
        d = [final(por["texto", s], clave, desde) - final(por["barajado", s], clave, desde) for s in semillas
             if ("texto", s) in por and ("barajado", s) in por]
        d = [x for x in d if x == x]
        p = permutacion_pareada(d)
        out[regla] = {"n": len(d), "diferencias": [round(x, 4) for x in d], "p_una_cola": round(p, 4),
                      "cumple": bool(d) and p < 0.05}
    out["R2_acierto_texto_sobre_base"] = {s: round(final(por["texto", s], "acierto_comida", desde), 4)
                                          for s in semillas if ("texto", s) in por}
    out["extinciones"] = {c: sum(por[c, s]["extinta_en"] is not None for s in semillas if (c, s) in por)
                          for c in CONDICIONES}
    return out


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--pasos", type=int, default=100_000)
    a.add_argument("--semillas", type=int, nargs="+", default=[1, 2])
    a.add_argument("--archivos", default="datos/textos/la_ultima_pregunta.txt,datos/textos/la_ultima_respuesta.txt")
    a.add_argument("--pasos-por-letra", type=int, default=500)
    a.add_argument("--set", action="append", default=[])
    a.add_argument("--procesos", type=int, default=6)
    a.add_argument("--salida", default="runs/fase12/mundo_texto.json")
    args = a.parse_args()
    tareas = [(c, s, args.pasos, args.archivos, args.pasos_por_letra, tuple(args.set))
              for c in CONDICIONES for s in args.semillas]
    with Pool(args.procesos) as pool:
        res = pool.map(correr, tareas)
    for r in res:
        f = r["serie"][-1] if r["serie"] else {}
        print(r["condicion"], r["semilla"], "extinta" if r["extinta_en"] else "viva",
              {k: f.get(k) for k in ("t", "poblacion", "acierto_comida", "tiene_memoria_a", "memoria_alineada_a")})
    informe = evaluar(res, args.pasos - args.pasos // 3)
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps({"corridas": res, "reglas": informe}, ensure_ascii=False, indent=2),
                      encoding="utf-8")


if __name__ == "__main__":
    main()
