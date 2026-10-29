"""Fase 12: mundo del texto (la estación la decide un texto, letra por letra)."""
import numpy as np
import pytest

from simbio import config
from simbio import genoma as gen
from simbio.simulacion import Simulacion
from simbio.texto import clases


def test_clases_de_letras():
    assert clases("Ñandú, ¡sí!").tolist() == [-1, 1, -1, -1, 1, -1, 1]  # ñ consonante, acentos fuera, signos fuera
    assert clases("12 ?!").size == 0


def _cfg(tmp_path, *ajustes):
    (tmp_path / "t.txt").write_text("casa de pan", encoding="utf-8")
    cfg = config.cargar(None, ["mundo.alto=16", "mundo.ancho=16", "sim.poblacion_inicial=20", "estaciones.activa=true",
                               "texto.activo=true", f"texto.archivos={tmp_path / 't.txt'}", "texto.pasos_por_letra=5",
                               "memoria.activa=true", *ajustes])
    cfg.sim.semilla = 4
    return cfg


def test_estacion_y_pista_siguen_al_texto(tmp_path):
    sim = Simulacion(_cfg(tmp_path))
    serie = clases("casa de pan").tolist()  # c a s a d e p a n
    for k in range(len(serie) + 1):
        sim.t = 5 * k + 2
        assert sim.estacion() == serie[k % len(serie)]
        s = sim.sensar(sim.ocupacion(), sim.validar_enlaces(sim.ocupacion()))
        assert np.all(s[:, gen.S_PISTA] == serie[(k - 1) % len(serie)])  # la pista es la letra anterior
    assert sim.texto.meta[0]["letras"] == 9 and len(sim.texto.meta[0]["sha256"]) == 64


def test_barajado_conserva_las_letras_y_es_determinista(tmp_path):
    a = Simulacion(_cfg(tmp_path, "texto.barajar=true")).texto.serie
    b = Simulacion(_cfg(tmp_path, "texto.barajar=true")).texto.serie
    assert np.array_equal(a, b) and sorted(a.tolist()) == sorted(clases("casa de pan").tolist())


def test_requiere_estaciones(tmp_path):
    with pytest.raises(ValueError):
        Simulacion(_cfg(tmp_path, "estaciones.activa=false"))


def test_corre(tmp_path):
    sim = Simulacion(_cfg(tmp_path, "sim.registrar_cada=10"))
    sim.correr(60)
    assert "acierto_comida" in sim.historial[-1] or sim.pob.n == 0
