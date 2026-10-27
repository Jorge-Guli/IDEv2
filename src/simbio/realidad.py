"""Datos reales (fase 12, etapa 2): una serie horaria de clima regula el mundo.

El acoplamiento es simple y está documentado en config.RealidadCfg:
    radiación   → recrecimiento de la comida (día y noche reales)
    temperatura → costo basal (lejos de la temperatura óptima, vivir cuesta más)
    lluvia      → qué tipo de comida nutre (seco: tipo A; húmedo: tipo B), en lugar de la estación artificial
    presión     → un sensor local con su tendencia reciente, que anticipa la lluvia

Todo se precalcula por hora en la CPU al crear la simulación; en cada paso solo se lee una fila. La simulación
lee el archivo y nada más: los datos los trae un proceso aparte (experiments/herramientas/descargar_clima.py).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .config import RealidadCfg

RAIZ = Path(__file__).resolve().parents[2]


def ubicar(archivo: str) -> Path:
    """Ruta del archivo de datos: tal cual, o relativa a la raíz del repositorio."""
    ruta = Path(archivo)
    if ruta.exists() or ruta.is_absolute():
        return ruta
    return RAIZ / ruta


def promedio_movil(x: np.ndarray, horas: float) -> np.ndarray:
    """Promedio móvil exponencial con constante de tiempo `horas` (solo mira el pasado)."""
    a = 1.0 / max(horas, 1.0)
    out = np.empty_like(x, dtype=np.float64)
    acum = float(x[0])
    for i, v in enumerate(x):
        acum += a * (float(v) - acum)
        out[i] = acum
    return out


class Clima:
    def __init__(self, cfg: RealidadCfg, rng: np.random.Generator):
        self.cfg = cfg
        with np.load(ubicar(cfg.archivo)) as d:
            serie = {k: d[k].astype(np.float64) for k in ("temperatura", "precipitacion", "presion", "radiacion")}
            self.meta = json.loads(str(d["meta"]))
        n = len(serie["temperatura"]) // 24 * 24  # días completos
        serie = {k: v[:n] for k, v in serie.items()}
        self.orden_dias = np.arange(n // 24)
        if cfg.barajar_dias:  # control: mismos días, en otro orden
            self.orden_dias = rng.permutation(n // 24)
            idx = (self.orden_dias[:, None] * 24 + np.arange(24)[None, :]).ravel()
            serie = {k: v[idx] for k, v in serie.items()}
        self.horas = n
        rad = serie["radiacion"]
        a = cfg.acople_radiacion
        self.f_regeneracion = (1.0 - a) + a * rad / max(rad.mean(), 1e-12)
        k = cfg.acople_temperatura
        self.f_basal = 1.0 + k * ((serie["temperatura"] - cfg.temperatura_optima) / 10.0) ** 2
        humedad = promedio_movil(serie["precipitacion"], cfg.ventana_lluvia)
        self.umbral_humedo = float(np.quantile(humedad, 1.0 - cfg.fraccion_humeda))
        self.estacion = np.where(humedad > self.umbral_humedo, -1.0, 1.0)
        v = cfg.ventana_presion
        p = serie["presion"]
        tendencia = np.zeros_like(p)
        tendencia[v:] = p[v:] - p[:-v]
        self.presion = np.clip(tendencia / max(2.0 * tendencia.std(), 1e-12), -1.0, 1.0)
        if cfg.presion_desacoplada:  # control: la presión de otro momento, desplazada medio registro
            self.presion = np.roll(self.presion, n // 2)
        self.serie = serie

    def hora(self, t: int) -> int:
        """Hora de la serie que corresponde al paso t (la serie se repite al terminar)."""
        return (self.cfg.hora_inicial + t // max(self.cfg.pasos_por_hora, 1)) % self.horas
