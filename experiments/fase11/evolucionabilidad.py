"""Fase 11: evolucionabilidad. Fracción de decisiones que cambia una mutación puntual de peso o sesgo (σ = 0,3 y 3),
en situaciones reales, para LUCA y poblaciones evolucionadas. Ejecutar desde la raíz:
    python experiments/fase11/evolucionabilidad.py
Resultados en docs/bitacora/2026-10-26-fase11-evaluacion.md.
"""
import sys, importlib.util, numpy as np
from simbio import config, persistencia, genoma as gen
from simbio.simulacion import Simulacion
sp = importlib.util.spec_from_file_location("evaluar_fase11", "experiments/fase11/evaluar.py")
f11 = importlib.util.module_from_spec(sp); sys.modules["evaluar_fase11"] = f11; sp.loader.exec_module(f11)
AJ = f11.MUNDO + ["estaciones.rampa_toxicidad=0", "herencia.mutacion=false", "herencia.modulacion=true"]

def medir(origen, sigma, reps=20):
    cfg = config.cargar(f11.fase9.fase7.CONFIG, AJ); cfg.sim.semilla = 1
    if origen == "luca":
        g = gen.repetir(gen.luca(cfg.herencia), 400); g["etiqueta"] = np.random.default_rng(1).random((400, 2))
    else:
        g = persistencia.cargar_genomas(origen)
        g = {k: v[np.random.default_rng(1).integers(0, len(g["mu"]), 400)] for k, v in g.items()}
    sim = Simulacion(cfg, g); sim.correr(1000)
    p = sim.pob; rng = np.random.default_rng(2)
    occ = sim.ocupacion(); s = sim.sensar(occ, sim.validar_enlaces(occ))
    guarda = {k: p[k].copy() for k in ("memoria", "senal")}
    def decide():
        a, _ = sim.decidir(s.copy())
        for k, v in guarda.items(): p[k] = v.copy()
        return a
    base = decide(); cambios = []
    w0, b0 = p["w"].copy(), p["b"].copy()
    for _ in range(reps):
        i = np.arange(p.n)
        gi = np.array([rng.choice(np.flatnonzero(p["activo"][k])) for k in i])
        if rng.random() < 0.5:
            si = rng.integers(0, gen.NUM_SENS_SIN_REALIDAD, p.n); p["w"][i, gi, si] += rng.normal(0, sigma, p.n)
        else:
            p["b"][i, gi] += rng.normal(0, sigma, p.n)
        cambios.append((decide() != base).mean())
        p["w"][:], p["b"][:] = w0, b0
    return float(np.mean(cambios)), p.n

for origen in ["luca", "resultados/fase10/sem_induccion_semilla_188.npz", "resultados/fase11/a_mod_semilla_183.npz"]:
    for sigma in (0.3, 3.0):
        f, n = medir(origen, sigma)
        print(origen.split("/")[-1], "sigma", sigma, "fracción de decisiones que cambian: %.4f" % f, "(n=%d)" % n)
