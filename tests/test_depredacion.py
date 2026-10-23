import numpy as np

from simbio import genoma as gen
from simbio.simulacion import Simulacion, componentes

from .conftest import colocar, sim_vacia
from .test_asociacion import ESTE, OESTE
from .test_organismo import genoma_con


def _cfg(cfg, **kw):
    cfg.depredacion.activa = True
    cfg.depredacion.prob_ataque = 1.0  # todos atacados
    for k, v in kw.items():
        setattr(cfg.depredacion, k, v)
    return cfg


def quieto(cfg):
    return genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])


def _fila(sim, cfg, xs, y=5):
    for x in xs:
        colocar(sim, quieto(cfg), [y], [x], E=50)
    p = sim.pob
    for a in range(len(xs) - 1):
        p["socio"][a, ESTE], p["socio"][a + 1, OESTE] = p["id"][a + 1], p["id"][a]


def test_componentes():
    socios = np.full((4, 8), -1)
    socios[0, ESTE], socios[1, OESTE] = 1, 0
    socios[1, ESTE], socios[2, OESTE] = 2, 1
    lab = componentes(socios)
    assert lab[0] == lab[1] == lab[2] != lab[3]


def test_sin_depredacion_nadie_muere(cfg):
    sim = sim_vacia(cfg)
    colocar(sim, quieto(cfg), [5], [5], E=50)
    sim.paso()
    assert sim.pob.n == 1


def test_suelto_atacado_muere(cfg):
    sim = sim_vacia(_cfg(cfg))
    colocar(sim, quieto(cfg), [5], [5], E=50)
    sim.paso()
    assert sim.pob.n == 0


def test_grupo_refugio_sobrevive(cfg):
    sim = sim_vacia(_cfg(cfg, refugio=4))
    _fila(sim, cfg, [5, 6, 7, 8])  # grupo de 4
    colocar(sim, quieto(cfg), [20], [20], E=50)  # suelto
    sim.paso()
    assert sim.pob.n == 4


def test_grupo_chico_no_es_refugio(cfg):
    sim = sim_vacia(_cfg(cfg, refugio=4))
    _fila(sim, cfg, [5, 6, 7])  # grupo de 3
    sim.paso()
    assert sim.pob.n == 0


def test_modo_uniforme(cfg):
    sim = sim_vacia(_cfg(cfg, modo="uniforme", refugio=4))
    _fila(sim, cfg, [5, 6, 7, 8])
    sim.paso()
    assert sim.pob.n == 0


def test_corrida_con_depredacion(cfg):
    cfg.mundo.alto = cfg.mundo.ancho = 48
    cfg.depredacion.activa = True
    sim = Simulacion(cfg)
    sim.correr(300)
    h = sim.historial[-1]
    assert sim.pob.n > 0 and "frac_en_refugio" in h and h["depredados"] >= 0
