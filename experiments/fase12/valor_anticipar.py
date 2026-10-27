"""Fase 12, etapa 2: ¿cuánto vale anticipar la lluvia en el clima real? Cálculo sin simulación de organismos.

Para cada regla de memoria se recorre la serie hora a hora: la memoria salta a 1 o a 0 cuando el impulso supera el
cerrojo (|impulso| > 0,5), la digestión la sigue con inercia, y el valor por hora es (2·digestión − 1)·estación
(+1: digestión preparada para la comida que nutre). Valor 0: digestión neutra (LUCA); 1: siempre preparada.

Uso (desde la raíz):  python experiments/fase12/valor_anticipar.py
"""

from __future__ import annotations

import numpy as np

from simbio.config import RealidadCfg
from simbio.realidad import Clima, promedio_movil


def valor(e, regla, inercia_h):
    m, d, tot = 0.5, 0.5, 0.0
    for i in range(len(e)):
        imp = regla(i)
        if abs(imp) > 0.5:
            m = 1.0 if imp > 0 else 0.0
        d += (m - d) / inercia_h
        tot += (2 * d - 1) * e[i]
    return tot / len(e)


def main() -> None:
    c = Clima(RealidadCfg(), np.random.default_rng(0))
    e, p = c.estacion, c.presion
    n = len(e)
    anomalia = c.serie["presion"] - promedio_movil(c.serie["presion"], 24 * 30)
    anomalia = np.clip(anomalia / (2 * anomalia.std()), -1, 1)
    ve = np.random.default_rng(1).random(n) < 1 - 0.99 ** 20  # la pista (p = 0,01 por paso), vista en la hora

    def pista(i):
        return 20 * e[i] if ve[i] else 0.0

    seco = e > 0
    futuro = np.zeros(n, dtype=bool)
    for k in range(1, 13):
        futuro[:-k] |= e[k:] < 0
    print(f"horas húmedas {(e < 0).mean():.3f}; P(empieza lo húmedo en 12 h | seco) = {futuro[seco].mean():.3f}")
    print(f"  con tendencia de presión < −0,5: {futuro[seco & (p < -0.5)].mean():.3f};"
          f" > 0,5: {futuro[seco & (p > 0.5)].mean():.3f}")
    reglas = {
        "siempre seco (memoria 1)": lambda i: 1.0,
        "tendencia b=0 w=3 (duelo)": lambda i: np.tanh(3 * p[i]),
        "tendencia b=2 w=3": lambda i: np.tanh(2 + 3 * p[i]),
        "anomalía b=1 w=3": lambda i: np.tanh(1 + 3 * anomalia[i]),
        "pista": pista,
        "pista + caída < −0,95": lambda i: -1.0 if p[i] < -0.95 else pista(i),
        "oráculo: estación actual": lambda i: e[i],
        "oráculo: estación 12 h antes": lambda i: e[min(i + 12, n - 1)],
        "oráculo: estación 24 h antes": lambda i: e[min(i + 24, n - 1)],
    }
    for inercia in (5, 24, 48):
        print(f"inercia de la digestión {inercia} h")
        for nombre, regla in reglas.items():
            print(f"  {nombre:32s} {valor(e, regla, inercia):+.3f}")


if __name__ == "__main__":
    main()
