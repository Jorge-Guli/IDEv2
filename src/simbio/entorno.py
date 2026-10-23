"""Mundo espacial: grilla toroidal con recursos en parches que se regeneran."""

from __future__ import annotations

import numpy as np

from .config import MundoCfg


def generar_parches(alto: int, ancho: int, escala: float, contraste: float,
                    rng: np.random.Generator) -> np.ndarray:
    """Campo en [0, 1] espacialmente correlacionado (ruido blanco con filtro gaussiano por FFT)."""
    ruido = rng.standard_normal((alto, ancho))
    ky = np.fft.fftfreq(alto)[:, None]
    kx = np.fft.fftfreq(ancho)[None, :]
    filtro = np.exp(-2.0 * (np.pi * escala) ** 2 * (kx**2 + ky**2))
    campo = np.real(np.fft.ifft2(np.fft.fft2(ruido) * filtro))
    campo = (campo - campo.min()) / max(campo.max() - campo.min(), 1e-12)
    return campo**contraste


class Entorno:
    def __init__(self, cfg: MundoCfg, rng: np.random.Generator, xp=np):
        self.cfg = cfg
        self.alto, self.ancho = cfg.alto, cfg.ancho
        self.rng = rng
        self.xp = xp
        self.K_base = self._nuevo_mapa()
        self.R = self.K_base * cfg.recurso_inicial

    def _nuevo_mapa(self) -> np.ndarray:
        # el mapa se genera en CPU (mismo resultado en cualquier dispositivo) y se copia
        c = self.cfg
        return self.xp.asarray(c.capacidad_max * generar_parches(c.alto, c.ancho, c.escala_parche, c.contraste,
                                                                 self.rng))

    def capacidad(self, t: int) -> np.ndarray:
        c = self.cfg
        if c.amplitud_estacional == 0.0:
            return self.K_base
        factor = 1.0 + c.amplitud_estacional * np.sin(2.0 * np.pi * t / c.periodo_estacional)
        return self.K_base * max(factor, 0.0)

    def paso(self, t: int) -> None:
        if t == self.cfg.cambio_en_paso:
            self.K_base = self._nuevo_mapa()
        K = self.capacidad(t)
        self.R += self.cfg.regeneracion * (K - self.R)
        self.xp.minimum(self.R, K, out=self.R)
        self.xp.maximum(self.R, 0.0, out=self.R)
