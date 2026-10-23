import numpy as np

from simbio.config import MundoCfg
from simbio.entorno import Entorno


def nuevo(**kw):
    cfg = MundoCfg(alto=32, ancho=32, **kw)
    return Entorno(cfg, np.random.default_rng(1))


def test_parches_reproducibles():
    assert np.array_equal(nuevo().K_base, nuevo().K_base)


def test_parches_correlacionados_y_acotados():
    e = nuevo()
    K = e.K_base
    assert K.min() >= 0 and K.max() <= e.cfg.capacidad_max + 1e-9
    # vecinos más parecidos que celdas al azar
    dif_vecinos = np.abs(K - np.roll(K, 1, 0)).mean()
    dif_azar = np.abs(K - np.random.default_rng(0).permutation(K.ravel()).reshape(K.shape)).mean()
    assert dif_vecinos < 0.5 * dif_azar


def test_regeneracion_acotada():
    e = nuevo()
    e.R[:] = 0
    previo = e.R.copy()
    for t in range(500):
        e.paso(t)
        assert (e.R >= previo - 1e-12).all()
        assert (e.R <= e.K_base + 1e-9).all()
        previo = e.R.copy()
    assert e.R.sum() > 0.9 * e.K_base.sum()


def test_estacionalidad():
    e = nuevo(amplitud_estacional=0.5, periodo_estacional=100)
    assert np.allclose(e.capacidad(25), e.K_base * 1.5)
    assert np.allclose(e.capacidad(75), e.K_base * 0.5)


def test_cambio_abrupto():
    e = nuevo(cambio_en_paso=10)
    antes = e.K_base.copy()
    for t in range(11):
        e.paso(t)
    assert not np.allclose(antes, e.K_base)
