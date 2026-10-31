"""Fase 13, desarrollo: red regulatoria (estado interno heredable que los genes leen) y señal por contacto."""
import numpy as np

from simbio import config
from simbio import genoma as gen
from simbio.simulacion import Simulacion

from .conftest import colocar, sim_vacia
from .test_organismo import genoma_con

# índices de las entradas de R
MORF = gen.NUM_REG  # primer morfógeno de los socios
SENS = gen.NUM_REG + gen.NUM_MORF  # primer sensor


def _sensar(sim):
    occ = sim.ocupacion()
    socios = sim.validar_enlaces(occ)
    return sim.sensar(occ, socios), socios


def _enlazar(sim, i, j, k):
    """Enlaza i con j, que está en la dirección k de i."""
    p = sim.pob
    p["socio"][i, k] = p["id"][j]
    p["socio"][j, (k + 4) % 8] = p["id"][i]


def test_el_regulador_sigue_a_su_entrada(cfg):
    cfg.desarrollo.activo = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])
    g["R"][0, 1, SENS + gen.S_ENERGIA] = 4.0  # el regulador 1 sube con la energía
    colocar(sim, g, [5], [5], E=100)
    for _ in range(60):
        s, socios = _sensar(sim)
        sim.decidir(s, socios)
    assert np.isclose(sim.pob["reg"][0, 1], np.tanh(4.0), atol=1e-3)
    assert np.allclose(sim.pob["reg"][0, [0, 2, 3]], 0.0)


def test_los_genes_leen_el_estado(cfg):
    cfg.desarrollo.activo = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.COMER, -1.0, {})])
    g["v"][0, 0, 3] = 5.0  # comer solo si el regulador 3 está alto
    colocar(sim, g, [5], [5], E=50)
    colocar(sim, g, [9], [9], E=50)
    sim.pob["reg"][:, 3] = [1.0, -1.0]  # mismo genoma, distinto estado
    act, _ = sim.decidir(*_sensar(sim))
    assert act[0] == gen.COMER and act[1] == gen.DESCANSAR


def test_inerte_los_genes_no_la_leen(cfg):
    cfg.desarrollo.activo = True
    cfg.desarrollo.inerte = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.COMER, -1.0, {})])
    g["v"][0, 0, 3] = 5.0
    g["R"][0, 3, gen.NUM_REG + gen.NUM_MORF + gen.S_CONST] = 4.0
    colocar(sim, g, [5], [5], E=50)
    sim.pob["reg"][0, 3] = 1.0
    act, _ = sim.decidir(*_sensar(sim))
    assert act[0] == gen.DESCANSAR
    assert sim.pob["reg"][0, 3] > 0.9  # la red sigue funcionando


def test_senal_por_contacto(cfg):
    cfg.desarrollo.activo = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])
    g["R"][0, 4, MORF + 0] = 3.0  # el regulador 4 lee el morfógeno 0 de los socios
    colocar(sim, gen.repetir(g, 3), [5, 5, 9], [5, 6, 9], E=50)
    _enlazar(sim, 0, 1, 2)  # 1 está al este de 0; 2 queda suelto
    sim.pob["reg"][:, 0] = 0.9
    s, socios = _sensar(sim)
    sim.decidir(s, socios)
    r4 = sim.pob["reg"][:, 4]
    esperado = cfg.desarrollo.tasa * np.tanh(3.0 * 0.9)
    assert np.allclose(r4[:2], esperado) and r4[2] == 0.0


def test_inhibicion_lateral_diferencia_a_dos_hermanas(cfg):
    # como Notch–Delta: el regulador 0 se activa a sí mismo y lo inhibe el de la vecina. Dos células pegadas con
    # el mismo genoma y una diferencia mínima terminan en estados opuestos: dos "tipos celulares"
    cfg.desarrollo.activo = True
    sim = sim_vacia(cfg)
    g = genoma_con(cfg, [(gen.DESCANSAR, 5.0, {})])
    g["R"][0, 0, 0] = 2.0
    g["R"][0, 0, MORF + 0] = -3.0
    colocar(sim, gen.repetir(g, 2), [5, 5], [5, 6], E=100)
    _enlazar(sim, 0, 1, 2)
    sim.pob["reg"][:, 0] = [0.01, -0.01]
    for _ in range(100):
        s, socios = _sensar(sim)
        sim.decidir(s, socios)
    r = sim.pob["reg"][:, 0]
    assert r[0] > 0.9 and r[1] < -0.9


def test_el_hijo_hereda_el_estado(cfg):
    cfg.desarrollo.activo = True
    cfg.mundo.capacidad_max = 0.0
    cfg.herencia.mutacion = False
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=90)
    sim.pob["reg"][0] = np.linspace(-0.8, 0.8, gen.NUM_REG)
    sim.paso()
    assert sim.pob.n == 2
    assert np.allclose(sim.pob["reg"][0], sim.pob["reg"][1])


def test_division_asimetrica(cfg):
    cfg.desarrollo.activo = True
    cfg.desarrollo.asimetria = 0.2
    cfg.mundo.capacidad_max = 0.0
    cfg.herencia.mutacion = False
    sim = sim_vacia(cfg)
    colocar(sim, genoma_con(cfg, [(gen.DIVIDIRSE, 5.0, {})]), [5], [5], E=90)
    sim.paso()
    assert sim.pob.n == 2
    assert not np.allclose(sim.pob["reg"][0], sim.pob["reg"][1])


def test_mutacion_de_la_red(cfg):
    g = gen.repetir(genoma_con(cfg, [(gen.COMER, 1.0, {})]), 50)
    sin = gen.mutar({k: v.copy() for k, v in g.items()}, np.full(50, 0.2), cfg.herencia,
                    np.random.default_rng(1), regulacion=False)
    con = gen.mutar({k: v.copy() for k, v in g.items()}, np.full(50, 0.2), cfg.herencia,
                    np.random.default_rng(1), regulacion=True)
    assert not sin["R"].any() and not sin["rb"].any() and not sin["v"].any()
    assert con["R"].any() and con["rb"].any() and con["v"].any()
    # la red se muta al final: lo demás es igual con y sin ella
    for k in ("w", "b", "prim", "mu", "etiqueta"):
        assert np.array_equal(sin[k], con[k])


def test_apagada_no_cambia_nada(cfg):
    cfg.sim.pasos = 200
    h1 = Simulacion(cfg).correr()
    cfg2 = type(cfg)()
    cfg2.mundo, cfg2.sim = cfg.mundo, cfg.sim
    cfg2.desarrollo.tasa = 0.9  # parámetros de la red sin efecto mientras está apagada
    cfg2.desarrollo.asimetria = 0.5
    h2 = Simulacion(cfg2).correr()
    assert repr(h1) == repr(h2)


def test_genomas_viejos_se_completan():
    g = gen.vacio(3, 24)
    for k in gen.CAMPOS_REG:
        del g[k]
    g = gen.compatibilizar(g)
    assert g["R"].shape == (3, gen.NUM_REG, gen.ENTRADAS_REG) and not g["R"].any()
    assert g["v"].shape == (3, 24, gen.NUM_REG)


def test_medidas_de_la_revision():
    cfg = config.cargar(None, ["mundo.alto=24", "mundo.ancho=24", "sim.poblacion_inicial=80", "ataque.activo=true",
                               "ataque.tamano=true", "desarrollo.activo=true", "sim.registrar_cada=50"])
    sim = Simulacion(cfg)
    sim.correr(150)
    f = sim.historial[-1]
    assert "frac_ataques_intragrupo" in f and 0.0 <= f["frac_ataques_intragrupo"] <= 1.0
    assert {"parentesco_relativo", "corr_reg_rol_intra"} <= set(f) or f.get("grupos_de_3_o_mas", 0) == 0


def test_linea_germinal():
    """Peldaño 3: si una sola célula del cuerpo hace todos los propágulos, el exceso sobre el azar es grande; si
    todas hacen los mismos, no hay exceso."""
    cfg = config.cargar(None, ["mundo.alto=16", "mundo.ancho=16", "sim.poblacion_inicial=6", "desarrollo.activo=true"])
    sim = Simulacion(cfg)
    lab, tam, edad = np.zeros(6, dtype=int), np.full(6, 6), np.full(6, 200.0)
    sim.pob["n_lugar"][:] = 100
    sim.pob["n_propagulos"][:] = sim.xp.asarray(np.array([12, 0, 0, 0, 0, 0], dtype=np.int32))
    f = sim._linea_germinal(lab, tam, edad)
    assert f["concentracion_propagulos"] == 1.0 and f["exceso_germinal"] > 0.3
    assert abs(f["frac_sin_propagulos"] - 5 / 6) < 1e-12
    sim.pob["n_propagulos"][:] = 2
    f = sim._linea_germinal(lab, tam, edad)
    assert abs(f["concentracion_propagulos"] - 1 / 3) < 1e-12 and f["exceso_germinal"] <= 0.0


def test_propagulos_se_cuentan():
    cfg = config.cargar(None, ["mundo.alto=24", "mundo.ancho=24", "sim.poblacion_inicial=80", "ataque.activo=true",
                               "ataque.tamano=true", "desarrollo.activo=true", "sim.registrar_cada=50"])
    sim = Simulacion(cfg)
    sim.correr(150)
    f = sim.historial[-1]
    assert {"exceso_germinal", "frac_sin_propagulos", "frac_propagulos_de_cuerpo"} <= set(f)
    assert int(sim.pob["n_propagulos"].sum()) > 0
    assert 0.0 <= f["frac_frente_hermana"] <= 1.0
    assert abs(f["supresion_cancer"] - (f["frac_frente_hermana"] - f["frac_ataques_intragrupo"])) < 1e-12
