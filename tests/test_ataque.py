"""Fase 12, etapa 4: la primitiva atacar (depredación evolucionada)."""
import numpy as np

from simbio import config
from simbio import genoma as gen
from simbio.simulacion import Simulacion


def _sim(n=3, *ajustes):
    cfg = config.cargar(None, ["mundo.alto=16", "mundo.ancho=16", f"sim.poblacion_inicial={n}",
                               "ataque.activo=true", *ajustes])
    sim = Simulacion(cfg)
    p = sim.pob
    p["y"][:] = 5
    p["x"][:] = np.arange(n) + 2  # en fila: 2, 3, 4...
    p["dir"][:] = 2  # mirando al este: cada uno tiene al siguiente enfrente
    p["E"][:] = 50.0
    p["socio"][:] = -1
    return sim


def _atacan(sim, quienes):
    act = np.full(sim.pob.n, gen.DESCANSAR, dtype=np.int8)
    act[quienes] = gen.ATACAR
    occ = sim.ocupacion()
    return sim._atacar(act, occ, sim.validar_enlaces(occ))


def test_quita_y_gana_con_perdida():
    sim = _sim(2)
    _atacan(sim, [0])
    assert sim.pob["E"][1] == 40.0
    assert sim.pob["E"][0] == 50.0 + 0.6 * 10.0
    assert sim.cont["ataques"] == 1 and sim.cont["robado"] == 10.0


def test_los_enlaces_protegen():
    sim = _sim(3)
    p = sim.pob
    p["socio"][1, 2] = p["id"][2]  # 1 y 2 enlazados (este / oeste)
    p["socio"][2, 6] = p["id"][1]
    _atacan(sim, [0])
    assert p["E"][1] == 45.0  # daño / (1 + 1 enlace)


def test_varios_atacantes_se_reparten_y_el_muerto_no_actua():
    sim = _sim(3)
    p = sim.pob
    p["y"][:], p["x"][:] = [5, 5, 4], [2, 3, 3]
    p["dir"][:] = [2, 0, 4]  # 0 y 2 miran a 1 (este y sur); 1 mira al norte (a 2)
    p["E"][1] = 8.0
    muertos = _atacan(sim, [0, 2])
    assert p["E"][1] <= 1e-9 and bool(muertos[1])
    assert p["E"][0] == p["E"][2] == 50.0 + 0.6 * 4.0


def test_sin_ataque_no_existe():
    cfg = config.cargar(None, ["mundo.alto=16", "mundo.ancho=16", "sim.poblacion_inicial=20"])
    sim = Simulacion(cfg)
    assert gen.ATACAR not in sim.permitidas and sim.n_prim == gen.NUM_PRIM_SIN_ATAQUE
    sim.correr(60)
    assert "tiene_atacar" not in sim.historial[-1] and "ataques" not in sim.historial[-1]
    g = gen.repetir(gen.luca(cfg.herencia), 2000)
    gen.mutar(g, np.full(2000, 0.2), cfg.herencia, np.random.default_rng(0))
    assert not (g["prim"] == gen.ATACAR).any()


def test_atacar_aparece_por_mutacion_y_se_mide():
    sim = _sim(3)
    assert gen.ATACAR in sim.permitidas
    g = gen.repetir(gen.luca(sim.cfg.herencia), 2000)
    gen.mutar(g, np.full(2000, 0.2), sim.cfg.herencia, np.random.default_rng(0), sim.permitidas)
    assert (g["prim"] == gen.ATACAR).any()
    cfg = config.cargar(None, ["mundo.alto=24", "mundo.ancho=24", "sim.poblacion_inicial=60", "ataque.activo=true",
                               'fisica.decision="softmax"', "sim.registrar_cada=20"])
    sim = Simulacion(cfg)
    sim.correr(100)
    assert {"ataques", "robado_por_org_paso", "tiene_atacar", "usa_atacar"} <= set(sim.historial[-1])
