"""Fase 12, etapa 5: archipiélago. Varias islas (simulaciones) que intercambian unos pocos organismos cada tanto.

Es el modelo de islas de la biología evolutiva: cada isla evoluciona por su cuenta y la migración trae a cada una lo
que otra inventó. Los migrantes salen de su isla y llegan a la siguiente (anillo), a celdas libres sorteadas, con su
genoma, su energía y su generación. Llegan sin enlaces ni memoria interna, como un recién nacido. Todo el azar de la
migración pasa por un generador propio, de CPU, así que el archipiélago es determinista.
"""

from __future__ import annotations

import numpy as np

from . import dispositivo as dev
from . import genoma as gen
from .simulacion import Simulacion


def extraer(isla: Simulacion, k: int, rng: np.random.Generator) -> dict | None:
    """Saca hasta k organismos al azar de la isla (nunca la vacía) y los devuelve como migrantes, en CPU."""
    p = isla.pob
    k = min(k, p.n - 1)
    if k <= 0:
        return None
    elegidos = np.sort(rng.choice(p.n, k, replace=False))
    idx = isla.xp.asarray(elegidos)
    m = {c: dev.a_cpu(p[c][idx]) for c in (*gen.CAMPOS, "E", "generacion", "cepa")}
    queda = np.ones(p.n, dtype=bool)
    queda[elegidos] = False
    p.filtrar(isla.xp.asarray(queda))
    return m


def insertar(isla: Simulacion, m: dict | None, rng: np.random.Generator) -> int:
    """Ubica a los migrantes en celdas libres sorteadas de la isla. Devuelve cuántos llegaron."""
    if m is None:
        return 0
    H, W = isla.entorno.alto, isla.entorno.ancho
    ocupadas = np.zeros(H * W, dtype=bool)
    ocupadas[dev.a_cpu(isla.pob["y"]) * W + dev.a_cpu(isla.pob["x"])] = True
    libres = np.flatnonzero(~ocupadas)
    k = min(len(m["E"]), len(libres))
    if k <= 0:
        return 0
    celdas = rng.choice(libres, k, replace=False)
    nuevos = isla._nuevos({c: m[c][:k] for c in gen.CAMPOS}, celdas // W, celdas % W, m["E"][:k],
                          padre=np.full(k, -1), generacion=m["generacion"][:k], cepa=m["cepa"][:k],
                          estres=np.zeros(k))
    isla.pob.agregar(nuevos)
    return k


class Archipielago:
    """Islas en anillo; cada `cada` pasos, `migrantes` organismos de cada isla pasan a la siguiente."""

    def __init__(self, islas: list[Simulacion], migrantes: int, cada: int, semilla: int):
        self.islas = islas
        self.migrantes = migrantes
        self.cada = cada
        self.rng = np.random.default_rng(np.random.SeedSequence([semilla, 5]))  # solo para la migración
        self.t = 0
        self.migrados = 0

    def paso(self) -> None:
        for isla in self.islas:
            if isla.pob.n:
                isla.paso()
        self.t += 1
        if self.migrantes and self.t % self.cada == 0:
            vivas = [i for i, isla in enumerate(self.islas) if isla.pob.n > 1]
            if len(vivas) < 2:
                return
            # todas eligen sus migrantes antes de recibir: nadie reenvía a un recién llegado
            salen = [extraer(self.islas[i], self.migrantes, self.rng) for i in vivas]
            for j, m in zip(vivas[1:] + vivas[:1], salen):
                self.migrados += insertar(self.islas[j], m, self.rng)
