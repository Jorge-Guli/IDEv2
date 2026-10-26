"""Fase 10: diagnóstico de qué hace el módulo condicionado completo dentro de una población evolucionada
(fracción de acciones de comer comida buena y mala, avanzar y descansar, por cepa). Ejecutar desde la raíz:
    python experiments/fase10/diagnostico_modulo.py 188
"""
import sys, importlib.util, numpy as np
sys.path.insert(0, "experiments/fase7")
import invadir_memoria as inv
from simbio import config, persistencia, genoma as gen
from simbio.simulacion import Simulacion
sp = importlib.util.spec_from_file_location("evaluar_fase10", "experiments/fase10/evaluar.py")
f10 = importlib.util.module_from_spec(sp); sys.modules["evaluar_fase10"] = f10; sp.loader.exec_module(f10)
AJ = f10.fase9.BASE + f10.CONDICIONES["sem_induccion"] + ["estaciones.rampa_toxicidad=0", "herencia.mutacion=false"]
pob = int(sys.argv[1]); genes = [inv.GENES_REGULADOS[k] for k in (1, 2, 3, 4)]
g = persistencia.cargar_genomas(f"resultados/fase10/sem_induccion_semilla_{pob}.npz")
caben = np.flatnonzero((~g["activo"]).sum(axis=1) >= len(genes))
idx = caben[np.random.default_rng(1).integers(0, caben.size, 600)]
g = {k: v[idx].copy() for k, v in g.items()}
cep = np.zeros(600, dtype=np.int16); cep[:300] = 1
a = {k: v[:300] for k, v in g.items()}; inv.agregar(a, True, genes)
b = {k: v[300:] for k, v in g.items()}; inv.agregar(b, False, genes)
for k in g: g[k][:300], g[k][300:] = a[k], b[k]
cfg = config.cargar(f10.fase9.fase7.CONFIG, AJ); cfg.sim.semilla = 1
sim = Simulacion(cfg, g, cep)
st = {c: np.zeros(5) for c in (0, 1)}  # comer_buena, comer_mala, avanzar, descansar, pasos
for t in range(3000):
    occ = sim.ocupacion(); s = sim.sensar(occ, sim.validar_enlaces(occ))
    act, _ = sim.decidir(s.copy())
    p = sim.pob; tp = sim.tipo[p["y"], p["x"]] * sim.estacion() > 0
    for c in (0, 1):
        m = p["cepa"] == c
        st[c] += [((act == gen.COMER) & tp & m).sum(), ((act == gen.COMER) & ~tp & m).sum(),
                  ((act == gen.AVANZAR) & m).sum(), ((act == gen.DESCANSAR) & m).sum(), m.sum()]
    sim.paso()
    if t % 1000 == 999:
        print(t + 1, {c: int((sim.pob["cepa"] == c).sum()) for c in (0, 1)},
              {c: float(sim.pob["E"][sim.pob["cepa"] == c].mean()) if (sim.pob["cepa"] == c).any() else None for c in (0, 1)})
for c in (0, 1):
    v = st[c]; print("cepa", c, "comer_buena %.3f comer_mala %.3f avanzar %.3f descansar %.3f" % tuple(v[:4] / v[4]))
