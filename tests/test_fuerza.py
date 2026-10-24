"""Movimiento de grupos por fuerza: probabilidad = fuerza en la dirección elegida / tamaño^α."""
import numpy as np

from simbio import genoma as gen

from .conftest import colocar, sim_vacia
from .test_asociacion import ESTE, OESTE
from .test_organismo import genoma_con


def _trios(cfg, dir_empuje, exponente=1.0, empujan=1):
    cfg.mundo.alto = cfg.mundo.ancho = 64
    cfg.mundo.capacidad_max = 0.0
    cfg.asociacion.movimiento = "fuerza"
    cfg.asociacion.exponente_arrastre = exponente
    sim = sim_vacia(cfg)
    empuja = genoma_con(cfg, [(gen.AVANZAR, 5.0, {})])
    quieto = genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])
    for y in range(2, 62, 3):
        for x in range(0, 60, 4):
            n0 = sim.pob.n
            for k in range(3):
                colocar(sim, empuja if k < empujan else quieto, [y], [x + k], E=80, dir_=dir_empuje)
            p = sim.pob
            for k in range(2):
                p["socio"][n0 + k, ESTE], p["socio"][n0 + k + 1, OESTE] = p["id"][n0 + k + 1], p["id"][n0 + k]
    y0 = sim.pob["y"].copy()
    sim.paso()
    return float((sim.pob["y"] != y0).mean())


def test_un_empujador_mueve_un_trio_un_tercio_de_las_veces(cfg):
    assert abs(_trios(cfg, 0) - 1 / 3) < 0.06  # 300 tríos


def test_sin_ventaja_diagonal(cfg):
    assert abs(_trios(cfg, 1) - 1 / 3) < 0.06  # rumbo noreste: misma probabilidad que norte


def test_exponente_de_arrastre(cfg):
    assert abs(_trios(cfg, 0, exponente=0.5) - 1 / np.sqrt(3)) < 0.07


def test_todos_empujan_siempre_se_mueve(cfg):
    assert _trios(cfg, 0, empujan=3) == 1.0
