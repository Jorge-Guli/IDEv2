"""Fase 12, etapa 3: estímulos desde afuera (luz y texto) por la carpeta de entradas."""
import json

import numpy as np
import pytest

from simbio import config, continuo, estimulos
from simbio import genoma as gen
from simbio.simulacion import Simulacion


def _cfg(*ajustes):
    cfg = config.cargar(None, ["mundo.alto=32", "mundo.ancho=32", "sim.poblacion_inicial=60",
                               "sim.registrar_cada=20", "estimulos.activo=true", "estimulos.revisar_cada=10",
                               *ajustes])
    cfg.sim.semilla = 3
    return cfg


def test_texto_es_una_secuencia_de_pulsos():
    cfg = config.EstimulosCfg(pasos_por_letra=10)
    p = estimulos.pulsos({"tipo": "texto", "texto": "ab a"}, cfg, 32, 32)
    assert [x[0] for x in p] == [0, 10, 30]  # el espacio es un silencio
    assert p[0][1:] == p[2][1:]  # la misma letra enciende siempre el mismo lugar
    assert p[0][1:] != p[1][1:]
    with pytest.raises(ValueError):
        estimulos.pulsos({"tipo": "otro"}, cfg, 32, 32)


def test_la_luz_se_ve_alimenta_y_se_apaga():
    sim = Simulacion(_cfg())
    sim.correr(5)
    R0 = float(sim.entorno.R[16, 16])
    sim.entorno.R[16, 16] = 0.0
    sim.estimular({"tipo": "luz", "y": 16, "x": 16, "radio": 3})
    sim.paso()
    assert float(sim.luz[16, 16]) > 0.9 and float(sim.luz[0, 0]) < 0.01
    assert float(sim.entorno.R[16, 16]) > 0.0  # creció comida
    s = sim.sensar(sim.ocupacion(), sim.validar_enlaces(sim.ocupacion()))
    assert np.allclose(s[:, gen.S_LUZ], sim.luz[sim.pob["y"], sim.pob["x"]])
    sim.correr(300)
    assert float(sim.luz.max()) < 0.01
    assert R0 >= 0


def test_control_sin_acople_no_alimenta():
    con, sin = Simulacion(_cfg()), Simulacion(_cfg("estimulos.acople_luz=0.0"))
    for sim in (con, sin):
        sim.entorno.R[:] = 0.0
        sim.estimular({"tipo": "luz", "y": 16, "x": 16, "radio": 3})
        sim.entorno.paso(sim.t, 0.0)
        sim._luz()
    assert float(con.entorno.R.sum()) > 0.0 and float(sin.entorno.R.sum()) == 0.0
    assert np.allclose(con.luz, sin.luz)


def test_la_luz_anuncia_la_comida_con_retraso():
    sim = Simulacion(_cfg("estimulos.retraso_luz=30"))
    sim.estimular({"tipo": "luz", "y": 16, "x": 16, "radio": 3})
    sim.entorno.R[:] = 0.0
    sim.entorno.paso(sim.t, 0.0)
    sim._luz()
    assert float(sim.luz[16, 16]) > 0.9  # se ve ya
    assert float(sim.entorno.R.sum()) == 0.0  # pero todavía no alimenta
    for _ in range(30):
        sim.t += 1
        sim._luz()
    assert float(sim.abono[16, 16]) > 0.9 and float(sim.luz[16, 16]) < 0.6
    assert float(sim.entorno.R[16, 16]) > 0.0  # llegó la comida


def test_lugares_al_azar_iguales_en_ambas_condiciones():
    fijo = Simulacion(_cfg())
    a = Simulacion(_cfg("estimulos.lugares_al_azar=true"))
    b = Simulacion(_cfg("estimulos.lugares_al_azar=true", "estimulos.acople_luz=0.0"))
    for sim in (fijo, a, b):
        sim.estimular({"tipo": "texto", "texto": "aaaa"})
    assert len({p[1:3] for p in fijo.agenda}) == 1  # la letra cae siempre en el mismo lugar
    assert len({p[1:3] for p in a.agenda}) > 1  # al azar, no
    assert a.agenda == b.agenda  # el control ve la misma luz en los mismos lugares


def test_canal_por_carpeta_y_reproducible(tmp_path):
    u = tmp_path / "u"
    continuo.vivir(_cfg(), u, guardar_cada=50, pasos=50, verbose=False)
    estimulos.enviar(u, {"tipo": "texto", "texto": "hola"})
    (u / "entradas" / "malo.json").write_text("{no es json", encoding="utf-8")
    sim = continuo.vivir(_cfg(), u, guardar_cada=50, pasos=200, verbose=False)
    filas = [json.loads(x) for x in (u / "estimulos.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(filas) == 2 and any("error" in f for f in filas)
    aplicado = next(f for f in filas if "dato" in f)
    assert aplicado["pulsos"] == 4 and aplicado["t"] == 50
    assert not list((u / "entradas").glob("*.json"))
    # repetir: los mismos estímulos en los mismos pasos dan el mismo universo
    otra = Simulacion(_cfg())
    otra.correr(50)
    otra.estimular(aplicado["dato"])
    otra.correr(150)
    assert np.array_equal(otra.pob["E"], sim.pob["E"])


def test_sin_estimulos_se_rechaza():
    sim = Simulacion(config.cargar(None, ["mundo.alto=16", "mundo.ancho=16", "sim.poblacion_inicial=10"]))
    with pytest.raises(ValueError):
        sim.estimular({"tipo": "texto", "texto": "x"})
