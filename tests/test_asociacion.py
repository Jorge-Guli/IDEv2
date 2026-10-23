import numpy as np

from simbio import genoma as gen
from simbio.config import HerenciaCfg
from simbio.simulacion import OPUESTA, Simulacion

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con

ESTE, OESTE = 2, 6


def quieto(cfg):
    return genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])


def con(cfg, prim):
    return genoma_con(cfg, [(prim, 5.0, {})])


def enlazados(sim, a, b):
    p = sim.pob
    return p["id"][b] in p["socio"][a] and p["id"][a] in p["socio"][b]


def mundo_sin_recursos(sim):
    sim.entorno.R[:] = 0
    sim.entorno.K_base[:] = 0


def test_unirse_con_el_de_enfrente(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, con(cfg, gen.UNIRSE), [5], [5], E=50, dir_=ESTE)
    colocar(sim, quieto(cfg), [5], [6], E=50)
    sim.paso()
    assert enlazados(sim, 0, 1)
    assert sim.pob["socio"][0, ESTE] == sim.pob["id"][1]
    assert sim.pob["socio"][1, OESTE] == sim.pob["id"][0]


def test_unirse_sin_nadie_enfrente(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, con(cfg, gen.UNIRSE), [5], [5], E=50, dir_=ESTE)
    sim.paso()
    assert np.all(sim.pob["socio"] < 0)


def _par_enlazado(sim, cfg, genoma_a, genoma_b, dir_a=ESTE, dir_b=ESTE):
    colocar(sim, genoma_a, [5], [5], E=50, dir_=dir_a)
    colocar(sim, genoma_b, [5], [6], E=50, dir_=dir_b)
    p = sim.pob
    p["socio"][0, ESTE] = p["id"][1]
    p["socio"][1, OESTE] = p["id"][0]


def test_uno_se_aleja_rompe_el_enlace(cfg):
    cfg.asociacion.adhesion = False
    sim = sim_vacia(cfg)
    _par_enlazado(sim, cfg, quieto(cfg), con(cfg, gen.AVANZAR))
    sim.paso()
    assert sim.pob["x"][1] == 7
    assert np.all(sim.pob["socio"] < 0)


def test_movimiento_conjunto_conserva_el_enlace(cfg):
    sim = sim_vacia(cfg)
    # el de atrás avanza hacia la celda que deja libre el de adelante: no puede (estaba ocupada al inicio)
    # así que se mueven en paralelo: uno arriba del otro, ambos hacia el este
    colocar(sim, con(cfg, gen.AVANZAR), [5], [5], E=50, dir_=ESTE)
    colocar(sim, con(cfg, gen.AVANZAR), [6], [5], E=50, dir_=ESTE)
    p = sim.pob
    p["socio"][0, 4] = p["id"][1]  # sur
    p["socio"][1, 0] = p["id"][0]  # norte
    sim.paso()
    assert (p["x"][0], p["x"][1]) == (6, 6)
    assert enlazados(sim, 0, 1)


def test_muerte_del_enlazado(cfg):
    sim = sim_vacia(cfg)
    mundo_sin_recursos(sim)
    _par_enlazado(sim, cfg, quieto(cfg), quieto(cfg))
    sim.pob["E"][1] = 0.1
    sim.paso()
    sim.paso()
    assert sim.pob.n == 1
    assert np.all(sim.pob["socio"] < 0)


def test_soltarse(cfg):
    sim = sim_vacia(cfg)
    _par_enlazado(sim, cfg, con(cfg, gen.SOLTARSE), quieto(cfg))
    sim.paso()
    assert np.all(sim.pob["socio"] < 0)


def test_mas_enlaces_mas_costo(cfg):
    sim = sim_vacia(cfg)
    mundo_sin_recursos(sim)
    _par_enlazado(sim, cfg, quieto(cfg), quieto(cfg))
    colocar(sim, quieto(cfg), [20], [20], E=50)
    sim.paso()
    assert sim.pob["E"][0] < sim.pob["E"][2]
    assert np.isclose(sim.pob["E"][2] - sim.pob["E"][0], cfg.asociacion.costo_enlace)


def test_reparto_con_perdidas(cfg):
    sim = sim_vacia(cfg)
    mundo_sin_recursos(sim)
    colocar(sim, con(cfg, gen.COMPARTIR), [5], [5], E=50)
    colocar(sim, quieto(cfg), [5], [6], E=20)
    colocar(sim, quieto(cfg), [5], [4], E=20)
    p = sim.pob
    p["socio"][0, ESTE], p["socio"][1, OESTE] = p["id"][1], p["id"][0]
    p["socio"][0, OESTE], p["socio"][2, ESTE] = p["id"][2], p["id"][0]
    a, f = cfg.asociacion, cfg.fisica
    costos_donante = f.costo_basal + f.costo_por_gen + a.costo_compartir + 2 * a.costo_enlace
    costos_receptor = f.costo_basal + f.costo_por_gen + a.costo_enlace
    E_donante = 50 - costos_donante
    cedido = a.fraccion_compartir * E_donante
    sim.paso()
    assert np.isclose(p["E"][0], E_donante - cedido)
    assert np.allclose(p["E"][1:], 20 - costos_receptor + cedido * a.eficiencia_compartir / 2)


def test_compartir_sin_enlaces(cfg):
    sim = sim_vacia(cfg)
    mundo_sin_recursos(sim)
    colocar(sim, con(cfg, gen.COMPARTIR), [5], [5], E=50)
    sim.paso()
    f = cfg.fisica
    assert np.isclose(sim.pob["E"][0], 50 - f.costo_basal - f.costo_por_gen - cfg.asociacion.costo_compartir)


def test_compartir_sin_beneficio(cfg):
    cfg.asociacion.eficiencia_compartir = 0.0
    sim = sim_vacia(cfg)
    mundo_sin_recursos(sim)
    _par_enlazado(sim, cfg, con(cfg, gen.COMPARTIR), quieto(cfg))
    sim.paso()
    f, a = cfg.fisica, cfg.asociacion
    assert np.isclose(sim.pob["E"][1], 50 - f.costo_basal - f.costo_por_gen - a.costo_enlace)


def test_division_unida(cfg):
    sim = sim_vacia(cfg)
    mundo_sin_recursos(sim)
    colocar(sim, con(cfg, gen.DIVIDIRSE_UNIDO), [5], [5], E=60)
    sim.paso()
    assert sim.pob.n == 2
    assert enlazados(sim, 0, 1)
    sim.validar_enlaces(sim.ocupacion())
    assert enlazados(sim, 0, 1)  # el enlace es geométricamente válido


def test_conjugacion(cfg):
    sim = sim_vacia(cfg)
    donante = genoma_con(cfg, [(gen.CONJUGAR, 5.0, {gen.S_ENERGIA: 0.7})])
    _par_enlazado(sim, cfg, donante, quieto(cfg))
    sim.paso()
    p = sim.pob
    assert p["activo"][1].sum() == 2
    nuevo = np.flatnonzero(p["activo"][1])[1]
    assert p["prim"][1, nuevo] == gen.CONJUGAR
    assert np.allclose(p["w"][1, nuevo], p["w"][0, 0])


def test_herencia_de_la_etiqueta():
    cfg = HerenciaCfg(mutacion=False)
    g = gen.luca(cfg)
    g["etiqueta"][0] = [0.3, 0.7]
    hijos = gen.repetir(g, 5)
    gen.mutar(hijos, np.full(5, 0.1), cfg, np.random.default_rng(0))
    assert np.allclose(hijos["etiqueta"], [0.3, 0.7])


def test_etiquetas_iniciales_al_azar(cfg):
    sim = Simulacion(cfg)
    assert len(np.unique(sim.pob["etiqueta"][:, 0])) == cfg.sim.poblacion_inicial


def test_mutacion_respeta_primitivas_permitidas():
    cfg = HerenciaCfg()
    g = gen.repetir(gen.luca(cfg), 3000)
    gen.mutar(g, np.full(3000, 0.2), cfg, np.random.default_rng(0), gen.primitivas_permitidas(False, False))
    assert g["prim"][g["activo"]].max() <= gen.DIVIDIRSE


def test_asociacion_desactivada(cfg):
    cfg.asociacion.activa = False
    cfg.mundo.alto = cfg.mundo.ancho = 48
    sim = Simulacion(cfg)
    # aunque un genoma traiga genes de asociación, no pueden ejecutarse
    sim.pob["prim"][:, 4] = gen.UNIRSE
    sim.pob["activo"][:, 4] = True
    sim.pob["b"][:, 4] = 10.0
    for _ in range(300):
        sim.paso()
        assert np.all(sim.pob["socio"] < 0)


def test_grupo_en_cadena(cfg):
    sim = sim_vacia(cfg)
    for x in (5, 6, 7):
        colocar(sim, quieto(cfg), [5], [x], E=50)
    colocar(sim, quieto(cfg), [20], [20], E=50)
    p = sim.pob
    p["socio"][0, ESTE], p["socio"][1, OESTE] = p["id"][1], p["id"][0]
    p["socio"][1, ESTE], p["socio"][2, OESTE] = p["id"][2], p["id"][1]
    lab, _, _ = sim.grupos()
    assert lab[0] == lab[1] == lab[2] != lab[3]
    m = sim.medir()
    assert m["tamano_grupo_max"] == 3
    assert np.isclose(m["frac_enlazados"], 0.75)


def test_invariantes_con_asociacion_forzada(cfg):
    """Una población que se une, comparte, conjuga y se divide unida mantiene los enlaces consistentes."""
    cfg.mundo.alto = cfg.mundo.ancho = 40
    cfg.sim.poblacion_inicial = 300
    sim = Simulacion(cfg)
    p = sim.pob
    for k, prim in enumerate([gen.UNIRSE, gen.COMPARTIR, gen.DIVIDIRSE_UNIDO, gen.CONJUGAR, gen.SOLTARSE]):
        p["activo"][:, 4 + k] = True
        p["prim"][:, 4 + k] = prim
        p["w"][:, 4 + k, gen.S_RUIDO] = 2.0
    hubo_enlaces = False
    for _ in range(400):
        sim.paso()
        p = sim.pob
        occ = sim.ocupacion()
        assert len(np.unique(p["y"] * 1000 + p["x"])) == p.n
        j = sim.vecinos_enlazados(occ)
        hay = p["socio"] >= 0
        hubo_enlaces |= bool(hay.any())
        # vecindad e identidad
        assert np.all(j[hay] >= 0)
        assert np.all(p["id"][j[hay]] == p["socio"][hay])
        # simetría
        f, k = np.nonzero(hay)
        assert np.all(p["socio"][j[f, k], OPUESTA[k]] == p["id"][f])
        assert np.all((p["E"] > 0) & (p["E"] <= cfg.fisica.energia_max + 1e-9))
    assert hubo_enlaces


def test_adhesion_impide_alejarse(cfg):
    sim = sim_vacia(cfg)
    _par_enlazado(sim, cfg, quieto(cfg), con(cfg, gen.AVANZAR))
    sim.paso()
    assert sim.pob["x"][1] == 6  # no pudo alejarse
    assert enlazados(sim, 0, 1)


def test_adhesion_permite_moverse_juntos(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, con(cfg, gen.AVANZAR), [5], [5], E=50, dir_=ESTE)
    colocar(sim, con(cfg, gen.AVANZAR), [6], [5], E=50, dir_=ESTE)
    p = sim.pob
    p["socio"][0, 4], p["socio"][1, 0] = p["id"][1], p["id"][0]
    sim.paso()
    assert (p["x"][0], p["x"][1]) == (6, 6)
    assert enlazados(sim, 0, 1)
