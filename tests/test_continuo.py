"""Fase 12: el modo continuo retoma exactamente donde estaba."""
import numpy as np

from simbio import config, continuo
from simbio.simulacion import Simulacion


def _cfg():
    cfg = config.cargar(None, ["mundo.alto=32", "mundo.ancho=32", "sim.poblacion_inicial=60",
                               "sim.registrar_cada=20", "estaciones.activa=true", "memoria.activa=true",
                               "herencia.modulacion=true", "estaciones.induccion=0.25",
                               'fisica.decision="softmax"'])
    cfg.sim.semilla = 7
    return cfg


def _huella(sim):
    p = sim.pob
    return (sim.t, p.n, float(np.asarray(p["E"]).sum()), float(np.asarray(p["w"]).sum()),
            float(np.asarray(sim.entorno.R).sum()))


def test_retomar_da_lo_mismo_que_no_cortar(tmp_path):
    seguida = Simulacion(_cfg())
    seguida.correr(240)
    continuo.vivir(_cfg(), tmp_path / "u", guardar_cada=50, pasos=120, verbose=False)
    retomada = continuo.vivir(_cfg(), tmp_path / "u", guardar_cada=50, pasos=240, verbose=False)
    assert _huella(retomada) == _huella(seguida)
    filas = continuo.leer_metricas(tmp_path / "u")
    assert [f["t"] for f in filas] == [f["t"] for f in seguida.historial]
    assert filas[-1]["poblacion"] == seguida.historial[-1]["poblacion"]


def test_eventos_y_archivos(tmp_path):
    continuo.vivir(_cfg(), tmp_path / "u", guardar_cada=50, pasos=100, verbose=False)
    eventos = [l for l in (tmp_path / "u" / "eventos.jsonl").read_text().splitlines()]
    assert '"inicio"' in eventos[0] and '"fin"' in eventos[-1]
    for nombre in ("estado.pkl", "config.toml", "poblacion.npz", "metricas.jsonl"):
        assert (tmp_path / "u" / nombre).exists()
