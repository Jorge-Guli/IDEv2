import numpy as np

from simbio import genoma as gen
from simbio.config import BienPublicoCfg, MundoCfg
from simbio.entorno import Entorno, difundir
from simbio.simulacion import Simulacion

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con


def _entorno(**kw):
    return Entorno(MundoCfg(alto=24, ancho=24), np.random.default_rng(0), bp=BienPublicoCfg(activo=True, **kw))


def test_difusion_conserva():
    campo = np.random.default_rng(1).random((10, 10))
    assert np.isclose(difundir(campo, 0.3).sum(), campo.sum())


def test_sin_enzima_no_hay_digestion():
    e = _entorno()
    e.paso(0)
    assert e.A.sum() == 0 and e.digerido == 0


def test_digestion_conserva_materia():
    e = _entorno(regeneracion_complejo=0.0, degradacion_libre=0.0, rendimiento=0.8)
    e.Z[5, 5] = 3.0
    C0, A0 = e.C.sum(), e.A.sum()
    e.paso(0)
    assert np.isclose(C0 - e.C.sum(), e.digerido)
    assert np.isclose(e.A.sum() - A0, 0.8 * e.digerido)


def test_enzima_se_degrada():
    e = _entorno()
    e.Z[:] = 1.0
    for t in range(200):
        e.paso(t)
    assert e.Z.sum() < 1e-6


def _cfg_bp(cfg, **kw):
    cfg.bien_publico.activo = True
    for k, v in kw.items():
        setattr(cfg.bien_publico, k, v)
    return cfg


def test_complejo_no_es_comestible(cfg):
    sim = sim_vacia(_cfg_bp(cfg))
    sim.entorno.R[:] = 0
    sim.entorno.K_base[:] = 0
    sim.entorno.C[5, 5] = 10.0
    colocar(sim, genoma_con(cfg, [(gen.COMER, 5.0, {})]), [5], [5], E=50)
    sim.paso()
    f = cfg.fisica
    assert np.isclose(sim.pob["E"][0], 50 - f.costo_basal - f.costo_por_gen - f.costo_comer)


def test_secretar_agrega_enzima_y_cuesta(cfg):
    sim = sim_vacia(_cfg_bp(cfg))
    colocar(sim, genoma_con(cfg, [(gen.SECRETAR, 5.0, {})]), [5], [5], E=50)
    sim.paso()
    assert sim.entorno.Z[5, 5] == cfg.bien_publico.enzima_por_secrecion
    f = cfg.fisica
    assert np.isclose(sim.pob["E"][0], 50 - f.costo_basal - f.costo_por_gen - cfg.bien_publico.costo_secretar)


def test_secrecion_inerte(cfg):
    sim = sim_vacia(_cfg_bp(cfg, secrecion_inerte=True))
    colocar(sim, genoma_con(cfg, [(gen.SECRETAR, 5.0, {})]), [5], [5], E=50)
    sim.paso()
    assert sim.entorno.Z.sum() == 0


def test_el_aprovechado_come_alimento_libre(cfg):
    sim = sim_vacia(_cfg_bp(cfg))
    sim.entorno.R[:] = 0
    sim.entorno.K_base[:] = 0
    colocar(sim, genoma_con(cfg, [(gen.COMER, 5.0, {})]), [5], [5], E=50)
    sim.entorno.A[5, 5] = 3.0
    sim.paso()
    assert sim.pob["E"][0] > 50
    assert sim.cont["comido_libre"] > 0 or sim.historial[-1]["comido_libre_por_org_paso"] > 0


def test_desactivado_no_permite_secretar(cfg):
    sim = Simulacion(cfg)
    assert gen.SECRETAR not in sim.permitidas
    assert sim.entorno.C.sum() == 0


def test_sensor_de_complejo(cfg):
    sim = sim_vacia(_cfg_bp(cfg))
    colocar(sim, genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})]), [5], [5], E=50)
    sim.entorno.C[5, 5] = cfg.bien_publico.capacidad_complejo_max / 2
    occ = sim.ocupacion()
    s = sim.sensar(occ, sim.validar_enlaces(occ))
    assert np.isclose(s[0, gen.S_COMPLEJO_AQUI], 0.5)


def test_secretar_no_se_refuerza(cfg):
    sim = sim_vacia(_cfg_bp(cfg))
    g = genoma_con(cfg, [(gen.SECRETAR, 0.5, {})])
    g["eta"][0] = 0.5
    colocar(sim, g, [5], [5], E=50)
    sim.paso()
    sim.aprender()
    assert sim.pob["p"][0, 0] == 0


def test_corrida_con_bien_publico(cfg):
    cfg.mundo.alto = cfg.mundo.ancho = 48
    sim = Simulacion(_cfg_bp(cfg))
    sim.correr(300)
    h = sim.historial[-1]
    assert sim.pob.n > 0 and "complejo_total" in h and "frac_enlazados_secretores" in h
