"""Fase 15: estar vivo cuesta según la actividad reciente; la cría hereda la actividad."""

import numpy as np

from simbio import genoma as gen
from simbio.config import Config
from simbio.simulacion import Simulacion


def _cfg(activo=True):
    cfg = Config()
    cfg.mundo.alto = cfg.mundo.ancho = 16
    cfg.sim.poblacion_inicial = 20
    cfg.metabolismo.activo = activo
    return cfg


def test_reposo_prolongado_baja_el_gasto():
    cfg = _cfg()
    m = cfg.metabolismo
    a = 1.0
    for _ in range(200):
        a += m.inercia * (0 - a)
    assert a < 1e-3
    assert cfg.fisica.costo_basal * (m.piso + (1 - m.piso) * a) < 0.101 * cfg.fisica.costo_basal


def test_quieto_gasta_menos_que_activo():
    gastos = []
    for actividad in (1.0, 0.0):
        sim = Simulacion(_cfg())
        sim.entorno.R[:] = 0.0
        sim.pob["actividad"][:] = actividad
        e0 = float(sim.pob["E"].sum())
        sim.paso()
        gastos.append(e0 - float(sim.pob["E"][: 20].sum()))
    assert gastos[1] < gastos[0]


def test_apagado_no_cambia_nada():
    def correr(cfg):
        sim = Simulacion(cfg)
        sim.correr(200)
        return sim.pob.n, float(sim.pob["E"].sum()), float(sim.entorno.R.sum())
    base = Config()
    base.mundo.alto = base.mundo.ancho = 16
    base.sim.poblacion_inicial = 20
    assert correr(base) == correr(_cfg(activo=False))


def test_la_cria_hereda_la_actividad():
    sim = Simulacion(_cfg())
    sim.pob["actividad"][:] = 0.05
    sim.pob["E"][:] = 90.0
    n0 = sim.pob.n
    for _ in range(30):
        sim.paso()
        if sim.pob.n > n0:
            break
    assert sim.pob.n > n0
    nuevos = np.asarray(sim.pob["actividad"])
    assert (nuevos < 0.2).sum() > n0 // 2


def test_poblacion_vieja_carga_con_actividad_plena():
    sim = Simulacion(_cfg())
    del sim.pob.d["actividad"]
    sim.pob.compatibilizar()
    assert np.all(np.asarray(sim.pob["actividad"]) == 1.0)
