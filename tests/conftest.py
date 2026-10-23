import numpy as np
import pytest

from simbio.config import Config
from simbio.simulacion import Simulacion


@pytest.fixture(autouse=True)
def _cpu_salvo_pruebas_de_dispositivo(request, monkeypatch):
    """Los tests construyen casos con arreglos de CPU: corren en CPU salvo los de test_dispositivo."""
    if request.module.__name__.split(".")[-1] != "test_dispositivo":
        monkeypatch.setenv("SIMBIO_DISPOSITIVO", "cpu")


@pytest.fixture
def cfg() -> Config:
    c = Config()
    c.mundo.alto = c.mundo.ancho = 32
    c.sim.poblacion_inicial = 40
    c.sim.registrar_cada = 10
    return c


def sim_vacia(cfg: Config) -> Simulacion:
    """Simulación sin organismos para colocar casos a mano."""
    cfg.sim.poblacion_inicial = 0
    return Simulacion(cfg)


def colocar(sim: Simulacion, genomas: dict, y, x, E, dir_=0) -> None:
    n = len(genomas["mu"])
    nuevos = sim._nuevos(genomas, np.asarray(y), np.asarray(x), np.full(n, float(E)),
                         padre=np.full(n, -1), generacion=np.zeros(n, dtype=np.int32),
                         cepa=np.zeros(n, dtype=np.int16), estres=np.zeros(n))
    nuevos["dir"][:] = dir_
    sim.pob.agregar(nuevos)
