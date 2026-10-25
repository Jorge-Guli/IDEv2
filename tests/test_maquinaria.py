"""Maquinaria por uso (fase 5): la eficiencia de comer y de avanzar depende del uso reciente."""
import numpy as np

from simbio import genoma as gen

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con


def _cfg(cfg, gamma=2.0):
    cfg.fisica.maquinaria_gamma = gamma
    return cfg


def test_especialista_come_mas(cfg):
    _cfg(cfg)
    sim = sim_vacia(cfg)
    sim.entorno.K_base[:] = 10.0
    sim.entorno.R[:] = 10.0
    come = genoma_con(cfg, [(gen.COMER, 5.0, {})])
    colocar(sim, come, [5], [5], E=20)
    colocar(sim, come, [5], [10], E=20)
    sim.pob["uso_comer"][:] = [0.7, 0.35]
    E0 = sim.pob["E"].copy()
    sim.paso()
    ganado = sim.pob["E"] - E0
    # el uso se actualiza antes de comer: el paso actual cuenta
    r, k0 = cfg.fisica.maquinaria_memoria, cfg.fisica.maquinaria_ref
    ef = [min(2.5, ((0.7 + r * 0.3) / k0) ** 2), ((k0 + r * (1 - k0)) / k0) ** 2]
    assert np.isclose(ganado[0] - ganado[1], cfg.fisica.toma_max * (ef[0] - ef[1]))


def test_sin_uso_no_avanza(cfg):
    _cfg(cfg)
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.AVANZAR, 5.0, {})]), [5], [5], E=50)
    sim.pob["uso_avanzar"][:] = 0.0
    sim.paso()
    assert (sim.pob["y"][0], sim.pob["x"][0]) == (5, 5)


def test_promedio_movil_del_uso(cfg):
    _cfg(cfg)
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.COMER, 5.0, {})]), [5], [5], E=50)
    r, k0 = cfg.fisica.maquinaria_memoria, cfg.fisica.maquinaria_ref
    sim.paso()
    assert np.isclose(sim.pob["uso_comer"][0], k0 + r * (1 - k0))
    assert np.isclose(sim.pob["uso_avanzar"][0], k0 * (1 - r))


def test_el_hijo_hereda_la_maquinaria(cfg):
    _cfg(cfg)
    cfg.mundo.capacidad_max = 0.0
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=90)
    sim.pob["uso_comer"][:] = 0.8
    sim.paso()
    assert sim.pob.n == 2 and np.allclose(sim.pob["uso_comer"], 0.8 * (1 - cfg.fisica.maquinaria_memoria))
