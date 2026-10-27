"""Fase 12, etapa 2: ¿el clima real premia anticipar? Duelo directo en el mundo de clima.toml, sin mutación.

    cepa 1: LUCA + un gen de memoria A que lee la tendencia de la presión (peso +3). La presión que baja lleva la
            memoria a 0 (prepara la digestión de la comida del tiempo húmedo, tipo B); la que sube, a 1 (tipo A).
    cepa 0: LUCA + el mismo gen con pesos y sesgo en cero (mismo costo, sin efecto).

Si anticipar se premia, la cepa 1 gana con el clima real y no gana con la presión desacoplada (el sensor lee la
presión de otro momento de la serie). Cada semilla arranca en un año distinto de la serie (hora_inicial).
Ejecutar desde la raíz:
    python experiments/fase12/duelo_presion.py                                 # clima real
    python experiments/fase12/duelo_presion.py realidad.presion_desacoplada=true
"""

from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, "experiments/fase7")
import invadir_memoria as inv  # noqa: E402

from simbio import config  # noqa: E402
from simbio import dispositivo as dev  # noqa: E402
from simbio import genoma as gen  # noqa: E402
from simbio.simulacion import Simulacion  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
PRESION = [(gen.MEMORIA_A, 0.0, {gen.S_PRESION: 3.0}, 0)]
BASE = ["herencia.mutacion=false", "estaciones.rampa_toxicidad=5000", "sim.registrar_cada=2000"]
PASOS = 60_000
HORAS_ANIO = 24 * 365


def correr(tarea):
    semilla, extra = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/clima.toml",
                        BASE + [f"realidad.hora_inicial={(semilla - 1) * HORAS_ANIO}"] + list(extra))
    cfg.sim.semilla = semilla
    n = cfg.sim.poblacion_inicial
    g = gen.repetir(gen.luca(cfg.herencia), n)
    g["etiqueta"] = np.random.default_rng(semilla).random((n, 2))
    cepas = np.zeros(n, dtype=np.int16)
    cepas[: n // 2] = 1
    a = {k: v[: n // 2] for k, v in g.items()}
    inv.agregar(a, True, PRESION)
    b = {k: v[n // 2:] for k, v in g.items()}
    inv.agregar(b, False, PRESION)
    for k in g:
        g[k][: n // 2], g[k][n // 2:] = a[k], b[k]
    sim = Simulacion(cfg, g, cepas)
    for _ in range(PASOS):
        sim.paso()
        if sim.pob.n == 0:
            return None
    c = dev.a_cpu(sim.pob["cepa"])
    return float((c == 1).mean())


def main() -> None:
    extra = tuple(sys.argv[1:])
    with Pool(8) as p:
        rs = p.map(correr, [(s, extra) for s in range(1, 9)])
    validos = [r for r in rs if r is not None]
    print("frac presion", extra, " ".join("x" if r is None else f"{r:.2f}" for r in rs),
          f"| media {np.mean(validos):.3f}, gana en {sum(r > 0.5 for r in validos)}/{len(validos)}")


if __name__ == "__main__":
    main()
