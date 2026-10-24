import numpy as np

from simbio import genoma as gen
from simbio.persistencia import cargar_genomas

from .conftest import colocar, sim_vacia
from .test_asociacion import ESTE, OESTE
from .test_organismo import genoma_con


def quieto(cfg):
    return genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])


def _par(sim, cfg, dir_a, dir_b, genoma=None):
    g = genoma if genoma is not None else quieto(cfg)
    colocar(sim, g, [5], [5], E=50, dir_=dir_a)
    colocar(sim, g, [5], [6], E=50, dir_=dir_b)
    p = sim.pob
    p["socio"][0, ESTE], p["socio"][1, OESTE] = p["id"][1], p["id"][0]


def _sensar(sim):
    occ = sim.ocupacion()
    return sim.sensar(occ, sim.validar_enlaces(occ))


def test_rumbo_de_los_socios(cfg):
    cfg.coordinacion.rumbo = True
    sim = sim_vacia(cfg)
    _par(sim, cfg, 0, 1)  # el socio apunta un octavo de vuelta hacia la derecha (girar_der suma 1)
    s = _sensar(sim)
    assert np.isclose(s[0, gen.S_RUMBO_SOCIOS_SIN], np.sin(np.pi / 4))
    assert np.isclose(s[1, gen.S_RUMBO_SOCIOS_SIN], -np.sin(np.pi / 4))
    assert np.isclose(s[0, gen.S_RUMBO_SOCIOS_COS], np.cos(np.pi / 4))


def test_empuje_de_los_socios(cfg):
    cfg.coordinacion.rumbo = True
    sim = sim_vacia(cfg)
    _par(sim, cfg, 0, 0)
    sim.pob["ult_act"][1] = gen.AVANZAR
    s = _sensar(sim)
    assert s[0, gen.S_EMPUJE_SOCIOS] == 1.0 and s[1, gen.S_EMPUJE_SOCIOS] == 0.0
    assert np.isclose(s[0, gen.S_RUMBO_SOCIOS_COS], 1.0)


def test_sin_coordinacion_sensores_en_cero(cfg):
    sim = sim_vacia(cfg)
    _par(sim, cfg, 0, 3)
    sim.pob["ult_act"][1] = gen.AVANZAR
    sim.pob["senal"][:] = 1.0
    s = _sensar(sim)
    assert not s[:, np.r_[gen.SENS_RUMBO, gen.SENS_SENAL]].any()


def test_senal_no_ocupa_la_accion_y_cuesta(cfg):
    cfg.coordinacion.senales = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.SENALAR, 0.7, {}), (gen.COMER, 5.0, {})])
    _par(sim, cfg, 0, 0, g)
    s = _sensar(sim)
    act, _ = sim.decidir(s)
    assert (act == gen.COMER).all()
    assert np.allclose(sim.pob["senal"], np.tanh(0.7))
    # el socio percibe la señal en el paso siguiente
    s = _sensar(sim)
    assert np.allclose(s[:, gen.S_SENAL_SOCIOS], np.tanh(0.7))
    assert np.allclose(s[:, gen.S_SENAL_PROPIA], np.tanh(0.7))


def test_costo_de_la_senal(cfg):
    cfg.mundo.capacidad_max = 0.0
    cfg.asociacion.costo_enlace = 0.0
    E = {}
    for senales in (False, True):
        cfg.coordinacion.senales = senales
        sim = sim_vacia(cfg)
        _par(sim, cfg, 0, 0, genoma_con(cfg, [(gen.SENALAR, 0.7, {}), (gen.DESCANSAR, 5.0, {})]))
        sim.paso()
        E[senales] = float(sim.pob["E"][0])
    assert np.isclose(E[False] - E[True], cfg.coordinacion.costo_senal * np.tanh(0.7))


def test_senal_desactivada_no_emite(cfg):
    sim = sim_vacia(cfg)
    _par(sim, cfg, 0, 0, genoma_con(cfg, [(gen.SENALAR, 0.7, {}), (gen.DESCANSAR, 5.0, {})]))
    sim.decidir(_sensar(sim))
    assert not sim.pob["senal"].any()


def test_barajar_conserva_los_valores(cfg):
    cfg.coordinacion.rumbo = True
    cfg.coordinacion.barajar = True
    sim = sim_vacia(cfg)
    for y in range(0, 20, 2):
        n0 = sim.pob.n
        colocar(sim, quieto(cfg), [y], [5], E=50, dir_=0)
        colocar(sim, quieto(cfg), [y], [6], E=50, dir_=y % 8)
        p = sim.pob
        p["socio"][n0, ESTE], p["socio"][n0 + 1, OESTE] = p["id"][n0 + 1], p["id"][n0]
    s = _sensar(sim)
    cfg.coordinacion.barajar = False
    s0 = _sensar(sim)
    col = gen.S_RUMBO_SOCIOS_SIN
    assert np.allclose(np.sort(s[:, col]), np.sort(s0[:, col]))
    assert not np.allclose(s[:, col], s0[:, col])


def test_barajar_deja_en_cero_a_los_sueltos_y_la_memoria(cfg):
    cfg.coordinacion.rumbo = cfg.coordinacion.senales = cfg.coordinacion.barajar = True
    sim = sim_vacia(cfg)
    for y in range(0, 12, 2):
        n0 = sim.pob.n
        colocar(sim, quieto(cfg), [y], [5], E=50, dir_=0)
        colocar(sim, quieto(cfg), [y], [6], E=50, dir_=y % 8)
        p = sim.pob
        p["socio"][n0, ESTE], p["socio"][n0 + 1, OESTE] = p["id"][n0 + 1], p["id"][n0]
    colocar(sim, quieto(cfg), [20], [20], E=50)  # suelto
    sim.pob["senal"][:] = np.linspace(0.1, 0.9, sim.pob.n)
    s = _sensar(sim)
    assert not s[-1, np.r_[gen.SENS_RUMBO, gen.S_SENAL_SOCIOS]].any()
    assert np.allclose(s[:, gen.S_SENAL_PROPIA], sim.pob["senal"])


def test_genomas_viejos_se_completan(tmp_path):
    g = gen.vacio(3, 24)
    g["w"] = g["w"][..., :15]
    np.savez(tmp_path / "p.npz", **g)
    h = cargar_genomas(tmp_path / "p.npz")
    assert h["w"].shape == (3, 24, gen.NUM_SENS)
