"""Población como estructura de arreglos: un arreglo por atributo, una fila por organismo."""

from __future__ import annotations

import numpy as np

from . import genoma as gen

ESTADO = {
    # nombre: (dtype, forma extra)
    "y": (np.int32, ()),
    "x": (np.int32, ()),
    "dir": (np.int8, ()),
    "E": (np.float64, ()),
    "estres": (np.float64, ()),
    "linea_base": (np.float64, ()),
    "delta_e": (np.float64, ()),
    "E_prev": (np.float64, ()),
    "ult_act": (np.int8, ()),
    "id": (np.int64, ()),
    "padre": (np.int64, ()),
    "generacion": (np.int32, ()),
    "nacimiento": (np.int32, ()),
    "cepa": (np.int16, ()),
    "dado": (np.float64, ()),  # energía cedida en la vida
    "recibido": (np.float64, ()),  # energía recibida en la vida
    "recibido_paso": (np.float64, ()),  # energía recibida desde la última decisión
    "senal": (np.float64, ()),  # señal emitida en el último paso (fase 3)
}


class Poblacion:
    def __init__(self, genes_max: int, xp=np):
        self.genes_max = genes_max
        self.xp = xp  # numpy o cupy (ver dispositivo.py)
        self.d: dict[str, np.ndarray] = self.vacia(0)

    def vacia(self, n: int) -> dict[str, np.ndarray]:
        G, xp = self.genes_max, self.xp
        d = {k: xp.zeros((n, *forma), dtype=dt) for k, (dt, forma) in ESTADO.items()}
        d.update(gen.vacio(n, G, xp))
        d["P"] = xp.zeros((n, G, gen.NUM_SENS))  # ajustes plásticos de pesos
        d["p"] = xp.zeros((n, G))  # ajustes plásticos de sesgos
        d["ult_s"] = xp.zeros((n, gen.NUM_SENS))
        d["ult_a"] = xp.zeros((n, G))
        d["ult_act"][:] = -1
        d["socio"] = xp.full((n, 8), -1, dtype=np.int64)  # id del enlazado en cada dirección
        return d

    @property
    def n(self) -> int:
        return len(self.d["E"])

    def __getitem__(self, clave: str) -> np.ndarray:
        return self.d[clave]

    def __setitem__(self, clave: str, valor: np.ndarray) -> None:
        self.d[clave] = valor

    def genomas(self, idx: np.ndarray | None = None) -> dict[str, np.ndarray]:
        if idx is None:
            idx = self.xp.arange(self.n)
        return {k: self.d[k][idx].copy() for k in gen.CAMPOS}

    def agregar(self, nuevos: dict[str, np.ndarray]) -> None:
        for k in self.d:
            self.d[k] = self.xp.concatenate([self.d[k], nuevos[k]], axis=0)

    def filtrar(self, mascara: np.ndarray) -> None:
        for k in self.d:
            self.d[k] = self.d[k][mascara]

    def actualizar(self, mascara: np.ndarray, nuevos: dict[str, np.ndarray] | None) -> None:
        """Conserva las filas de la máscara y agrega los nuevos, tocando solo las filas que cambian.

        Los recién nacidos ocupan las filas de los muertos; los huecos sobrantes se rellenan con las
        últimas filas y se recorta; solo si hay más nacimientos que muertes se concatena el excedente.
        El orden de las filas cambia, pero de forma determinista.
        """
        xp = self.xp
        huecos = xp.flatnonzero(~mascara)
        nn = 0 if nuevos is None else len(nuevos["E"])
        k = min(len(huecos), nn)
        if k:
            for c in self.d:
                self.d[c][huecos[:k]] = nuevos[c][:k]
        if nn > k:
            for c in self.d:
                self.d[c] = xp.concatenate([self.d[c], nuevos[c][k:]], axis=0)
        elif len(huecos) > k:
            restantes = huecos[k:]
            n_final = self.n - len(restantes)
            # filas vivas del final que pasan a ocupar los huecos por debajo de n_final
            destino = restantes[restantes < n_final]
            sobra = xp.zeros(self.n - n_final, dtype=bool)
            sobra[restantes[restantes >= n_final] - n_final] = True
            cola = xp.flatnonzero(~sobra) + n_final
            for c in self.d:
                if destino.size:
                    self.d[c][destino] = self.d[c][cola]
                self.d[c] = self.d[c][:n_final]
