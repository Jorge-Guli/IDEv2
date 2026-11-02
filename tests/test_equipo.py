"""El equipo como mundo físico de LUCA: la CPU libre regula el recrecimiento, y lo aplicado queda grabado."""

import json
import time

import numpy as np

from simbio import continuo
from simbio.config import Config
from simbio.simulacion import Simulacion


def _cfg(carpeta):
    cfg = Config()
    cfg.mundo.alto = cfg.mundo.ancho = 16
    cfg.sim.poblacion_inicial = 20
    cfg.equipo.activa = True
    cfg.equipo.carpeta = str(carpeta)
    return cfg


def test_cpu_libre_regula_el_recrecimiento(tmp_path):
    sims = []
    for libre in (1.0, 0.2):
        sim = Simulacion(_cfg(tmp_path))
        sim.entorno.R[:] = 0.0
        sim.cpu_libre = libre
        sim.entorno.paso(0, sim.cfg.mundo.regeneracion * sim.cpu_libre)
        sims.append(float(sim.entorno.R.sum()))
    assert sims[1] < sims[0]
    assert np.isclose(sims[1] / sims[0], 0.2)


def test_leer_equipo_siente_cada_nivel(tmp_path):
    def escribir(nivel, libre, edad=0):
        (tmp_path / f"{nivel}.json").write_text(json.dumps({"hora": time.time() - edad, "cpu_libre": libre}),
                                                encoding="utf-8")
    escribir("docker", 0.5)
    escribir("pc", 0.8)
    sim = Simulacion(_cfg(tmp_path))
    fila = continuo.leer_equipo(sim, tmp_path)
    assert np.isclose(sim.cpu_libre, 0.4) and fila["docker"] == 0.5 and fila["pc"] == 0.8
    # muestra vencida en un nivel: ese nivel queda con su valor anterior
    escribir("pc", 0.1, edad=10_000)
    fila = continuo.leer_equipo(sim, tmp_path)
    assert np.isclose(sim.cpu_libre, 0.4) and "sin_dato_pc" in fila
    # un nivel que nunca dio dato no resta
    (tmp_path / "docker.json").unlink()
    sim2 = Simulacion(_cfg(tmp_path))
    escribir("pc", 0.6)
    continuo.leer_equipo(sim2, tmp_path)
    assert np.isclose(sim2.cpu_libre, 0.6)
    assert len((tmp_path / "equipo.jsonl").read_text(encoding="utf-8").splitlines()) == 3


def test_misma_entrada_mismo_resultado(tmp_path):
    def correr():
        sim = Simulacion(_cfg(tmp_path))
        for t in range(300):
            sim.cpu_libre = 0.3 if (t // 50) % 2 else 0.9  # la misma serie grabada
            sim.paso()
        return sim.pob.n, float(sim.entorno.R.sum())
    assert correr() == correr()
