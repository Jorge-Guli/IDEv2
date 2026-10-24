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
    sim = sim_vacia(_cfg(cfg, refugio=4, gradual=False))
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


def test_refugio_gradual(cfg):
    sim = sim_vacia(_cfg(cfg, refugio=4))
    for y in range(0, 30, 2):  # 15 filas de 3 (en x 5, 6, 7) y sus enlaces
        base = sim.pob.n
        for x in (5, 6, 7):
            colocar(sim, quieto(cfg), [y], [x], E=50)
        p = sim.pob
        for a in (0, 1):
            p["socio"][base + a, ESTE], p["socio"][base + a + 1, OESTE] = p["id"][base + a + 1], p["id"][base + a]
    sim.paso()
    muertos = 45 - sim.pob.n
    assert 5 <= muertos <= 25  # esperado: 15 (un tercio)


def test_modo_aleatorio_perdona(cfg):
    sim = sim_vacia(_cfg(cfg, modo="aleatorio", prob_perdon=1.0))
    colocar(sim, quieto(cfg), [5], [5], E=50)
    sim.paso()
    assert sim.pob.n == 1


def test_aclimatacion(cfg):
    sim = sim_vacia(_cfg(cfg, inicio=3))
    colocar(sim, quieto(cfg), [5], [5], E=50)
    sim.correr(3)
    assert sim.pob.n == 1
    sim.paso()
    assert sim.pob.n == 0


def test_socio_que_muere_de_hambre_no_protege(cfg):
    sim = sim_vacia(_cfg(cfg, refugio=2))
    _fila(sim, cfg, [5, 6])
    sim.pob["E"][1] = 0.1  # muere por costos en este paso
    sim.paso()
    assert sim.pob.n == 0


def test_mismos_sorteos_en_todos_los_modos(cfg):
    """El generador del depredador no altera el de la simulación: sin enlaces, tamano == uniforme."""
    cfg.mundo.alto = cfg.mundo.ancho = 40
    cfg.depredacion.activa = True
    cfg.depredacion.prob_ataque = 0.01
    cfg.asociacion.activa = False
    a = repr(Simulacion(cfg).correr(200))
    cfg.depredacion.modo = "uniforme"
    b = repr(Simulacion(cfg).correr(200))
    assert a == b


def test_sin_division_unida(cfg):
    cfg.asociacion.division_unida = False
    sim = Simulacion(cfg)
    assert gen.DIVIDIRSE_UNIDO not in sim.permitidas and gen.UNIRSE in sim.permitidas


def test_rampa(cfg):
    """Con rampa, al principio la intensidad es casi nula."""
    sim = sim_vacia(_cfg(cfg, rampa=1000))
    for x in range(0, 30, 2):
        colocar(sim, quieto(cfg), [5], [x], E=50)
    sim.paso()
    assert sim.pob.n >= 14


def test_escalada_del_refugio(cfg):
    sim = sim_vacia(_cfg(cfg, refugio=2, refugio_final=4.0, escalada_inicio=10, escalada_pasos=20))
    for t, esperado in ((0, 2.0), (10, 2.0), (20, 3.0), (30, 4.0), (100, 4.0)):
        sim.t = t
        assert np.isclose(sim.refugio_actual(), esperado)


def test_sin_escalada_refugio_fijo(cfg):
    sim = sim_vacia(_cfg(cfg, refugio=3))
    sim.t = 10_000
    assert sim.refugio_actual() == 3.0


def test_par_vulnerable_tras_la_escalada(cfg):
    # con refugio 2 un par está a salvo; tras escalar a 3, un ataque lo mata con prob. 1/2
    sim = sim_vacia(_cfg(cfg, refugio=2, refugio_final=3.0, escalada_inicio=0, escalada_pasos=1))
    for y in range(0, 20, 2):
        _fila_en(sim, cfg, y)
    sim.t = 5
    sim.paso()
    assert 0 < sim.pob.n < 20


def _fila_en(sim, cfg, y):
    n0 = sim.pob.n
    colocar(sim, quieto(cfg), [y], [5], E=50)
    colocar(sim, quieto(cfg), [y], [6], E=50)
    p = sim.pob
    p["socio"][n0, ESTE], p["socio"][n0 + 1, OESTE] = p["id"][n0 + 1], p["id"][n0]
