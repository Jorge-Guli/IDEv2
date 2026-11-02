"""El equipo como mundo físico de LUCA: la CPU libre regula el recrecimiento, y lo aplicado queda grabado."""

import json
import time

import numpy as np

from simbio import continuo
from simbio.config import Config
from simbio.simulacion import Simulacion


def _cfg(archivo):
    cfg = Config()
    cfg.mundo.alto = cfg.mundo.ancho = 16
    cfg.sim.poblacion_inicial = 20
    cfg.equipo.activa = True
    cfg.equipo.archivo = str(archivo)
    return cfg


def test_cpu_libre_regula_el_recrecimiento(tmp_path):
    sims = []
    for libre in (1.0, 0.2):
        sim = Simulacion(_cfg(tmp_path / "x.json"))
        sim.entorno.R[:] = 0.0
        sim.cpu_libre = libre
        sim.entorno.paso(0, sim.cfg.mundo.regeneracion * sim.cpu_libre)
        sims.append(float(sim.entorno.R.sum()))
    assert sims[1] < sims[0]
    assert np.isclose(sims[1] / sims[0], 0.2)


def test_leer_equipo_aplica_y_graba(tmp_path):
    archivo = tmp_path / "actual.json"
    archivo.write_text(json.dumps({"hora": time.time(), "cpu_libre": 0.35}), encoding="utf-8")
    sim = Simulacion(_cfg(archivo))
    fila = continuo.leer_equipo(sim, tmp_path)
    assert sim.cpu_libre == 0.35 and fila["cpu_libre"] == 0.35
    # muestra vencida: no se aplica, queda la anterior
    archivo.write_text(json.dumps({"hora": time.time() - 10_000, "cpu_libre": 0.9}), encoding="utf-8")
    fila = continuo.leer_equipo(sim, tmp_path)
    assert sim.cpu_libre == 0.35 and "sin_dato" in fila
    filas = (tmp_path / "equipo.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(filas) == 2


def test_misma_entrada_mismo_resultado(tmp_path):
    def correr():
        sim = Simulacion(_cfg(tmp_path / "x.json"))
        for t in range(300):
            sim.cpu_libre = 0.3 if (t // 50) % 2 else 0.9  # la misma serie grabada
            sim.paso()
        return sim.pob.n, float(sim.entorno.R.sum())
    assert correr() == correr()
