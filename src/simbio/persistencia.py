"""Guardado y carga de configuraciones, métricas, poblaciones y linaje."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from . import genoma as gen
from .config import Config


def guardar_config(cfg: Config, ruta: Path) -> None:
    ruta.write_text(cfg.to_toml(), encoding="utf-8")


def guardar_historial(historial: list[dict[str, float]], ruta: Path) -> None:
    if not historial:
        return
    columnas = list(dict.fromkeys(k for fila in historial for k in fila))
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(historial)


def leer_historial(ruta: Path) -> list[dict[str, float]]:
    with open(ruta, encoding="utf-8") as f:
        return [{k: float(v) if v != "" else float("nan") for k, v in fila.items()} for fila in csv.DictReader(f)]


def guardar_poblacion(sim, ruta: Path) -> None:
    p = sim.pob
    extra = {k: p[k] for k in ("generacion", "cepa", "E", "id", "estres")}
    np.savez_compressed(ruta, **p.genomas(), **extra)


def cargar_genomas(ruta: Path) -> dict[str, np.ndarray]:
    with np.load(ruta) as datos:
        return {k: datos[k].copy() for k in gen.CAMPOS}


def guardar_linaje(sim, ruta: Path) -> None:
    filas = np.concatenate(sim.linaje, axis=0) if sim.linaje else np.zeros((0, 5), dtype=np.int64)
    np.savez_compressed(ruta, linaje=filas, columnas=np.array(["id", "padre", "nacimiento", "generacion", "cepa"]))
