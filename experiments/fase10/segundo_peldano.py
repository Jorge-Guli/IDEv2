"""Fase 10: ¿se premia la conducta condicionada (segundo peldaño) en poblaciones que ya tienen memoria?

Agrega a las poblaciones finales de `sem_induccion` (181, 183, 186, 188; `resultados/fase10/`) los genes de
`invadir_memoria.GENES_REGULADOS` indicados por índice (1–2: comer condicionado; 3–4: avanzar condicionado), contra
un control con los mismos genes en cero. Sin mutación, 20 000 pasos, semillas 1–2. Ejecutar desde la raíz:
    python experiments/fase10/segundo_peldano.py 3 4
    EXTRA="estaciones.induccion=0.0" python experiments/fase10/segundo_peldano.py 1 2 3 4
Resultados en docs/bitacora/2026-10-26-fase10-evaluacion.md.
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
AJ = f10.fase9.BASE + f10.CONDICIONES["sem_induccion"] + ["estaciones.rampa_toxicidad=0", "herencia.mutacion=false"] + os.environ.get("EXTRA", "").split()
def correr(t):
    pob, sub, semilla = t
    genes = [inv.GENES_REGULADOS[k] for k in sub]
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
sub = tuple(int(x) for x in sys.argv[1:])
tareas = [(p, sub, s) for p in (181, 183, 186, 188) for s in (1, 2)]
with Pool(4) as pool:
    rs = pool.map(correr, tareas)
print("genes", sub, [(t[0], r) for t, r in zip(tareas, rs)])
