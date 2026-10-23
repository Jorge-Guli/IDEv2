"""Mundo espacial: grilla toroidal con recursos en parches que se regeneran."""

from __future__ import annotations

import numpy as np

from .config import BienPublicoCfg, MundoCfg


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


def difundir(campo, fraccion: float, xp=np):
    """Reparte una fracción de cada celda en partes iguales entre sus 8 vecinas (toroidal; conserva el total)."""
    if fraccion <= 0.0:
        return campo
    sale = campo * fraccion
    llega = sum(xp.roll(xp.roll(sale, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                if (dy, dx) != (0, 0)) / 8.0
    return campo - sale + llega


class Entorno:
    def __init__(self, cfg: MundoCfg, rng: np.random.Generator, xp=np, bp: BienPublicoCfg | None = None):
        self.cfg = cfg
        self.bp = bp if bp is not None else BienPublicoCfg()
        self.alto, self.ancho = cfg.alto, cfg.ancho
        self.rng = rng
        self.xp = xp
        self.K_base = self._nuevo_mapa()
        self.R = self.K_base * cfg.recurso_inicial
        # bien público: recurso complejo C, enzima Z y alimento libre A (en cero si está desactivado)
        self.Kc = xp.zeros_like(self.K_base)
        if self.bp.activo:
            b = self.bp
            self.Kc = xp.asarray(b.capacidad_complejo_max * generar_parches(
                cfg.alto, cfg.ancho, b.escala_parche_complejo, b.contraste_complejo, self.rng))
        self.C = self.Kc.copy()
        self.Z = xp.zeros_like(self.K_base)
        self.A = xp.zeros_like(self.K_base)
        self.digerido = 0.0  # recurso complejo convertido en el último paso

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
        if self.bp.activo:
            self._bien_publico()

    def _bien_publico(self) -> None:
        b, xp = self.bp, self.xp
        self.C += b.regeneracion_complejo * (self.Kc - self.C)
        self.Z = difundir(self.Z, b.difusion_enzima, xp) * (1.0 - b.degradacion_enzima)
        d = self.C * (1.0 - xp.exp(-b.tasa_digestion * self.Z))
        self.C -= d
        self.A += b.rendimiento * d
        self.digerido = float(d.sum())
        self.A = difundir(self.A, b.difusion_libre, xp) * (1.0 - b.degradacion_libre)

    def comestible(self):
        """Alimento que se puede comer en cada celda: recurso simple más alimento libre."""
        return self.R + self.A if self.bp.activo else self.R
