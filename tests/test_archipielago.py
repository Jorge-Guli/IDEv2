"""Fase 12, etapa 5: archipiélago (islas con migración)."""
import numpy as np

from simbio import config
from simbio.archipielago import Archipielago
from simbio.simulacion import Simulacion


def _islas(n=3, semilla=1):
    islas = []
    for i in range(n):
        c = config.cargar(None, ["mundo.alto=24", "mundo.ancho=24", "sim.poblacion_inicial=40"])
        c.sim.semilla = semilla * 100 + i
        islas.append(Simulacion(c))
    return islas


def _huella(a):
    return [float(i.pob["E"].sum()) for i in a.islas] + [i.pob.n for i in a.islas]


def test_migran_y_se_conservan():
    a = Archipielago(_islas(), migrantes=5, cada=10, semilla=1)
    for isla in a.islas:
        isla.pob["generacion"][:] = 7
    a.islas[0].pob["mu"][:] = 0.123  # marca genética de la isla 0
    antes = [i.pob.n for i in a.islas]
    for isla in a.islas:  # que no cambie nada más en el paso de migración
        isla.paso = lambda: None
    for _ in range(10):
        a.paso()
    assert a.migrados == 15 and [i.pob.n for i in a.islas] == antes  # anillo: cada una da 5 y recibe 5
    mu1 = a.islas[1].pob["mu"]
    assert int(np.isclose(mu1, 0.123).sum()) == 5  # la isla 1 recibió de la 0
    assert int(np.isclose(a.islas[0].pob["mu"], 0.123).sum()) == antes[0] - 5
    assert (a.islas[1].pob["generacion"] == 7).all()
    for isla in a.islas:  # nadie comparte celda
        celdas = isla.pob["y"] * 24 + isla.pob["x"]
        assert len(np.unique(celdas)) == isla.pob.n


def test_sin_migrantes_son_islas_independientes():
    a = Archipielago(_islas(), migrantes=0, cada=10, semilla=1)
    for _ in range(40):
        a.paso()
    sola = _islas()[1]
    for _ in range(40):
        sola.paso()
    assert a.migrados == 0
    assert np.array_equal(a.islas[1].pob["E"], sola.pob["E"])


def test_determinista():
    corridas = []
    for _ in range(2):
        a = Archipielago(_islas(), migrantes=3, cada=10, semilla=2)
        for _ in range(60):
            a.paso()
        corridas.append(_huella(a))
    assert corridas[0] == corridas[1]
