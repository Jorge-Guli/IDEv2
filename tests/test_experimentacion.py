import numpy as np

from simbio import config, corrida, genoma as gen, persistencia
from simbio.simulacion import Simulacion


def test_misma_semilla_mismas_metricas(cfg):
    a = Simulacion(cfg).correr(300)
    b = Simulacion(cfg).correr(300)
    assert a == b


def test_distinta_semilla_distintas_metricas(cfg):
    a = Simulacion(cfg).correr(300)
    cfg.sim.semilla = 99
    b = Simulacion(cfg).correr(300)
    assert a != b


def test_configuracion_toml_y_ajustes(tmp_path):
    ruta = tmp_path / "c.toml"
    ruta.write_text("[mundo]\nalto = 40\n[aprendizaje]\nactivo = false\n")
    cfg = config.cargar(ruta, ["fisica.costo_basal=0.5", "herencia.estres=false"])
    assert cfg.mundo.alto == 40 and not cfg.aprendizaje.activo
    assert cfg.fisica.costo_basal == 0.5 and not cfg.herencia.estres
    # ida y vuelta por TOML
    ruta2 = tmp_path / "d.toml"
    persistencia.guardar_config(cfg, ruta2)
    assert config.cargar(ruta2).to_dict() == cfg.to_dict()


def test_salida_de_una_corrida(cfg, tmp_path):
    cfg.sim.pasos = 100
    corrida.correr(cfg, tmp_path)
    for nombre in ("config.toml", "metricas.csv", "poblacion.npz", "linaje.npz", "metricas.png",
                   "mundo_final.png", "resumen.json"):
        assert (tmp_path / nombre).exists(), nombre
    historial = persistencia.leer_historial(tmp_path / "metricas.csv")
    assert historial[-1]["poblacion"] > 0
    genomas = persistencia.cargar_genomas(tmp_path / "poblacion.npz")
    assert set(genomas) == set(gen.CAMPOS)


def test_competencia_contra_si_misma_es_pareja(cfg):
    cfg.mundo.alto = cfg.mundo.ancho = 48
    cfg.sim.poblacion_inicial = 200
    cfg.sim.pasos = 300
    cfg.herencia.mutacion = False
    luca = gen.luca(cfg.herencia)
    fracciones = []
    for semilla in range(4):
        cfg.sim.semilla = semilla
        fracciones.append(corrida.competir(cfg, luca, luca))
    assert 0.35 < np.mean(fracciones) < 0.65


def test_estres_barajado_corre(cfg):
    cfg.herencia.estres_modo = "barajado"
    sim = Simulacion(cfg)
    sim.correr(300)
    assert sim.pob.n > 0
