import numpy as np

from simbio import genoma as gen
from simbio.simulacion import Simulacion

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con


def test_hijo_nace_sin_aprendizaje(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=60)
    sim.pob["P"][:] = 0.7
    sim.pob["p"][:] = 0.7
    sim.paso()
    assert sim.pob.n == 2
    assert np.all(sim.pob["P"][1] == 0) and np.all(sim.pob["p"][1] == 0)


def test_accion_recompensada_se_refuerza(cfg):
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.COMER, 0.5, {}), (gen.AVANZAR, 0.4, {})])
    g["eta"][0] = 0.5
    colocar(sim, g, [5], [5], E=30)
    sim.entorno.K_base[:] = 0
    sim.entorno.R[:] = 0
    sim.entorno.R[5, 5] = sim.entorno.K_base[5, 5] = 4.0
    sim.paso()  # come: gana mucho más que su línea base
    assert sim.pob["ult_act"][0] == gen.COMER
    sim.aprender()
    assert sim.pob["p"][0, 0] > 0  # el gen de comer aumentó su respuesta
    assert sim.pob["p"][0, 1] == 0  # el otro gen no cambió


def test_aprendizaje_desactivado(cfg):
    cfg.aprendizaje.activo = False
    sim = Simulacion(cfg)
    sim.correr(200)
    assert np.all(sim.pob["P"] == 0) and np.all(sim.pob["p"] == 0)


def test_division_no_altera_la_linea_base(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=60)
    sim.entorno.R[:] = 0
    sim.paso()  # se divide
    sim.aprender()
    assert sim.pob["linea_base"][0] == 0.0
    assert sim.pob["delta_e"][0] == 0.0
