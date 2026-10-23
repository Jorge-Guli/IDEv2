"""Selección del dispositivo de cálculo: GPU (CuPy) si está disponible, si no CPU (NumPy).

La simulación usa el módulo `xp` que corresponda: NumPy y CuPy comparten casi toda la interfaz. Los
números aleatorios se generan siempre en la CPU con el generador sembrado y se copian al dispositivo,
de modo que una corrida en GPU y otra en CPU consumen exactamente la misma secuencia aleatoria.
Las diferencias de redondeo entre dispositivos pueden separar las trayectorias con el tiempo: la
reproducibilidad exacta se garantiza para la misma semilla en el mismo tipo de dispositivo.

Preferencia: argumento `preferencia` ("auto", "cpu", "gpu"), o la variable de entorno SIMBIO_DISPOSITIVO.
"""

from __future__ import annotations

import os
from types import ModuleType

import numpy as np


def _cupy_disponible() -> ModuleType | None:
    try:
        import cupy as cp

        if cp.cuda.runtime.getDeviceCount() < 1:
            return None
        cp.zeros(1).sum().item()  # confirma que el dispositivo responde
        return cp
    except Exception:
        return None


def elegir(preferencia: str = "auto") -> tuple[ModuleType, str]:
    """Devuelve (xp, nombre). 'gpu' falla si no hay GPU utilizable; 'auto' cae a CPU sin error."""
    preferencia = os.environ.get("SIMBIO_DISPOSITIVO", preferencia).lower()
    if preferencia not in ("auto", "cpu", "gpu"):
        raise ValueError(f"dispositivo desconocido: {preferencia!r} (usar auto, cpu o gpu)")
    if preferencia == "cpu":
        return np, "cpu"
    cp = _cupy_disponible()
    if cp is not None:
        return cp, "gpu"
    if preferencia == "gpu":
        raise RuntimeError("se pidió GPU pero no hay una GPU NVIDIA utilizable con CuPy instalado "
                           "(ver docs/dispositivos.md)")
    return np, "cpu"


def descripcion(nombre: str) -> str:
    if nombre == "gpu":
        import cupy as cp

        props = cp.cuda.runtime.getDeviceProperties(cp.cuda.Device().id)
        return f"GPU {props['name'].decode()} (CuPy {cp.__version__})"
    return f"CPU (NumPy {np.__version__})"


def modulo(arr) -> ModuleType:
    """Módulo (numpy o cupy) al que pertenece un arreglo."""
    if type(arr).__module__.startswith("cupy"):
        import cupy as cp

        return cp
    return np


def a_cpu(arr):
    """Copia un arreglo a la memoria del CPU (no hace nada si ya está ahí)."""
    if type(arr).__module__.startswith("cupy"):
        return arr.get()
    return arr


def sumar_en(arr, idx, valores) -> None:
    """arr[idx] += valores acumulando índices repetidos (np.add.at)."""
    if modulo(arr) is np:
        np.add.at(arr, idx, valores)
    else:
        import cupyx

        cupyx.scatter_add(arr, idx, valores)


def minimo_en(arr, idx, valores) -> None:
    """arr[idx] = min(arr[idx], valores) con índices repetidos (np.minimum.at)."""
    if modulo(arr) is np:
        np.minimum.at(arr, idx, valores)
    else:
        import cupyx

        cupyx.scatter_min(arr, idx, valores)
