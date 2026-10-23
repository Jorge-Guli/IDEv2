import numpy as np
import pytest

from simbio.poblacion import Poblacion


def _pob(n):
    p = Poblacion(4)
    d = p.vacia(n)
    d["id"] = np.arange(n)
    d["E"] = np.arange(n, dtype=float)
    p.agregar(d)
    return p


def _nuevos(p, ids):
    d = p.vacia(len(ids))
    d["id"] = np.array(ids)
    d["E"] = np.array(ids, dtype=float)
    return d


@pytest.mark.parametrize("muertos,nacen", [([], []), ([1, 3], []), ([1, 3], [100]), ([1], [100, 101, 102]),
                                           ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [100]), ([9, 8], []), ([], [100])])
def test_actualizar_conserva_vivos_y_agrega_nuevos(muertos, nacen):
    p = _pob(10)
    mascara = ~np.isin(np.arange(10), muertos)
    p.actualizar(mascara, _nuevos(p, nacen) if nacen else None)
    esperado = set(range(10)) - set(muertos) | set(nacen)
    assert sorted(p["id"].tolist()) == sorted(esperado)
    assert np.all(p["E"] == p["id"])  # las filas siguen coherentes entre campos
    assert all(len(v) == p.n for v in p.d.values())
