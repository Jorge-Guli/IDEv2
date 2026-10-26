"""Fase 10: duelo directo, memoria escrita con la pista (cepa 1) contra memoria escrita con el tipo de comida de la
celda (cepa 0, el atajo). Mundo mosaico, rampa de toxicidad de 5000 pasos, cerrojo, sin mutación, 30 000 pasos,
semillas 1–8. Ejecutar desde la raíz:
    python experiments/fase10/duelo_pista_tipo.py estaciones.induccion=0.25 estaciones.inercia_digestion=100
Resultados en docs/bitacora/2026-10-26-fase10-prerregistro.md.
"""
import sys
sys.path.insert(0, "experiments/fase7")
from multiprocessing import Pool
import numpy as np
import invadir_memoria as inv, luca_memoria as lm
from simbio import config, genoma as gen
from simbio import dispositivo as dev
from simbio.simulacion import Simulacion
PISTA = [(gen.MEMORIA_A, 0.0, {gen.S_PISTA: 20.0}, 0)]
TIPO = [(gen.MEMORIA_A, 0.0, {gen.S_TIPO_AQUI: 2.5}, 0)]
def correr(t):
    semilla, extra = t
    cfg = config.cargar(lm.fase7.CONFIG, lm.AJUSTES + ["estaciones.castigo=0.2"] + list(extra))
    cfg.sim.semilla = semilla
    n = cfg.sim.poblacion_inicial
    g = gen.repetir(gen.luca(cfg.herencia), n)
    g["etiqueta"] = np.random.default_rng(semilla).random((n, 2))
    cepas = np.zeros(n, dtype=np.int16); cepas[: n // 2] = 1
    a = {k: v[: n // 2] for k, v in g.items()}; inv.agregar(a, True, PISTA)
    b = {k: v[n // 2:] for k, v in g.items()}; inv.agregar(b, True, TIPO)
    for k in g: g[k][: n // 2], g[k][n // 2:] = a[k], b[k]
    sim = Simulacion(cfg, g, cepas)
    for _ in range(30000):
        sim.paso()
    c = dev.a_cpu(sim.pob["cepa"]); n0, n1 = int((c == 0).sum()), int((c == 1).sum())
    return None if n0 + n1 == 0 else n1 / (n0 + n1)
extra = ("estaciones.escala_parche=1.0", "estaciones.rampa_toxicidad=5000", "memoria.umbral=0.5") + tuple(sys.argv[1:])
with Pool(4) as p:
    rs = p.map(correr, [(s, extra) for s in range(1, 9)])
print("frac pista", sys.argv[1:], " ".join("x" if r is None else f"{r:.2f}" for r in rs))
