"""Memoria de contexto (fase 7): dos tipos de comida, estación oculta que decide cuál nutre, pista intermitente."""
import numpy as np

from simbio import genoma as gen

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con


def _cfg(cfg, p_pista=0.5):
    cfg.estaciones.activa = True
    cfg.estaciones.periodo = 10
    cfg.estaciones.p_pista = p_pista
    return cfg


def test_estacion_alterna(cfg):
    sim = sim_vacia(_cfg(cfg))
    vals = []
    for t in (0, 9, 10, 19, 20):
        sim.t = t
        vals.append(sim.estacion())
    assert vals == [1.0, 1.0, -1.0, -1.0, 1.0]


def test_comida_fuera_de_estacion_es_toxica(cfg):
    sim = sim_vacia(_cfg(cfg))
    sim.entorno.K_base[:] = 10.0
    sim.entorno.R[:] = 10.0
    come = genoma_con(cfg, [(gen.COMER, 5.0, {})])
    ya, yb = np.argwhere(sim.tipo > 0)[0], np.argwhere(sim.tipo < 0)[0]
    colocar(sim, come, [ya[0]], [ya[1]], E=50)
    colocar(sim, come, [yb[0]], [yb[1]], E=50)
    sim.paso()  # estación +1: nutre el tipo A
    E = sim.pob["E"]
    assert E[0] > 50 and E[1] < 50


def test_sensores(cfg):
    sim = sim_vacia(_cfg(cfg, p_pista=0.3))
    for k in range(200):
        colocar(sim, genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})]), [k // 32 * 2], [k % 32], E=50)
    occ = sim.ocupacion()
    s = sim.sensar(occ, sim.validar_enlaces(occ))
    p = sim.pob
    assert np.array_equal(s[:, gen.S_TIPO_AQUI], sim.tipo[p["y"], p["x"]])
    pista = s[:, gen.S_PISTA]
    assert set(np.unique(pista)) <= {0.0, 1.0} and 0.15 < (pista != 0).mean() < 0.45


def test_desactivadas(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})]), [5], [5], E=50)
    occ = sim.ocupacion()
    assert not sim.sensar(occ, sim.validar_enlaces(occ))[0, gen.SENS_ESTACIONES].any()


def test_toxicidad_diferida(cfg):
    _cfg(cfg)
    cfg.estaciones.toxicidad = "diferido"
    cfg.estaciones.castigo = 0.5
    sim = sim_vacia(cfg)
    sim.entorno.K_base[:] = 10.0
    sim.entorno.R[:] = 10.0
    come = genoma_con(cfg, [(gen.COMER, 5.0, {})])
    yb = np.argwhere(sim.tipo < 0)[0]
    colocar(sim, come, [yb[0]], [yb[1]], E=50)
    sim.paso()  # come tóxica: gana energía al instante, pero queda veneno
    p = sim.pob
    assert p["E"][0] > 50 and np.isclose(p["veneno"][0], 1.5 * cfg.fisica.toma_max)
