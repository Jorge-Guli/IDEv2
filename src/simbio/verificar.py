"""Verificación del dispositivo de cálculo: qué se detecta, cuánto rinde y si CPU y GPU coinciden.

    python -m simbio dispositivo            # informe completo
    python -m simbio dispositivo --rapido   # solo detección y una prueba corta
"""

from __future__ import annotations

import time

import numpy as np

from . import dispositivo as dev
from .config import Config
from .simulacion import Simulacion


def _corrida(nombre: str, lado: int, pasos: int, semilla: int = 1) -> tuple[list[dict], float, int]:
    cfg = Config()
    cfg.sim.dispositivo = nombre
    cfg.sim.semilla = semilla
    cfg.sim.registrar_cada = 50
    cfg.mundo.alto = cfg.mundo.ancho = lado
    cfg.sim.poblacion_inicial = max(200, lado * lado // 15)
    sim = Simulacion(cfg)
    sim.correr(min(200, pasos))  # calentamiento (compilación de kernels en GPU)
    t0 = time.time()
    sim.correr(pasos)
    return sim.historial, pasos / (time.time() - t0), sim.pob.n


def main(rapido: bool = False) -> None:
    xp, nombre = dev.elegir("auto")
    print(f"Dispositivo detectado (auto): {dev.descripcion(nombre)}")
    if nombre == "cpu":
        print("No hay GPU utilizable: la simulación corre en CPU con NumPy. Ver docs/dispositivos.md para usar GPU.")
    lados = [64] if rapido else [128, 256, 512]
    pasos = 100 if rapido else 300
    print(f"\n{'mundo':>8} {'organismos':>11} {'CPU pasos/s':>12} {'GPU pasos/s':>12}")
    for lado in lados:
        _, pps_cpu, n = _corrida("cpu", lado, pasos)
        pps_gpu = float("nan")
        if nombre == "gpu":
            _, pps_gpu, n = _corrida("gpu", lado, pasos)
        print(f"{lado:>5}²   {n:>11} {pps_cpu:>12.1f} {pps_gpu:>12.1f}")
    if nombre == "gpu":
        # misma semilla y misma secuencia aleatoria: el comienzo debe coincidir; luego el redondeo puede separarlas
        h_cpu, _, _ = _corrida("cpu", 64, 600)
        h_gpu, _, _ = _corrida("gpu", 64, 600)
        pc = np.array([h["poblacion"] for h in h_cpu])
        pg = np.array([h["poblacion"] for h in h_gpu])
        iguales = int(np.argmax(pc != pg)) if (pc != pg).any() else len(pc)
        print(f"\nCPU y GPU coinciden en los primeros {iguales * 50} pasos de 800 (después el redondeo puede "
              f"separar las trayectorias). Población media CPU={pc.mean():.0f}, GPU={pg.mean():.0f}.")
