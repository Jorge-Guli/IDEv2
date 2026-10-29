"""Mundo del texto (fase 12): un texto real decide la estación, letra por letra.

Cada letra dura `pasos_por_letra` pasos. Vocal: estación +1 (nutre el tipo A); consonante: −1 (el tipo B). Los
acentos se quitan, la ñ es consonante y lo que no es letra se salta. El sensor "pista" muestra la letra anterior, así
que comer bien exige predecir la vigente. El control baraja las letras con un generador propio.

La simulación solo lee el archivo. Los textos con derechos de autor viven en datos/textos/, que Git ignora: en los
registros queda su sha256 y su largo, nunca el contenido.
"""

from __future__ import annotations

import hashlib
import unicodedata

import numpy as np

from .config import TextoCfg
from .realidad import ubicar

VOCALES = set("aeiou")


def clases(texto: str) -> np.ndarray:
    """+1 por cada vocal y −1 por cada consonante, en orden; lo demás se salta."""
    plano = unicodedata.normalize("NFD", texto.lower().replace("ñ", "\0"))
    letras = [c for c in plano if ("a" <= c <= "z") or c == "\0"]
    return np.array([1 if c in VOCALES else -1 for c in letras], dtype=np.int8)


class Texto:
    def __init__(self, cfg: TextoCfg, rng: np.random.Generator):
        self.cfg = cfg
        partes, self.meta = [], []
        for nombre in (a.strip() for a in cfg.archivos.split(",") if a.strip()):
            datos = ubicar(nombre).read_bytes()
            c = clases(datos.decode("utf-8"))
            partes.append(c)
            self.meta.append({"archivo": nombre, "sha256": hashlib.sha256(datos).hexdigest(), "letras": int(c.size)})
        self.serie = np.concatenate(partes) if partes else np.zeros(0, dtype=np.int8)
        if self.serie.size < 2:
            raise ValueError("texto.archivos no tiene letras")
        if cfg.barajar:
            self.serie = self.serie[rng.permutation(self.serie.size)]

    def indice(self, t: int) -> int:
        return t // self.cfg.pasos_por_letra

    def vigente(self, t: int) -> float:
        return float(self.serie[self.indice(t) % self.serie.size])

    def anterior(self, t: int) -> float:
        return float(self.serie[(self.indice(t) - 1) % self.serie.size])
