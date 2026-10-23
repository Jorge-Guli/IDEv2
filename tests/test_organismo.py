import numpy as np

from simbio import genoma as gen
from simbio.simulacion import Simulacion

from .conftest import colocar, sim_vacia


def genoma_con(cfg, genes):
    """genes: lista de (primitiva, sesgo, {sensor: peso})."""
    g = gen.vacio(1, cfg.herencia.genes_max)
    for i, (prim, sesgo, pesos) in enumerate(genes):
        g["activo"][0, i] = True
        g["prim"][0, i] = prim
        g["b"][0, i] = sesgo
        for s, v in pesos.items():
            g["w"][0, i, s] = v
    g["mu"][0] = 0.01
    return g


def test_muerte_por_inanicion(cfg):
    cfg.mundo.capacidad_max = 0.0
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DESCANSAR, 1.0, {})]), [5], [5], E=3.0)
    sim.correr(20)
    assert sim.pob.n == 0


def test_genoma_grande_cuesta_mas(cfg):
    sim = sim_vacia(cfg)
    chico = genoma_con(cfg, [(gen.DESCANSAR, 1.0, {})])
    grande = genoma_con(cfg, [(gen.DESCANSAR, 1.0, {})] * 10)
    colocar(sim, chico, [1], [1], E=50)
    colocar(sim, grande, [10], [10], E=50)
    sim.entorno.R[:] = 0
    sim.paso()
    assert sim.pob["E"][1] < sim.pob["E"][0]


def test_sin_gen_de_division_no_hay_reproduccion(cfg):
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.COMER, 5.0, {})])
    colocar(sim, g, [5], [5], E=cfg.fisica.energia_max)
    sim.correr(100)
    assert sim.pob.n == 1


def test_descanso_por_defecto(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.AVANZAR, -5.0, {})]), [5], [5], E=50)
    sim.paso()
    assert sim.pob["ult_act"][0] == gen.DESCANSAR
    assert (sim.pob["y"][0], sim.pob["x"][0]) == (5, 5)


def test_comer_agota_la_celda(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.COMER, 5.0, {})]), [5], [5], E=50)
    sim.entorno.R[:] = 0
    sim.entorno.K_base[:] = 0
    sim.entorno.R[5, 5] = sim.entorno.K_base[5, 5] = 1.5
    sim.paso()
    esperado = 50 - cfg.fisica.costo_basal - cfg.fisica.costo_por_gen - cfg.fisica.costo_comer + 1.5
    assert np.isclose(sim.pob["E"][0], esperado)
    assert sim.entorno.R[5, 5] == 0


def test_borde_toroidal(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.AVANZAR, 5.0, {})]), [3], [cfg.mundo.ancho - 1], E=50, dir_=2)  # este
    sim.paso()
    assert (sim.pob["y"][0], sim.pob["x"][0]) == (3, 0)


def test_celda_ocupada_bloquea(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.AVANZAR, 5.0, {})]), [3], [3], E=50, dir_=2)
    colocar(sim, genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})]), [3], [4], E=50)
    sim.paso()
    assert (sim.pob["y"][0], sim.pob["x"][0]) == (3, 3)


def test_division_exitosa(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=60)
    sim.entorno.R[:] = 0
    sim.paso()
    p = sim.pob
    assert p.n == 2
    f = cfg.fisica
    esperado = (60 - f.costo_basal - f.costo_por_gen - f.costo_division) / 2
    assert np.allclose(p["E"], esperado)
    assert p["generacion"][1] == 1 and p["padre"][1] == p["id"][0]
    assert max(abs(int(p["y"][1]) - 5), abs(int(p["x"][1]) - 5)) == 1


def test_sin_espacio_no_hay_division(cfg):
    sim = sim_vacia(cfg)
    quieto = genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])
    vecinos = [(y, x) for y in (4, 5, 6) for x in (4, 5, 6) if (y, x) != (5, 5)]
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=60)
    for y, x in vecinos:
        colocar(sim, quieto, [y], [x], E=60)
    sim.entorno.R[:] = 0
    sim.paso()
    assert sim.pob.n == 9
    assert np.isclose(sim.pob["E"][0], 60 - cfg.fisica.costo_basal - cfg.fisica.costo_por_gen)


def test_percepcion_local(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})]), [10], [10], E=50)
    occ = sim.ocupacion()
    sim.rng = np.random.default_rng(0)
    s1 = sim.sensar(occ)
    sim.entorno.R[20, 20] += 5.0  # lejos
    sim.rng = np.random.default_rng(0)
    s2 = sim.sensar(occ)
    assert np.array_equal(s1, s2)


def test_luca_persiste_en_corrida_corta(cfg):
    cfg.mundo.alto = cfg.mundo.ancho = 64
    sim = Simulacion(cfg)
    sim.correr(1500)
    assert sim.pob.n > cfg.sim.poblacion_inicial
