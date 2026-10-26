"""Regulación condicionada (fase 9): cada gen se expresa según una condición sobre la memoria interna."""
import numpy as np

from simbio import genoma as gen
from simbio.config import HerenciaCfg

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con


def _sensar(sim):
    occ = sim.ocupacion()
    return sim.sensar(occ, sim.validar_enlaces(occ))


def test_gen_condicionado_a_memoria_alta(cfg):
    cfg.memoria.activa = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.COMER, 5.0, {}), (gen.DESCANSAR, 1.0, {})])
    g["cond"][0, 0] = 1  # comer solo si la memoria A está alta
    colocar(sim, g, [5], [5], E=50)
    colocar(sim, g, [9], [9], E=50)
    sim.pob["memoria"][:, 0] = [0.9, 0.1]
    act, _ = sim.decidir(_sensar(sim))
    assert list(act) == [gen.COMER, gen.DESCANSAR]


def test_sin_memoria_la_condicion_no_actua(cfg):
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.COMER, 5.0, {}), (gen.DESCANSAR, 1.0, {})])
    g["cond"][0, 0] = 1
    colocar(sim, g, [5], [5], E=50)
    act, _ = sim.decidir(_sensar(sim))
    assert act[0] == gen.COMER


def test_la_condicion_muta_solo_con_memoria():
    cfg = HerenciaCfg(k_condicion=1.0)
    rng = np.random.default_rng(0)
    g = gen.repetir(gen.luca(cfg), 200)
    sin = gen.primitivas_permitidas(True, True)
    h = {k: v.copy() for k, v in g.items()}
    gen.mutar(h, np.full(200, 0.2), cfg, rng, sin)
    assert not h["cond"].any()
    con = gen.primitivas_permitidas(True, True, memoria=True)
    gen.mutar(h, np.full(200, 0.2), cfg, rng, con)
    assert h["cond"].any() and h["cond"].max() < gen.NUM_COND


def test_genomas_sin_condicion_se_completan(tmp_path):
    from simbio.persistencia import cargar_genomas
    g = gen.vacio(3, 24)
    del g["cond"]
    np.savez(tmp_path / "p.npz", **g)
    assert not cargar_genomas(tmp_path / "p.npz")["cond"].any()


def test_gen_modulado_por_la_memoria(cfg):
    """Fase 11: con la condición 5, la memoria A cambia el signo de la respuesta al tipo de comida (y solo a ese
    receptor: el resto de las entradas del gen no cambia)."""
    cfg.memoria.activa = True
    cfg.herencia.modulacion = True
    cfg.estaciones.activa = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.COMER, 0.0, {gen.S_TIPO_AQUI: 5.0}), (gen.DESCANSAR, 0.5, {}),
                         (gen.AVANZAR, -3.0, {gen.S_ENERGIA: 5.0})])
    g["cond"][0, [0, 2]] = gen.COND_MODULA_A
    ya = np.argwhere(sim.tipo > 0)
    colocar(sim, g, [ya[0][0]], [ya[0][1]], E=50)
    colocar(sim, g, [ya[1][0]], [ya[1][1]], E=50)
    sim.pob["memoria"][:, 0] = [1.0, 0.0]
    act, a = sim.decidir(_sensar(sim))
    assert a[0, 0] > 0 > a[1, 0]
    assert np.isclose(a[0, 2], a[1, 2])  # la energía no es un receptor modulable
    assert act[0] == gen.COMER and act[1] != gen.COMER


def test_la_modulacion_muta_solo_si_esta_permitida():
    cfg = HerenciaCfg(k_condicion=1.0)
    rng = np.random.default_rng(0)
    con = gen.primitivas_permitidas(True, True, memoria=True)
    h = gen.repetir(gen.luca(cfg), 200)
    gen.mutar(h, np.full(200, 0.2), cfg, rng, con)
    assert h["cond"].max() < gen.NUM_COND
    cfg.modulacion = True
    gen.mutar(h, np.full(200, 0.2), cfg, rng, con)
    assert h["cond"].max() >= gen.COND_MODULA_A
