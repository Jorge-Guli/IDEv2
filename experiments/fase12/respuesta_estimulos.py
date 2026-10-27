"""Fase 12, etapa 3: ¿el universo responde a lo que le dice Claude? Experimento con control.

Mundo de clima.toml con estímulos. Cada `--cada` pasos, Claude le manda la frase siguiente de una conversación fija
(FRASES, en ciclo): cada letra enciende un lugar. Condiciones:
    acoplado:    la luz hace crecer comida (estimulos.acople_luz = 0,05)
    desacoplado: la misma luz, en los mismos lugares y pasos, sin efecto (acople 0): control
Medidas (promedio de la segunda mitad):
    enriquecimiento  fracción de organismos en celdas con luz / fracción de celdas con luz (1: indiferentes)
    peso_luz         |peso| medio sobre el sensor de luz en los genes activos de avanzar, comer y girar; en el
                     desacoplado mide la deriva (el sensor no informa nada útil)
    peso_ruido       lo mismo sobre el sensor de ruido (referencia de deriva dentro de cada corrida)

Uso (desde la raíz):  python experiments/fase12/respuesta_estimulos.py --pasos 150000 --semillas 1 2 3 4
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config
from simbio import dispositivo as dev
from simbio import genoma as gen
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
FRASES = ["hola, soy Claude", "Jorge te mira desde Capitan Bermudez", "la luz trae comida",
          "seguí la luz", "llueve en la pampa", "buenas noches"]
CONDICIONES = {"acoplado": [], "desacoplado": ["estimulos.acople_luz=0.0"]}
PRIM_MIRADAS = [gen.AVANZAR, gen.COMER, gen.GIRAR_IZQ, gen.GIRAR_DER]


def pesos(sim, sensor):
    p = sim.pob
    activo = dev.a_cpu(p["activo"]) & np.isin(dev.a_cpu(p["prim"]), PRIM_MIRADAS)
    w = dev.a_cpu(p["w"])[:, :, sensor][activo]
    return float(np.abs(w).mean()) if w.size else float("nan")


def peso_con_signo(sim, prim, sensor):
    """Peso medio (con signo) sobre un sensor en los genes activos de una primitiva."""
    p = sim.pob
    activo = dev.a_cpu(p["activo"]) & (dev.a_cpu(p["prim"]) == prim)
    w = dev.a_cpu(p["w"])[:, :, sensor][activo]
    return float(w.mean()) if w.size else float("nan")


def permutacion_pareada(dif) -> float:
    """p de una cola (media > 0) por inversión de signos exacta (como en las fases 3d y 4)."""
    d = np.asarray([x for x in dif if x == x], dtype=float)
    if d.size == 0:
        return float("nan")
    signos = ((np.arange(2 ** d.size)[:, None] >> np.arange(d.size)) & 1) * 2 - 1
    return float(((signos * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def evaluar(res: list[dict]) -> dict:
    """Reglas prerregistradas (docs/bitacora/2026-10-27-fase12-luz-prerregistro.md)."""
    por = {(r["condicion"], r["semilla"]): r for r in res if r.get("extinta_en") is None}
    semillas = sorted({s for c, s in por if c == "acoplado"} & {s for c, s in por if c == "desacoplado"})
    out = {}
    for regla, medida in (("R1_peso_luz", "peso_luz"), ("R2_enriquecimiento", "enriquecimiento"),
                          ("E_peso_ruido", "peso_ruido"), ("E_avanzar_luz", "avanzar_luz"),
                          ("E_comer_luz", "comer_luz")):
        d = [por["acoplado", s][medida] - por["desacoplado", s][medida] for s in semillas]
        p = permutacion_pareada(d)
        out[regla] = {"n": len(d), "diferencias": [round(x, 3) for x in d], "p_una_cola": round(p, 4),
                      "cumple": bool(d) and p < 0.05}
    return out


def correr(tarea):
    nombre, semilla, pasos, cada = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/clima.toml",
                        ["estimulos.activo=true", "sim.registrar_cada=500"] + CONDICIONES[nombre])
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg)
    k = 0
    for _ in range(pasos):
        if sim.t % cada == 0:
            sim.estimular({"tipo": "texto", "texto": FRASES[k % len(FRASES)]})
            k += 1
        sim.paso()
        if sim.pob.n == 0:
            return {"condicion": nombre, "semilla": semilla, "extinta_en": sim.t}
    h = [f for f in sim.historial[len(sim.historial) // 2:] if f.get("frac_celdas_con_luz", 0) > 0.005]
    enr = [f["frac_en_luz"] / f["frac_celdas_con_luz"] for f in h]
    return {"condicion": nombre, "semilla": semilla, "extinta_en": None, "frases": k,
            "enriquecimiento": float(np.mean(enr)) if enr else float("nan"),
            "poblacion": float(np.mean([f["poblacion"] for f in h])) if h else float("nan"),
            "peso_luz": pesos(sim, gen.S_LUZ), "peso_ruido": pesos(sim, gen.S_RUIDO),
            "avanzar_luz": peso_con_signo(sim, gen.AVANZAR, gen.S_LUZ),
            "comer_luz": peso_con_signo(sim, gen.COMER, gen.S_LUZ),
            "generacion": float(dev.a_cpu(sim.pob["generacion"]).mean())}


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--pasos", type=int, default=150_000)
    a.add_argument("--semillas", type=int, nargs="+", default=[1, 2, 3, 4])
    a.add_argument("--cada", type=int, default=3000)
    a.add_argument("--procesos", type=int, default=8)
    a.add_argument("--salida", default="runs/fase12/respuesta_estimulos.json")
    args = a.parse_args()
    tareas = [(c, s, args.pasos, args.cada) for c in CONDICIONES for s in args.semillas]
    with Pool(args.procesos) as pool:
        res = pool.map(correr, tareas)
    for r in res:
        print(json.dumps(r, ensure_ascii=False))
    informe = evaluar(res)
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    salida = RAIZ / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps({"corridas": res, "reglas": informe}, ensure_ascii=False, indent=2),
                      encoding="utf-8")


if __name__ == "__main__":
    main()
