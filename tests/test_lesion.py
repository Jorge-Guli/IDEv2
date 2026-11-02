"""Prueba de lesión de la fase 14: las dos copias deben ser independientes y una lesión nula no cuesta nada."""

import importlib.util
from pathlib import Path

from simbio import config
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[1]


def _ojos():
    spec = importlib.util.spec_from_file_location("ojos", RAIZ / "experiments/fase14/ojos.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _sim():
    cfg = config.cargar(RAIZ / "experiments/configs/natural.toml", ["vision.activa=true"])
    cfg.sim.semilla = 3
    sim = Simulacion(cfg)
    for _ in range(200):
        sim.paso()
    return sim


def test_lesion_nula_no_cuesta(monkeypatch):
    ojos = _ojos()
    monkeypatch.setattr(ojos, "PASOS_LESION", 200)
    sim = _sim()
    assert ojos.lesion(sim, lambda c: None) == 0.0
    # la lesión no toca la simulación original
    assert not sim.cfg.desarrollo.inerte
    ojos.lesion(sim, lambda c: setattr(c.desarrollo, "inerte", True))
    assert not sim.cfg.desarrollo.inerte


def test_lesion_cambia_la_historia(monkeypatch):
    ojos = _ojos()
    monkeypatch.setattr(ojos, "PASOS_LESION", 400)
    sim = _sim()
    assert ojos.lesion(sim, lambda c: setattr(c.desarrollo, "inerte", True)) != 0.0
