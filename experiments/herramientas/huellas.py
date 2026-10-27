"""Huellas de determinismo: corre configuraciones cortas desde LUCA y muestra un hash de las métricas y de la
energía final de cada una.

Uso: antes y después de cambiar el motor, para comprobar que un cambio que debería ser neutro (una opción nueva
apagada por defecto) no altera las dinámicas existentes:
    python experiments/herramientas/huellas.py            # muestra las huellas
    python experiments/herramientas/huellas.py --guardar  # las guarda como referencia (huellas_referencia.json)
    python experiments/herramientas/huellas.py --comparar # compara con la referencia

Las huellas dependen de la versión de NumPy y de la plataforma: la referencia vale en el equipo donde se generó.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from simbio import config
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
REFERENCIA = Path(__file__).with_name("huellas_referencia.json")
BASE = ["sim.dispositivo=cpu", "mundo.alto=48", "mundo.ancho=48", "sim.poblacion_inicial=150",
        "sim.registrar_cada=100"]
CASOS = {
    "base": (RAIZ / "experiments/configs/base.toml", []),
    "coordinacion_fuerza": (RAIZ / "experiments/configs/coordinacion.toml",
                            ['asociacion.movimiento="fuerza"', "asociacion.exponente_arrastre=0.5"]),
    "estaciones_memoria": (RAIZ / "experiments/configs/base.toml",
                           ["estaciones.activa=true", 'estaciones.toxicidad="diferido"', "estaciones.castigo=0.2",
                            "estaciones.escala_parche=1.0", "memoria.activa=true", "memoria.tasa=1.0"]),
    "vivo": (RAIZ / "experiments/configs/vivo.toml", []),
    "vivo_softmax": (RAIZ / "experiments/configs/vivo.toml", ['fisica.decision="softmax"']),
}


def huellas(pasos: int = 600) -> dict[str, str]:
    out = {}
    for nombre, (ruta, ajustes) in CASOS.items():
        cfg = config.cargar(ruta, BASE + ajustes)
        cfg.sim.semilla = 3
        sim = Simulacion(cfg)
        h = sim.correr(pasos)
        out[nombre] = (hashlib.sha256(repr(h).encode()).hexdigest()[:16] + " "
                       + hashlib.sha256(np.asarray(sim.pob["E"]).tobytes()).hexdigest()[:16])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guardar", action="store_true")
    ap.add_argument("--comparar", action="store_true")
    args = ap.parse_args()
    h = huellas()
    for k, v in h.items():
        print(f"{k:22s} {v}")
    if args.guardar:
        REFERENCIA.write_text(json.dumps({"numpy": np.__version__, "huellas": h}, indent=2), encoding="utf-8")
        print(f"guardadas en {REFERENCIA}")
    if args.comparar:
        ref = json.loads(REFERENCIA.read_text(encoding="utf-8"))
        distintas = [k for k in h if ref["huellas"].get(k) != h[k]]
        print("iguales a la referencia" if not distintas else f"DISTINTAS: {distintas} (referencia con NumPy "
              f"{ref['numpy']}, ahora {np.__version__})")


if __name__ == "__main__":
    main()
