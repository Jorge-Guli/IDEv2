import numpy as np

from simbio import genoma as gen
from simbio.config import HerenciaCfg


def test_luca_tiene_las_conductas_basicas():
    g = gen.luca(HerenciaCfg())
    prims = set(g["prim"][0][g["activo"][0]].tolist())
    assert {gen.COMER, gen.AVANZAR, gen.VOLTERETA, gen.DIVIDIRSE} <= prims


def test_mutacion_desactivada_copia_exacta():
    cfg = HerenciaCfg(mutacion=False)
    g = gen.repetir(gen.luca(cfg), 50)
    original = {k: v.copy() for k, v in g.items()}
    m = gen.tasa_efectiva(g["mu"], g["sens"], np.ones(50), cfg)
    gen.mutar(g, m, cfg, np.random.default_rng(0))
    assert all(np.array_equal(g[k], original[k]) for k in g)


def test_mutacion_produce_variacion_y_cambios_de_tamano():
    cfg = HerenciaCfg()
    g = gen.repetir(gen.luca(cfg), 2000)
    original_w = g["w"].copy()
    gen.mutar(g, np.full(2000, 0.2), cfg, np.random.default_rng(0))
    tamanos = g["activo"].sum(1)
    assert (g["w"] != original_w).any()
    assert tamanos.max() > 4 and tamanos.min() < 4  # duplicaciones/genes nuevos y eliminaciones


def test_duplicacion_copia_el_gen():
    cfg = HerenciaCfg(k_eliminacion=0, k_primitiva=0, k_gen_nuevo=0, k_duplicacion=1.0, sigma_peso=0.0)
    g = gen.luca(cfg)
    gen.mutar(g, np.array([1.0]), cfg, np.random.default_rng(0))
    activos = g["activo"][0]
    assert activos.sum() == 8  # cada uno de los 4 genes se duplicó
    for j in range(4):
        copias = [k for k in np.flatnonzero(activos)
                  if g["prim"][0, k] == g["prim"][0, j] and np.allclose(g["w"][0, k], g["w"][0, j])]
        assert len(copias) >= 2


def test_mas_estres_mas_mutacion():
    cfg = HerenciaCfg()
    mu, sens = np.array([0.01, 0.01]), np.array([3.0, 3.0])
    m = gen.tasa_efectiva(mu, sens, np.array([0.1, 0.9]), cfg)
    assert m[1] > m[0]
    assert np.isclose(m[1], 0.01 * (1 + 3 * 0.9))


def test_estres_desactivado():
    cfg = HerenciaCfg(estres=False)
    m = gen.tasa_efectiva(np.array([0.01]), np.array([5.0]), np.array([1.0]), cfg)
    assert np.isclose(m[0], 0.01)
    g = gen.repetir(gen.luca(cfg), 500)
    gen.mutar(g, np.full(500, 0.1), cfg, np.random.default_rng(0))
    assert np.all(g["sens"] == cfg.sensibilidad_inicial)


def test_rasgos_no_mutan_con_tasa_cero():
    cfg = HerenciaCfg()
    g = gen.repetir(gen.luca(cfg), 200)
    gen.mutar(g, np.zeros(200), cfg, np.random.default_rng(0))
    assert np.all(g["mu"] == cfg.mu_inicial) and np.all(g["eta"] == cfg.eta_inicial)


def test_tasa_efectiva_acotada():
    cfg = HerenciaCfg()
    m = gen.tasa_efectiva(np.array([0.1]), np.array([20.0]), np.array([1.0]), cfg)
    assert m[0] == cfg.tasa_max
