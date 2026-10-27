"""Estímulos desde afuera (fase 12, etapa 3): luz y texto que alguien le da al universo mientras corre.

Un estímulo es un dato JSON:
    {"tipo": "luz", "y": 40, "x": 90, "radio": 6, "intensidad": 1.0, "repetir": 1, "cada": 0}
    {"tipo": "texto", "texto": "hola mundo"}

Se convierte en pulsos de luz programados a partir del paso en que llega. La luz es un campo del mundo: se percibe
con el sensor local "luz" y hace crecer comida donde cae (config.EstimulosCfg). En un texto, cada letra es siempre
el mismo pulso (mismo lugar y tamaño): un mensaje es una secuencia de lugares que se encienden, uno cada
`pasos_por_letra` pasos; los espacios son silencios.

En el modo continuo los datos llegan como archivos en <universo>/entradas/ (`python -m simbio estimular`), se
aplican en orden de nombre y quedan grabados en estimulos.jsonl con el paso: todo lo que entra se puede repetir.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np

from .config import EstimulosCfg


def pulsos(dato: dict, cfg: EstimulosCfg, alto: int, ancho: int) -> list[tuple[int, int, int, float, float]]:
    """Pulsos (paso relativo, y, x, radio, intensidad) de un estímulo."""
    tipo = dato.get("tipo")
    if tipo == "luz":
        y, x = int(dato["y"]) % alto, int(dato["x"]) % ancho
        radio, inten = float(dato.get("radio", 5)), float(dato.get("intensidad", 1.0))
        cada = int(dato.get("cada", 0))
        return [(k * cada, y, x, radio, inten) for k in range(max(int(dato.get("repetir", 1)), 1))]
    if tipo == "texto":
        out = []
        for j, letra in enumerate(str(dato["texto"])):
            if letra.isspace():
                continue
            c = ord(letra)
            out.append((j * cfg.pasos_por_letra, (c * 97) % alto, (c * 61) % ancho, 3.0 + c % 4, 1.0))
        return out
    raise ValueError(f"tipo de estímulo desconocido: {tipo!r}")


def mancha(alto: int, ancho: int, y: int, x: int, radio: float) -> np.ndarray:
    """Campo gaussiano centrado en (y, x) sobre la grilla toroidal, con máximo 1."""
    dy = np.minimum(np.abs(np.arange(alto) - y), alto - np.abs(np.arange(alto) - y))
    dx = np.minimum(np.abs(np.arange(ancho) - x), ancho - np.abs(np.arange(ancho) - x))
    return np.exp(-(dy[:, None] ** 2 + dx[None, :] ** 2) / (2.0 * max(radio, 0.5) ** 2))


# ------------------------------------------------------------------ canal por carpeta (modo continuo)
def enviar(universo: Path, dato: dict) -> Path:
    """Deja un estímulo en la carpeta de entradas del universo (escritura atómica: el universo nunca lee uno a
    medio escribir)."""
    pulsos(dato, EstimulosCfg(), 128, 128)  # valida antes de enviar
    carpeta = Path(universo) / "entradas"
    carpeta.mkdir(parents=True, exist_ok=True)
    nombre = f"{time.time_ns():020d}.json"
    tmp = carpeta / (nombre + ".tmp")
    tmp.write_text(json.dumps(dato, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, carpeta / nombre)
    return carpeta / nombre


def recibir(sim, universo: Path) -> list[dict]:
    """Aplica los estímulos que esperan en <universo>/entradas/ y los graba en estimulos.jsonl."""
    carpeta = Path(universo) / "entradas"
    if not carpeta.is_dir():
        return []
    registro = []
    for archivo in sorted(carpeta.glob("*.json")):
        try:
            dato = json.loads(archivo.read_text(encoding="utf-8"))
            n = sim.estimular(dato)
            destino, fila = "procesadas", {"t": sim.t, "archivo": archivo.name, "dato": dato, "pulsos": n}
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            destino, fila = "rechazadas", {"t": sim.t, "archivo": archivo.name, "error": str(e)}
        (carpeta / destino).mkdir(exist_ok=True)
        os.replace(archivo, carpeta / destino / archivo.name)
        fila["hora"] = time.time()
        registro.append(fila)
    if registro:
        with open(Path(universo) / "estimulos.jsonl", "a", encoding="utf-8") as f:
            for fila in registro:
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    return registro
