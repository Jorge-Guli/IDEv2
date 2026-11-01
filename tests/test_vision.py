"""Fase 14: visión a distancia (alcance heredable, con costo)."""
import numpy as np

from simbio import config
from simbio import genoma as gen
from simbio.simulacion import Simulacion


def _sim(*ajustes):
    cfg = config.cargar(None, ["mundo.alto=16", "mundo.ancho=16", "sim.poblacion_inicial=2", "vision.activa=true",
                               *ajustes])
    return Simulacion(cfg)


def _poner(sim, i, y, x, d):
    p = sim.pob
    p["y"][i], p["x"][i], p["dir"][i] = y, x, d


def test_ve_otro_y_comida_lejos():
    sim = _sim()
    p = sim.pob
    d = 2  # una dirección cualquiera
    _poner(sim, 0, 5, 5, d)
    dy, dx = int(sim.DY[d]), int(sim.DX[d])
    _poner(sim, 1, (5 + 3 * dy) % 16, (5 + 3 * dx) % 16, (d + 4) % 8)  # a tres celdas: la segunda más allá
    p["socio"][:] = -1
    sim.entorno.R[:] = 0.0
    sim.entorno.R[(5 + 2 * dy) % 16, (5 + 2 * dx) % 16] = sim.cfg.mundo.capacidad_max
    occ = sim.ocupacion()
    socios = sim.validar_enlaces(occ)
    p["alcance"][:] = 0.0
    s = sim.sensar(occ, socios)
    assert s[0, gen.S_OTRO_LEJOS] == 0.0 and s[0, gen.S_COMIDA_LEJOS] == 0.0  # sin ojos no ve nada
    p["alcance"][:] = 2.0
    s = sim.sensar(occ, socios)
    assert abs(s[0, gen.S_COMIDA_LEJOS] - 1.0) < 1e-12
    assert abs(s[0, gen.S_OTRO_LEJOS] - (1.0 - 1 / 5)) < 1e-12
    assert abs(s[0, gen.S_TAMANO_LEJOS] - 0.5) < 1e-12  # los dos solos: mismo tamaño


def test_el_ojo_cuesta():
    a = _sim("herencia.mutacion=false")
    b = _sim("herencia.mutacion=false")
    b.pob["alcance"][:] = 4.0
    a.paso(), b.paso()
    # mismo azar y misma conducta (LUCA no lee los sensores nuevos): la diferencia es el costo del ojo
    assert np.allclose(np.asarray(a.pob["E"]) - np.asarray(b.pob["E"]), 4.0 * a.cfg.vision.costo_por_celda)


def test_el_alcance_muta_y_se_hereda():
    sim = _sim("sim.poblacion_inicial=80", "mundo.alto=24", "mundo.ancho=24", "herencia.mu_inicial=0.2")
    sim.correr(300)
    alc = np.asarray(sim.pob["alcance"])
    assert alc.max() > 0.0 and alc.max() <= sim.cfg.vision.alcance_max
    assert "alcance_medio" in sim.historial[-1]


def test_cegar_apaga_la_informacion():
    sim = _sim("vision.cegar=true")
    sim.pob["alcance"][:] = 5.0
    occ = sim.ocupacion()
    s = sim.sensar(occ, sim.validar_enlaces(occ))
    assert not np.asarray(s[:, gen.SENS_VISION]).any()
