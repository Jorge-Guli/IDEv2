"""Restricción flagelar (fase 4): tras dividirse, progenitor e hijo no pueden avanzar durante T pasos."""
import numpy as np

from simbio import genoma as gen

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con


def _divisor(cfg):
    # se divide si tiene energía; si no, intenta avanzar
    return genoma_con(cfg, [(gen.DIVIDIRSE, -5.0, {gen.S_ENERGIA: 10.0}), (gen.AVANZAR, 0.5, {})])


def test_tras_dividirse_no_puede_avanzar(cfg):
    cfg.fisica.refractario_division = 5
    cfg.mundo.capacidad_max = 0.0
    sim = sim_vacia(cfg)
    colocar(sim, _divisor(cfg), [10], [10], E=90)
    sim.paso()
    p = sim.pob
    assert p.n == 2 and (p["refractario"] == 5).all() and p["n_divisiones"][0] == 1
    act, _ = sim.decidir(sim.sensar(sim.ocupacion(), sim.validar_enlaces(sim.ocupacion())))
    assert not (act == gen.AVANZAR).any()


def test_el_periodo_se_agota(cfg):
    cfg.fisica.refractario_division = 3
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.AVANZAR, 5.0, {})]), [10], [10], E=50)
    sim.pob["refractario"][:] = 3
    avanzo = []
    for _ in range(5):
        x0 = int(sim.pob["x"][0]) + int(sim.pob["y"][0]) * 1000
        sim.paso()
        avanzo.append(int(sim.pob["x"][0]) + int(sim.pob["y"][0]) * 1000 != x0)
    assert avanzo == [False, False, False, True, True]
    assert sim.pob["n_avances"][0] == 2


def test_sin_refractario_nada_cambia(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, _divisor(cfg), [10], [10], E=90)
    sim.paso()
    assert (sim.pob["refractario"] == 0).all()


def test_control_aleatorio_desligado_de_dividirse(cfg):
    cfg.fisica.refractario_division = 10
    cfg.fisica.refractario_modo = "aleatorio"
    cfg.sim.poblacion_inicial = 300
    from simbio.simulacion import Simulacion
    sim = Simulacion(cfg)
    desligado, alguno = False, False
    for _ in range(60):
        sim.paso()
        p = sim.pob
        alguno |= bool((p["refractario"] > 0).any())
        # los períodos no están ligados a la división: hay refractarios que nunca se dividieron
        desligado |= bool(((p["refractario"] > 0) & (p["n_divisiones"] == 0)).any())
    assert alguno and desligado
