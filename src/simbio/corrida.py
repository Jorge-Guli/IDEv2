"""Corridas completas con salida a disco, y competencia entre poblaciones."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import persistencia, visual
from .config import Config
from .simulacion import Simulacion


def correr(cfg: Config, salida: Path | None = None, genomas=None, cepas=None,
           imagenes: bool = True, verbose: bool = False) -> Simulacion:
    sim = Simulacion(cfg, genomas, cepas)
    if salida is not None:
        salida.mkdir(parents=True, exist_ok=True)
        persistencia.guardar_config(cfg, salida / "config.toml")
    cada = cfg.sim.imagen_cada
    inicio = time.time()
    for _ in range(cfg.sim.pasos):
        sim.paso()
        if salida is not None and imagenes and cada and sim.t % cada == 0:
            visual.imagen_mundo(sim, salida / f"mundo_{sim.t:07d}.png")
        if verbose and sim.t % (cfg.sim.registrar_cada * 20) == 0:
            print(f"t={sim.t} población={sim.pob.n}", flush=True)
        if sim.pob.n == 0:
            sim.historial.append(sim.medir())
            break
    duracion = time.time() - inicio
    if salida is not None:
        persistencia.guardar_historial(sim.historial, salida / "metricas.csv")
        persistencia.guardar_poblacion(sim, salida / "poblacion.npz")
        persistencia.guardar_linaje(sim, salida / "linaje.npz")
        resumen = {"pasos": sim.t, "poblacion_final": sim.pob.n, "dispositivo": sim.dispositivo,
                   "segundos": round(duracion, 2),
                   "pasos_por_segundo": round(sim.t / max(duracion, 1e-9), 2)}
        (salida / "resumen.json").write_text(json.dumps(resumen, indent=2), encoding="utf-8")
        if imagenes:
            visual.imagen_mundo(sim, salida / "mundo_final.png")
            visual.graficos(sim.historial, salida / "metricas.png")
    return sim


def competir(cfg: Config, genomas_a: dict, genomas_b: dict, salida: Path | None = None,
             imagenes: bool = False) -> float:
    """Siembra mitad de cada población (cepa 0 = A, cepa 1 = B) y devuelve la fracción final de B."""
    rng = np.random.default_rng(cfg.sim.semilla + 10_007)
    n = cfg.sim.poblacion_inicial
    mitad = n // 2
    ia = rng.integers(0, len(genomas_a["mu"]), mitad)
    ib = rng.integers(0, len(genomas_b["mu"]), n - mitad)
    genomas = {k: np.concatenate([genomas_a[k][ia], genomas_b[k][ib]]) for k in genomas_a}
    cepas = np.concatenate([np.zeros(mitad), np.ones(n - mitad)]).astype(np.int16)
    sim = correr(cfg, salida, genomas, cepas, imagenes=imagenes)
    if sim.pob.n == 0:
        return float("nan")
    return float((sim.pob["cepa"] == 1).mean())
