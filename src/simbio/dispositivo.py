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
import warnings

# CuPy avisa que no encuentra CUDA_PATH aunque funcione con las cabeceras instaladas por pip ([ctk])
warnings.filterwarnings("ignore", message="CUDA path could not be detected")
from types import ModuleType

import numpy as np


_MOTIVO_SIN_GPU = ""


def _cupy_disponible() -> ModuleType | None:
    """CuPy si hay una GPU que además puede compilar y ejecutar kernels; si no, None (y guarda el motivo)."""
    global _MOTIVO_SIN_GPU
    try:
        import cupy as cp
    except Exception as e:  # CuPy no instalado o mal instalado
        _MOTIVO_SIN_GPU = f"CuPy no disponible ({type(e).__name__})"
        return None
    try:
        if cp.cuda.runtime.getDeviceCount() < 1:
            _MOTIVO_SIN_GPU = "no hay GPU NVIDIA"
            return None
        # operaciones que obligan a compilar kernels elementales y de reducción (fallan sin cabeceras de CUDA)
        x = cp.arange(16, dtype=cp.float64) * 0.5 + 1.0
        if abs(float(cp.tanh(x).sum()) - float(np.tanh(np.arange(16) * 0.5 + 1.0).sum())) > 1e-9:
            raise RuntimeError("resultado incorrecto en la prueba de GPU")
        return cp
    except Exception as e:
        _MOTIVO_SIN_GPU = f"la GPU no pudo ejecutar la prueba: {str(e).splitlines()[0][:200]}"
        return None


def elegir(preferencia: str = "auto", celdas: int | None = None,
           umbral_gpu: int = 90_000) -> tuple[ModuleType, str]:
    """Devuelve (xp, nombre). 'gpu' falla si no hay GPU utilizable; 'auto' cae a CPU sin error.

    En 'auto', la GPU se usa solo si el mundo tiene al menos `umbral_gpu` celdas: con pocos organismos,
    el costo fijo de cada operación en GPU la vuelve más lenta que la CPU.
    """
    preferencia = os.environ.get("SIMBIO_DISPOSITIVO", preferencia).lower()
    if preferencia not in ("auto", "cpu", "gpu"):
        raise ValueError(f"dispositivo desconocido: {preferencia!r} (usar auto, cpu o gpu)")
    if preferencia == "cpu" or (preferencia == "auto" and celdas is not None and celdas < umbral_gpu):
        return np, "cpu"
    cp = _cupy_disponible()
    if cp is not None:
        return cp, "gpu"
    if preferencia == "gpu":
        raise RuntimeError(f"se pidió GPU pero no está utilizable: {_MOTIVO_SIN_GPU} (ver docs/dispositivos.md)")
    if _MOTIVO_SIN_GPU.startswith("la GPU"):  # hay GPU pero falla: avisar, sin interrumpir
        warnings.warn(f"se usa CPU porque {_MOTIVO_SIN_GPU}. Ver docs/dispositivos.md", stacklevel=2)
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
    modulo(arr).add.at(arr, idx, valores)


def minimo_en(arr, idx, valores) -> None:
    """arr[idx] = min(arr[idx], valores) con índices repetidos (np.minimum.at)."""
    modulo(arr).minimum.at(arr, idx, valores)
