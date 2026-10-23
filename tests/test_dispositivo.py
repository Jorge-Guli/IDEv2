"""Selección de dispositivo. Las pruebas de GPU se ejecutan solo si hay una GPU NVIDIA con CuPy."""

import hashlib

import numpy as np
import pytest

from simbio import dispositivo as dev
from simbio import genoma as gen
from simbio.config import Config
from simbio.simulacion import OPUESTA, Simulacion

HAY_GPU = dev._cupy_disponible() is not None
solo_gpu = pytest.mark.skipif(not HAY_GPU, reason="no hay GPU NVIDIA utilizable con CuPy")


def test_cpu_explicita():
    xp, nombre = dev.elegir("cpu")
    assert xp is np and nombre == "cpu"


def test_auto_siempre_funciona():
    xp, nombre = dev.elegir("auto")
    assert nombre in ("cpu", "gpu")


def test_preferencia_invalida():
    with pytest.raises(ValueError):
        dev.elegir("tpu")


def test_variable_de_entorno(monkeypatch):
    monkeypatch.setenv("SIMBIO_DISPOSITIVO", "cpu")
    assert dev.elegir("gpu")[1] == "cpu"


@pytest.mark.skipif(HAY_GPU, reason="hay GPU")
def test_gpu_pedida_sin_gpu_falla_claro():
    with pytest.raises(RuntimeError):
        dev.elegir("gpu")


def _cfg(dispositivo):
    c = Config()
    c.sim.dispositivo = dispositivo
    c.mundo.alto = c.mundo.ancho = 48
    c.sim.poblacion_inicial = 300
    c.sim.registrar_cada = 20
    return c


def _forzar(sim):
    p = sim.pob
    for k, prim in enumerate([gen.UNIRSE, gen.COMPARTIR, gen.DIVIDIRSE_UNIDO, gen.CONJUGAR, gen.SOLTARSE]):
        p["activo"][:, 4 + k] = True
        p["prim"][:, 4 + k] = prim
        p["w"][:, 4 + k, gen.S_RUIDO] = 2.0


def _huella(dispositivo):
    sim = Simulacion(_cfg(dispositivo))
    _forzar(sim)
    h = hashlib.sha256(repr(sim.correr(300)).encode())
    for k in sorted(sim.pob.d):
        h.update(np.ascontiguousarray(dev.a_cpu(sim.pob.d[k])).tobytes())
    return h.hexdigest()


@solo_gpu
def test_gpu_determinista():
    assert _huella("gpu") == _huella("gpu")


@solo_gpu
def test_gpu_invariantes_de_enlaces():
    sim = Simulacion(_cfg("gpu"))
    _forzar(sim)
    for _ in range(200):
        sim.paso()
        p = {k: dev.a_cpu(v) for k, v in sim.pob.d.items()}
        j = dev.a_cpu(sim.vecinos_enlazados(sim.ocupacion()))
        hay = p["socio"] >= 0
        f, k = np.nonzero(hay)
        assert len(np.unique(p["y"] * 1000 + p["x"])) == len(p["E"])
        assert np.all(j[hay] >= 0) and np.all(p["id"][j[hay]] == p["socio"][hay])
        assert np.all(p["socio"][j[f, k], OPUESTA[k]] == p["id"][f])


@solo_gpu
def test_gpu_y_cpu_arrancan_iguales():
    """Misma semilla y misma secuencia aleatoria: los primeros pasos coinciden en ambos dispositivos."""
    a = Simulacion(_cfg("cpu")).correr(60)
    b = Simulacion(_cfg("gpu")).correr(60)
    assert [h["poblacion"] for h in a[:3]] == [h["poblacion"] for h in b[:3]]
