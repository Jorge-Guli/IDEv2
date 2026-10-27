"""Fase 12, etapa 4: ¿la física premia atacar? Duelo directo sin mutación, en el mundo de vivo.toml con ataque.

    cepa 1: LUCA + un gen atacar que se dispara cuando hay alguien enfrente (sesgo 0, peso +4 sobre "bloqueado")
    cepa 0: LUCA + el mismo gen en cero (mismo costo de genoma, sin efecto)

Se reporta la fracción final de la cepa 1 y si la población total sobrevive (un depredador que extingue a sus presas
se extingue con ellas). Ejecutar desde la raíz, con ajustes opcionales:
    python experiments/fase12/duelo_ataque.py
    python experiments/fase12/duelo_ataque.py ataque.eficiencia=0.3
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
ATAQUE = [(gen.ATACAR, 0.0, {gen.S_BLOQUEADO: 4.0}, 0)]
BASE = ["ataque.activo=true", "herencia.mutacion=false", "sim.registrar_cada=1000"]
PASOS = 30_000


def correr(tarea):
    semilla, extra = tarea
    cfg = config.cargar(RAIZ / "experiments/configs/vivo.toml", BASE + list(extra))
    cfg.sim.semilla = semilla
    n = cfg.sim.poblacion_inicial
    g = gen.repetir(gen.luca(cfg.herencia), n)
    g["etiqueta"] = np.random.default_rng(semilla).random((n, 2))
    cepas = np.zeros(n, dtype=np.int16)
    cepas[: n // 2] = 1
    a = {k: v[: n // 2] for k, v in g.items()}
    inv.agregar(a, True, ATAQUE)
    b = {k: v[n // 2:] for k, v in g.items()}
    inv.agregar(b, False, ATAQUE)
    for k in g:
        g[k][: n // 2], g[k][n // 2:] = a[k], b[k]
    sim = Simulacion(cfg, g, cepas)
    for _ in range(PASOS):
        sim.paso()
        if sim.pob.n == 0:
            return None, 0
    c = dev.a_cpu(sim.pob["cepa"])
    return float((c == 1).mean()), sim.pob.n


def main() -> None:
    extra = tuple(sys.argv[1:])
    with Pool(8) as p:
        rs = p.map(correr, [(s, extra) for s in range(1, 9)])
    fr = [r for r, _ in rs if r is not None]
    print("frac atacante", extra, " ".join("x" if r is None else f"{r:.2f}" for r, _ in rs),
          "| población", " ".join(str(n) for _, n in rs),
          f"| media {np.mean(fr) if fr else float('nan'):.3f}, gana en {sum(r > 0.5 for r in fr)}/{len(fr)}")


if __name__ == "__main__":
    main()
