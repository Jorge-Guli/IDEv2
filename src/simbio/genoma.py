"""Genoma de genes-regla: cada gen conecta sensores con una primitiva de acción.

Un genoma se representa como un dict de arreglos con una primera dimensión por organismo:
    activo (n, G) bool     - ranura ocupada por un gen
    prim   (n, G) int8     - primitiva que expresa cada gen
    w      (n, G, S)       - pesos sobre los sensores
    b      (n, G)          - sesgo
    mu, sens, eta (n,)     - rasgos heredables: tasa base de mutación,
                             sensibilidad al estrés y tasa de aprendizaje
    etiqueta (n, 2)        - marca heredable sin efecto físico, perceptible por los vecinos
"""

from __future__ import annotations

import numpy as np

from .config import HerenciaCfg
from .dispositivo import a_cpu, modulo

# Primitivas: la "física" fija de las acciones posibles.
(DESCANSAR, AVANZAR, GIRAR_IZQ, GIRAR_DER, VOLTERETA, COMER, DIVIDIRSE,
 UNIRSE, SOLTARSE, COMPARTIR, DIVIDIRSE_UNIDO, CONJUGAR, SECRETAR, SENALAR, MEMORIA_A, MEMORIA_B, ATACAR) = range(17)
PRIMITIVAS = ["descansar", "avanzar", "girar_izq", "girar_der", "voltereta", "comer", "dividirse",
              "unirse", "soltarse", "compartir", "dividirse_unido", "conjugar", "secretar", "senalar",
              "memoria_a", "memoria_b", "atacar"]
PRIM_MEMORIA = np.array([MEMORIA_A, MEMORIA_B])
NUM_PRIM = len(PRIMITIVAS)
# primitivas de los mundos sin ataque (fases 1-12): en ellos el azar y las métricas no cambian por haber agregado
# atacar al final (fase 12, etapa 4)
NUM_PRIM_SIN_ATAQUE = ATACAR
PRIM_BASICAS = np.arange(DIVIDIRSE + 1)
PRIM_ASOCIACION = np.array([UNIRSE, SOLTARSE, COMPARTIR, DIVIDIRSE_UNIDO, CONJUGAR])
# acciones cuyo valor no se mide en energía propia: no se refuerzan por aprendizaje
PRIM_SIN_REFUERZO = np.array([DIVIDIRSE, DIVIDIRSE_UNIDO, COMPARTIR, CONJUGAR, SECRETAR, MEMORIA_A, MEMORIA_B])
# primitivas que no compiten por la acción del paso: sus genes fijan una salida continua (la señal)
PRIM_NO_ACCION = np.array([SENALAR, MEMORIA_A, MEMORIA_B])

# Sensores locales (los sociales van al final para conservar los índices de la fase 1).
(S_CONST, S_AQUI, S_FRENTE, S_FRENTE_IZQ, S_FRENTE_DER, S_ENERGIA,
 S_VECINOS, S_BLOQUEADO, S_DELTA_E, S_RUIDO,
 S_ENLACES, S_ENERGIA_SOCIOS, S_SOCIO_FRENTE, S_SIMILITUD_FRENTE, S_COMPLEJO_AQUI,
 S_RUMBO_SOCIOS_SIN, S_RUMBO_SOCIOS_COS, S_EMPUJE_SOCIOS, S_SENAL_SOCIOS, S_SENAL_PROPIA,
 S_MEMORIA_A, S_MEMORIA_B, S_TIPO_AQUI, S_PISTA, S_PRESION, S_LUZ, S_COINCIDE) = range(27)
SENSORES = ["const", "recurso_aqui", "recurso_frente", "recurso_frente_izq", "recurso_frente_der",
            "energia", "vecinos", "bloqueado", "delta_e", "ruido",
            "enlaces", "energia_socios", "socio_frente", "similitud_frente", "complejo_aqui",
            "rumbo_socios_sin", "rumbo_socios_cos", "empuje_socios", "senal_socios", "senal_propia",
            "memoria_a", "memoria_b", "tipo_aqui", "pista", "presion", "luz", "coincide"]
SENS_MEMORIA = np.array([S_MEMORIA_A, S_MEMORIA_B])
SENS_ESTACIONES = np.array([S_TIPO_AQUI, S_PISTA])
SENS_RUMBO = np.array([S_RUMBO_SOCIOS_SIN, S_RUMBO_SOCIOS_COS, S_EMPUJE_SOCIOS])
SENS_SENAL = np.array([S_SENAL_SOCIOS, S_SENAL_PROPIA])
NUM_SENS = len(SENSORES)
# sensores de los mundos sin datos reales ni estímulos (fases 1-12): en ellos solo mutan estos pesos, así el azar
# que se consume y las dinámicas no cambian por haber agregado al final los sensores nuevos (fase 12, etapas 2 y 3)
NUM_SENS_SIN_REALIDAD = S_PRESION
# con datos reales o estímulos (etapas 2 y 3) mutan también presión y luz, pero no los posteriores
NUM_SENS_REALIDAD = S_COINCIDE

CAMPOS = ("activo", "prim", "w", "b", "mu", "sens", "eta", "etiqueta", "cond")
# condición de expresión de cada gen (fase 9): 0 siempre; 1/2 solo si la memoria A está alta/baja (> 0,5 o ≤ 0,5);
# 3/4 ídem con la memoria B. Solo actúa con la memoria activa
NUM_COND = 5
# fase 11: condiciones de modulación (la memoria A o B cambia el signo del aporte de los sensores del gen)
COND_MODULA_A, COND_MODULA_B = 5, 6
# receptores químicos cuya respuesta puede modularse (fase 11): el tipo de comida de la celda
SENS_MODULABLES = [S_TIPO_AQUI]
NUM_COND_MODULACION = 7


def primitivas_permitidas(asociacion: bool, conjugacion: bool, bien_publico: bool = False,
                          division_unida: bool = True, senales: bool = False, memoria: bool = False,
                          ataque: bool = False) -> np.ndarray:
    permitidas = list(PRIM_BASICAS)
    if asociacion:
        permitidas += [p for p in PRIM_ASOCIACION
                       if (conjugacion or p != CONJUGAR) and (division_unida or p != DIVIDIRSE_UNIDO)]
    if bien_publico:
        permitidas.append(SECRETAR)
    if senales:
        permitidas.append(SENALAR)
    if memoria:
        permitidas += list(PRIM_MEMORIA)
    if ataque:
        permitidas.append(ATACAR)
    return np.array(permitidas)


def compatibilizar(g: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Completa con pesos nulos los genomas guardados con menos sensores (versiones anteriores)."""
    faltan = NUM_SENS - g["w"].shape[-1]
    if faltan > 0:
        g = dict(g)
        g["w"] = np.concatenate([g["w"], np.zeros(g["w"].shape[:-1] + (faltan,))], axis=-1)
    if "cond" not in g:
        g = dict(g)
        g["cond"] = np.zeros(g["activo"].shape, dtype=np.int8)
    return g


def vacio(n: int, genes_max: int, xp=np) -> dict[str, np.ndarray]:
    return {
        "activo": xp.zeros((n, genes_max), dtype=bool),
        "prim": xp.zeros((n, genes_max), dtype=np.int8),
        "w": xp.zeros((n, genes_max, NUM_SENS)),
        "b": xp.zeros((n, genes_max)),
        "mu": xp.zeros(n),
        "sens": xp.zeros(n),
        "eta": xp.zeros(n),
        "etiqueta": xp.zeros((n, 2)),
        "cond": xp.zeros((n, genes_max), dtype=np.int8),
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


def a_dispositivo(g: dict[str, np.ndarray], xp) -> dict[str, np.ndarray]:
    return {k: xp.asarray(v) for k, v in g.items()}


def tomar(g: dict[str, np.ndarray], idx: np.ndarray) -> dict[str, np.ndarray]:
    return {k: v[idx].copy() for k, v in g.items()}


def tasa_efectiva(mu: np.ndarray, sens: np.ndarray, estres: np.ndarray, cfg: HerenciaCfg) -> np.ndarray:
    """Tasa de mutación de la descendencia: μ·(1 + sensibilidad·estrés), con tope tasa_max."""
    xp = modulo(mu)
    if not cfg.mutacion:
        return xp.zeros_like(mu)
    if not cfg.estres:
        return xp.minimum(mu, cfg.tasa_max)
    return xp.minimum(mu * (1.0 + sens * estres), cfg.tasa_max)


def mutar(g: dict[str, np.ndarray], m: np.ndarray, cfg: HerenciaCfg,
          rng: np.random.Generator, permitidas: np.ndarray | None = None,
          n_sens: int = NUM_SENS_SIN_REALIDAD) -> dict[str, np.ndarray]:
    """Aplica los operadores de mutación in situ con tasa efectiva m (n,) y devuelve g.

    `permitidas`: primitivas que pueden aparecer por mutación (por defecto, todas).
    `n_sens`: cuántos sensores (los primeros) tienen pesos que mutan; los demás quedan como están.
    """
    n, G = g["activo"].shape
    if n == 0 or not cfg.mutacion:
        return g
    if permitidas is None:
        permitidas = np.arange(NUM_PRIM_SIN_ATAQUE)
    # el azar sale siempre del generador en CPU y se copia al dispositivo (misma secuencia en CPU y GPU)
    xp = modulo(g["w"])
    A = xp.asarray
    mm = m[:, None]
    activo = g["activo"]

    # mutación puntual de pesos y sesgos
    forma_w = (n, G, n_sens)
    mask_w = (A(rng.random(forma_w)) < m[:, None, None]) & activo[:, :, None]
    g["w"][:, :, :n_sens] += mask_w * A(rng.normal(0.0, cfg.sigma_peso, forma_w))
    mask_b = (A(rng.random((n, G))) < mm) & activo
    g["b"] += mask_b * A(rng.normal(0.0, cfg.sigma_peso, (n, G)))

    # cambio de primitiva
    mask_p = (A(rng.random((n, G))) < cfg.k_primitiva * mm) & activo
    g["prim"][mask_p] = A(rng.choice(permitidas, int(mask_p.sum())).astype(np.int8))

    # cambio de condición de expresión (fase 9): solo si la memoria existe en este mundo
    if MEMORIA_A in permitidas:
        mask_c = (A(rng.random((n, G))) < cfg.k_condicion * mm) & activo
        tope = NUM_COND_MODULACION if cfg.modulacion else NUM_COND
        g["cond"][mask_c] = A(rng.integers(0, tope, int(mask_c.sum())).astype(np.int8))

    # eliminación
    mask_del = (A(rng.random((n, G))) < cfg.k_eliminacion * mm) & activo
    activo[mask_del] = False

    # duplicación hacia una ranura libre (eventos raros: bucle explícito en CPU)
    mask_dup = (A(rng.random((n, G))) < cfg.k_duplicacion * mm) & activo
    pares = a_cpu(xp.stack(xp.nonzero(mask_dup), axis=1))
    if len(pares):
        activo_h = a_cpu(activo).copy()
        for i, j in pares:
            libres = np.flatnonzero(~activo_h[i])
            if libres.size == 0:
                continue
            k = int(libres[0])
            activo_h[i, k] = True
            activo[i, k] = True
            g["prim"][i, k] = g["prim"][i, j]
            g["w"][i, k] = g["w"][i, j]
            g["b"][i, k] = g["b"][i, j]
            g["cond"][i, k] = g["cond"][i, j]

    # gen nuevo aleatorio
    nuevos = np.flatnonzero(rng.random(n) < a_cpu(cfg.k_gen_nuevo * G * m))
    if nuevos.size:
        activo_h = a_cpu(activo).copy()
        for i in nuevos:
            libres = np.flatnonzero(~activo_h[i])
            if libres.size == 0:
                continue
            k = int(libres[0])
            activo_h[i, k] = True
            activo[i, k] = True
            g["prim"][i, k] = int(rng.choice(permitidas))
            g["w"][i, k] = 0.0
            g["w"][i, k, :n_sens] = A(rng.normal(0.0, 1.0, n_sens))
            g["b"][i, k] = float(rng.normal(0.0, 1.0))
            g["cond"][i, k] = 0

    # rasgos heredables
    rasgos = [("mu", cfg.mu_min, cfg.mu_max), ("eta", 0.0, cfg.eta_max)]
    if cfg.estres:
        rasgos.append(("sens", 0.0, cfg.sensibilidad_max))
    for nombre, lo, hi in rasgos:
        mask = A(rng.random(n)) < xp.minimum(1.0, cfg.k_rasgo * m)
        factor = A(np.exp(rng.normal(0.0, cfg.sigma_log_rasgo, n)))
        g[nombre] = xp.where(mask, xp.clip(g[nombre] * factor, lo, hi), g[nombre])

    # etiqueta
    mask = A(rng.random(n)) < xp.minimum(1.0, cfg.k_rasgo * m)
    ruido = A(rng.normal(0.0, cfg.sigma_etiqueta, (n, 2)))
    g["etiqueta"] = xp.where(mask[:, None], xp.clip(g["etiqueta"] + ruido, 0.0, 1.0), g["etiqueta"])
    return g
