"""Genoma de genes-regla: cada gen conecta sensores con una primitiva de acción.

Un genoma se representa como un dict de arreglos con una primera dimensión por organismo:
    activo (n, G) bool     - ranura ocupada por un gen
    prim   (n, G) int8     - primitiva que expresa cada gen
    w      (n, G, S)       - pesos sobre los sensores
    b      (n, G)          - sesgo
    mu, sens, eta (n,)     - rasgos heredables: tasa base de mutación,
                             sensibilidad al estrés y tasa de aprendizaje
"""

from __future__ import annotations

import numpy as np

from .config import HerenciaCfg

# Primitivas: la "física" fija de las acciones posibles.
DESCANSAR, AVANZAR, GIRAR_IZQ, GIRAR_DER, VOLTERETA, COMER, DIVIDIRSE = range(7)
PRIMITIVAS = ["descansar", "avanzar", "girar_izq", "girar_der", "voltereta", "comer", "dividirse"]
NUM_PRIM = len(PRIMITIVAS)

# Sensores locales.
(S_CONST, S_AQUI, S_FRENTE, S_FRENTE_IZQ, S_FRENTE_DER, S_ENERGIA,
 S_VECINOS, S_BLOQUEADO, S_DELTA_E, S_RUIDO) = range(10)
SENSORES = ["const", "recurso_aqui", "recurso_frente", "recurso_frente_izq", "recurso_frente_der",
            "energia", "vecinos", "bloqueado", "delta_e", "ruido"]
NUM_SENS = len(SENSORES)

CAMPOS = ("activo", "prim", "w", "b", "mu", "sens", "eta")


def vacio(n: int, genes_max: int) -> dict[str, np.ndarray]:
    return {
        "activo": np.zeros((n, genes_max), dtype=bool),
        "prim": np.zeros((n, genes_max), dtype=np.int8),
        "w": np.zeros((n, genes_max, NUM_SENS)),
        "b": np.zeros((n, genes_max)),
        "mu": np.zeros(n),
        "sens": np.zeros(n),
        "eta": np.zeros(n),
    }


def luca(cfg: HerenciaCfg) -> dict[str, np.ndarray]:
    """Genoma mínimo del primer organismo, diseñado a mano (n = 1)."""
    g = vacio(1, cfg.genes_max)
    genes = [
        # primitiva, sesgo, {sensor: peso}
        (COMER, 0.5, {S_AQUI: 20.0, S_ENERGIA: -3.0}),           # comer si hay recurso y no estoy lleno
        (AVANZAR, 0.3, {S_FRENTE: 4.0, S_AQUI: -10.0, S_BLOQUEADO: -3.0}),  # buscar si aquí no hay
        (VOLTERETA, -0.2, {S_RUIDO: 0.8, S_BLOQUEADO: 2.0}),    # voltereta al azar o si estoy bloqueado
        (DIVIDIRSE, -5.0, {S_ENERGIA: 8.0}),                    # dividirse con energía alta
    ]
    for i, (prim, sesgo, pesos) in enumerate(genes):
        g["activo"][0, i] = True
        g["prim"][0, i] = prim
        g["b"][0, i] = sesgo
        for s, v in pesos.items():
            g["w"][0, i, s] = v
    g["mu"][0] = cfg.mu_inicial
    g["sens"][0] = cfg.sensibilidad_inicial
    g["eta"][0] = cfg.eta_inicial
    return g


def repetir(g: dict[str, np.ndarray], n: int) -> dict[str, np.ndarray]:
    return {k: np.repeat(v, n, axis=0) for k, v in g.items()}


def tomar(g: dict[str, np.ndarray], idx: np.ndarray) -> dict[str, np.ndarray]:
    return {k: v[idx].copy() for k, v in g.items()}


def tasa_efectiva(mu: np.ndarray, sens: np.ndarray, estres: np.ndarray, cfg: HerenciaCfg) -> np.ndarray:
    """Tasa de mutación de la descendencia: μ·(1 + sensibilidad·estrés), con tope tasa_max."""
    if not cfg.mutacion:
        return np.zeros_like(mu)
    if not cfg.estres:
        return np.minimum(mu, cfg.tasa_max)
    return np.minimum(mu * (1.0 + sens * estres), cfg.tasa_max)


def mutar(g: dict[str, np.ndarray], m: np.ndarray, cfg: HerenciaCfg,
          rng: np.random.Generator) -> dict[str, np.ndarray]:
    """Aplica los operadores de mutación in situ con tasa efectiva m (n,) y devuelve g."""
    n, G = g["activo"].shape
    if n == 0 or not cfg.mutacion:
        return g
    mm = m[:, None]
    activo = g["activo"]

    # mutación puntual de pesos y sesgos
    mask_w = (rng.random(g["w"].shape) < m[:, None, None]) & activo[:, :, None]
    g["w"] += mask_w * rng.normal(0.0, cfg.sigma_peso, g["w"].shape)
    mask_b = (rng.random((n, G)) < mm) & activo
    g["b"] += mask_b * rng.normal(0.0, cfg.sigma_peso, (n, G))

    # cambio de primitiva
    mask_p = (rng.random((n, G)) < cfg.k_primitiva * mm) & activo
    g["prim"][mask_p] = rng.integers(0, NUM_PRIM, mask_p.sum())

    # eliminación
    mask_del = (rng.random((n, G)) < cfg.k_eliminacion * mm) & activo
    activo[mask_del] = False

    # duplicación hacia una ranura libre (eventos raros: bucle explícito)
    mask_dup = (rng.random((n, G)) < cfg.k_duplicacion * mm) & activo
    for i, j in zip(*np.nonzero(mask_dup)):
        libres = np.flatnonzero(~activo[i])
        if libres.size == 0:
            continue
        k = libres[0]
        activo[i, k] = True
        g["prim"][i, k] = g["prim"][i, j]
        g["w"][i, k] = g["w"][i, j]
        g["b"][i, k] = g["b"][i, j]

    # gen nuevo aleatorio
    nuevos = np.flatnonzero(rng.random(n) < cfg.k_gen_nuevo * G * m)
    for i in nuevos:
        libres = np.flatnonzero(~activo[i])
        if libres.size == 0:
            continue
        k = libres[0]
        activo[i, k] = True
        g["prim"][i, k] = rng.integers(0, NUM_PRIM)
        g["w"][i, k] = rng.normal(0.0, 1.0, NUM_SENS)
        g["b"][i, k] = rng.normal(0.0, 1.0)

    # rasgos heredables
    rasgos = [("mu", cfg.mu_min, cfg.mu_max), ("eta", 0.0, cfg.eta_max)]
    if cfg.estres:
        rasgos.append(("sens", 0.0, cfg.sensibilidad_max))
    for nombre, lo, hi in rasgos:
        mask = rng.random(n) < np.minimum(1.0, cfg.k_rasgo * m)
        factor = np.exp(rng.normal(0.0, cfg.sigma_log_rasgo, n))
        g[nombre] = np.where(mask, np.clip(g[nombre] * factor, lo, hi), g[nombre])
    return g
