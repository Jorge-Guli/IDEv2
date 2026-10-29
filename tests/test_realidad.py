"""Fase 12, etapa 2: el clima real regula el mundo."""
import json

import numpy as np
import pytest

from simbio import config, continuo
from simbio import genoma as gen
from simbio.config import RealidadCfg
from simbio.realidad import Clima
from simbio.simulacion import Simulacion


def _serie(ruta, dias=60):
    """Clima sintético: día y noche, temperatura que oscila, lluvias cada 10 días precedidas por una baja de
    presión."""
    h = np.arange(dias * 24)
    radiacion = np.maximum(0.0, np.sin(2 * np.pi * (h % 24 - 6) / 24)) * 800
    temperatura = 20 + 8 * np.sin(2 * np.pi * h / (24 * 30))
    precipitacion = np.where((h // 24) % 10 == 9, 2.0, 0.0)
    presion = 1013 - 6 * np.exp(-(((h + 12) % 240 - 228) / 12.0) ** 2)
    meta = {"lugar": "prueba", "horas": len(h)}
    np.savez(ruta, temperatura=temperatura, precipitacion=precipitacion, presion=presion, radiacion=radiacion,
             nubosidad=np.zeros(len(h)), hora=np.array([str(x) for x in h]), meta=json.dumps(meta))
    return ruta


def _cfg(archivo, *ajustes):
    cfg = config.cargar(None, ["mundo.alto=32", "mundo.ancho=32", "sim.poblacion_inicial=80",
                               "sim.registrar_cada=50", "estaciones.activa=true", "memoria.activa=true",
                               'estaciones.toxicidad="diferido"', "estaciones.castigo=0.2",
                               "estaciones.rampa_toxicidad=2000", "realidad.activa=true", f'realidad.archivo="{archivo.as_posix()}"',
                               "realidad.pasos_por_hora=2", *ajustes])
    cfg.sim.semilla = 5
    return cfg


def test_clima_precalculado(tmp_path):
    archivo = _serie(tmp_path / "c.npz")
    c = Clima(RealidadCfg(archivo=str(archivo), pasos_por_hora=3, acople_radiacion=1.0), np.random.default_rng(0))
    assert c.hora(0) == 0 and c.hora(3) == 1 and c.hora(3 * c.horas) == 0  # la serie se repite
    assert c.f_regeneracion.mean() == pytest.approx(1.0)  # misma comida en promedio, repartida en el día
    assert c.f_regeneracion[2] == 0.0  # de noche no crece
    assert np.all(np.abs(c.presion) <= 1.0)
    assert set(np.unique(c.estacion)) == {-1.0, 1.0}
    assert (c.estacion < 0).mean() == pytest.approx(0.3, abs=0.05)
    # la presión baja antes de que empiece cada lluvia
    inicio = np.flatnonzero(np.diff(c.estacion) < 0) + 1
    assert all(c.presion[max(i - 12, 0):i].min() < -0.3 for i in inicio)


def test_barajar_conserva_las_cantidades_y_rompe_el_orden(tmp_path):
    archivo = _serie(tmp_path / "c.npz")
    real = Clima(RealidadCfg(archivo=str(archivo)), np.random.default_rng(0))
    mezcla = Clima(RealidadCfg(archivo=str(archivo), barajar_dias=True), np.random.default_rng(0))
    for k in real.serie:
        assert np.allclose(np.sort(real.serie[k]), np.sort(mezcla.serie[k]))
    for k in ("temperatura", "precipitacion", "presion"):
        assert not np.allclose(real.serie[k], mezcla.serie[k])
    assert np.allclose(real.serie["radiacion"][:24], mezcla.serie["radiacion"][:24])  # el día queda entero


def test_sin_realidad_los_pesos_nuevos_no_mutan():
    g = gen.repetir(gen.luca(config.HerenciaCfg()), 300)
    gen.mutar(g, np.full(300, 0.2), config.HerenciaCfg(), np.random.default_rng(0))
    assert np.all(g["w"][:, :, gen.S_PRESION] == 0.0)
    gen.mutar(g, np.full(300, 0.2), config.HerenciaCfg(), np.random.default_rng(0), n_sens=gen.NUM_SENS_REALIDAD)
    assert np.any(g["w"][:, :, gen.S_PRESION] != 0.0)


def test_el_clima_llega_al_mundo(tmp_path):
    sim = Simulacion(_cfg(_serie(tmp_path / "c.npz")))
    assert sim.n_sens == gen.NUM_SENS_REALIDAD
    sim.correr(24 * 2 * 12)  # 12 días
    assert sim.pob.n > 0
    estaciones = {f["estacion"] for f in sim.historial if "estacion" in f}
    assert estaciones == {-1.0, 1.0}  # pasó una lluvia
    assert any(f["con_gen_presion"] > 0 for f in sim.historial if "con_gen_presion" in f)
    s = sim.sensar(sim.ocupacion(), sim.validar_enlaces(sim.ocupacion()))
    assert np.all(s[:, gen.S_PRESION] == sim.clima.presion[sim.clima.hora(sim.t)])


def test_determinismo_y_retomar(tmp_path):
    archivo = _serie(tmp_path / "c.npz")
    a, b = Simulacion(_cfg(archivo)), Simulacion(_cfg(archivo))
    a.correr(300)
    b.correr(300)
    assert np.array_equal(a.pob["E"], b.pob["E"])
    continuo.vivir(_cfg(archivo), tmp_path / "u", guardar_cada=100, pasos=150, verbose=False)
    r = continuo.vivir(_cfg(archivo), tmp_path / "u", guardar_cada=100, pasos=300, verbose=False)
    assert np.array_equal(r.pob["E"], a.pob["E"])


def test_barajado_cambia_el_mundo(tmp_path):
    archivo = _serie(tmp_path / "c.npz")
    a = Simulacion(_cfg(archivo))
    b = Simulacion(_cfg(archivo, "realidad.barajar_dias=true"))
    assert not np.array_equal(a.clima.estacion, b.clima.estacion)


def test_presion_desacoplada(tmp_path):
    archivo = _serie(tmp_path / "c.npz")
    real = Clima(RealidadCfg(archivo=str(archivo)), np.random.default_rng(0))
    otra = Clima(RealidadCfg(archivo=str(archivo), presion_desacoplada=True), np.random.default_rng(0))
    assert np.allclose(np.sort(real.presion), np.sort(otra.presion))
    assert np.array_equal(real.estacion, otra.estacion)
    assert not np.allclose(real.presion, otra.presion)


def test_lluvia_requiere_estaciones(tmp_path):
    with pytest.raises(ValueError):
        Simulacion(_cfg(_serie(tmp_path / "c.npz"), "estaciones.activa=false"))


def test_estado_viejo_se_completa():
    sim = Simulacion(config.cargar(None, ["mundo.alto=16", "mundo.ancho=16", "sim.poblacion_inicial=10"]))
    for k in ("w", "P", "ult_s"):
        sim.pob[k] = sim.pob[k][..., :gen.NUM_SENS_SIN_REALIDAD]
    sim.pob.compatibilizar()
    sim.correr(5)
    assert sim.pob["w"].shape[-1] == gen.NUM_SENS
