"""Fase 11: competencia de genes modulados por la memoria ("c": comer, "a": avanzar) agregados a las poblaciones
de la fase 10 con memoria (181, 183, 186, 188), contra un control con los mismos genes en cero. Sin mutación,
20 000 pasos, semillas 1–2. Ejecutar desde la raíz:
    python experiments/fase11/genes_modulados.py a a
    python experiments/fase11/genes_modulados.py c a a
Resultados en docs/bitacora/2026-10-26-fase11-prerregistro.md.
"""
import sys, importlib.util
sys.path.insert(0, "experiments/fase7")
from multiprocessing import Pool
import numpy as np
import invadir_memoria as inv
from simbio import config, persistencia
from simbio import dispositivo as dev
from simbio.simulacion import Simulacion
sp = importlib.util.spec_from_file_location("evaluar_fase10", "experiments/fase10/evaluar.py")
f10 = importlib.util.module_from_spec(sp); sys.modules["evaluar_fase10"] = f10; sp.loader.exec_module(f10)
import os
AJ = f10.fase9.BASE + f10.CONDICIONES["sem_induccion"] + ["estaciones.rampa_toxicidad=0", "herencia.mutacion=false"] + os.environ.get("EXTRA", "").split() + ["herencia.modulacion=true"]
from simbio import genoma as gen
MOD = {"c": (gen.COMER, -5.0, {gen.S_TIPO_AQUI: 5.0}, gen.COND_MODULA_A),      # + si coincide, − si no
       "a": (gen.AVANZAR, 5.0, {gen.S_TIPO_AQUI: -5.0}, gen.COND_MODULA_A)}   # − si coincide, + si no
def correr(t):
    pob, sub, semilla = t
    genes = [MOD[k] for k in sub]
    g = persistencia.cargar_genomas(f"resultados/fase10/sem_induccion_semilla_{pob}.npz")
    caben = np.flatnonzero((~g["activo"]).sum(axis=1) >= len(genes))
    idx = caben[np.random.default_rng(semilla).integers(0, caben.size, 600)]
    g = {k: v[idx].copy() for k, v in g.items()}
    cep = np.zeros(600, dtype=np.int16); cep[:300] = 1
    a = {k: v[:300] for k, v in g.items()}; inv.agregar(a, True, genes)
    b = {k: v[300:] for k, v in g.items()}; inv.agregar(b, False, genes)
    for k in g: g[k][:300], g[k][300:] = a[k], b[k]
    cfg = config.cargar(f10.fase9.fase7.CONFIG, AJ); cfg.sim.semilla = semilla
    sim = Simulacion(cfg, g, cep)
    for _ in range(20000):
        sim.paso()
    c = dev.a_cpu(sim.pob["cepa"]); n0, n1 = int((c == 0).sum()), int((c == 1).sum())
    return None if n0 + n1 == 0 else round(n1 / (n0 + n1), 2)
sub = tuple(sys.argv[1:])
tareas = [(p, sub, s) for p in (181, 183, 186, 188) for s in (1, 2)]
with Pool(4) as pool:
    rs = pool.map(correr, tareas)
print("genes", sub, [(t[0], r) for t, r in zip(tareas, rs)])
