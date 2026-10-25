"""Memoria interna (paso C): persistente, escrita por genes que no ocupan la acción, heredada al dividirse."""
import numpy as np

from simbio import genoma as gen

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con


def _sensar(sim):
    occ = sim.ocupacion()
    return sim.sensar(occ, sim.validar_enlaces(occ))


def test_el_gen_escribe_sin_ocupar_la_accion(cfg):
    cfg.memoria.activa = True
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.MEMORIA_A, 0.5, {}), (gen.COMER, 5.0, {})]), [5], [5], E=50)
    act, _ = sim.decidir(_sensar(sim))
    assert act[0] == gen.COMER
    assert np.isclose(sim.pob["memoria"][0, 0], cfg.memoria.tasa * np.tanh(0.5))
    assert sim.pob["memoria"][0, 1] == 0.0


def test_sin_genes_la_memoria_persiste_y_se_percibe(cfg):
    cfg.memoria.activa = True
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})]), [5], [5], E=50)
    sim.pob["memoria"][0] = [0.7, 0.2]
    for _ in range(20):
        sim.paso()
    assert np.allclose(sim.pob["memoria"][0], [0.7, 0.2])
    s = _sensar(sim)
    assert np.allclose(s[0, gen.SENS_MEMORIA], [0.7, 0.2])


def test_el_hijo_hereda_la_memoria(cfg):
    cfg.memoria.activa = True
    cfg.mundo.capacidad_max = 0.0
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=90)
    sim.pob["memoria"][0] = [0.9, 0.1]
    sim.paso()
    assert sim.pob.n == 2 and np.allclose(sim.pob["memoria"], [[0.9, 0.1], [0.9, 0.1]])


def test_interruptor_biestable(cfg):
    # un gen que se refuerza a sí mismo: por encima de 0,5 sube hasta 1, por debajo baja hasta 0
    cfg.memoria.activa = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.MEMORIA_A, -2.0, {gen.S_MEMORIA_A: 4.0}), (gen.DESCANSAR, 5.0, {})])
    colocar(sim, g, [5], [5], E=90)
    colocar(sim, g, [9], [9], E=90)
    sim.pob["memoria"][:, 0] = [0.55, 0.45]
    for _ in range(100):
        sim.decidir(_sensar(sim))
    assert np.allclose(sim.pob["memoria"][:, 0], [1.0, 0.0])


def test_desactivada(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.MEMORIA_A, 0.5, {}), (gen.DESCANSAR, 5.0, {})]), [5], [5], E=50)
    sim.decidir(_sensar(sim))
    assert sim.pob["memoria"][0, 0] == 0.0 and not _sensar(sim)[0, gen.SENS_MEMORIA].any()
