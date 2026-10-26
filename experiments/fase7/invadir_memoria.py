"""Fase 7b: ¿el mundo de la fase 7 premia una memoria de la pista bien usada? (prueba de invasión)

Residentes: una población evolucionada en el mundo de la fase 7 (con memoria disponible). Se siembran 600:
60 % residentes, 20 % mutante con memoria (cepa 1) y 20 % control marcado (cepa 2). Todos reciben cinco genes
extra; solo en el mutante están conectados:
    memoria_a:  20 · pista                  (la pista fija la memoria: 1 en la estación A, 0 en la B)
    comer:      tanh(−5 · tipo − 10 · m)    ⎫ sumados: ≈ 0 si el tipo coincide con la memoria y ≈ −2 si no
    comer:      tanh(5 · tipo + 10 · m − 10) ⎭ (inhibe comer la comida fuera de estación)
    avanzar:    los mismos dos genes con el signo invertido (≈ +2 si no coincide: irse a buscar la otra)
(En el piloto, sin los genes de avanzar, el mutante dejaba de comer la comida mala pero no se iba: giraba en el
lugar y moría de hambre.)
En el control, los cinco genes tienen pesos y sesgo 0 (mismo costo, sin efecto). Sin mutación ni aprendizaje.
La memoria se actualiza con tasa 1 (una pista basta para fijarla).

Uso:
    python experiments/fase7/invadir_memoria.py POBLACION.npz [--semillas 6] [--pasos 20000] [--procesos 4]
"""

from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, genoma as gen, persistencia
from simbio import dispositivo as dev
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "experiments" / "fase7"))
import evaluar as fase7  # noqa: E402

AJUSTES = fase7.MUNDO + ["memoria.activa=true", "memoria.tasa=1.0", "aprendizaje.activo=false",
                         "herencia.mutacion=false"]
GENES = [(gen.MEMORIA_A, 0.0, {gen.S_PISTA: 20.0}),
         (gen.COMER, 0.0, {gen.S_TIPO_AQUI: -5.0, gen.S_MEMORIA_A: -10.0}),
         (gen.COMER, -10.0, {gen.S_TIPO_AQUI: 5.0, gen.S_MEMORIA_A: 10.0}),
         # y avanzar cuando la comida no coincide (≈ +2), para buscar la del tipo correcto
         (gen.AVANZAR, 0.0, {gen.S_TIPO_AQUI: 5.0, gen.S_MEMORIA_A: 10.0}),
         (gen.AVANZAR, 10.0, {gen.S_TIPO_AQUI: -5.0, gen.S_MEMORIA_A: -10.0})]
# fase 9: la misma lógica con genes condicionados (cuarto campo: condición de expresión; 1 = memoria A alta,
# 2 = memoria A baja). Cada gen mira solo el tipo de comida; la memoria decide cuál se expresa. Como en el
# mutante de arriba, valen ≈ 0 si el tipo coincide con la memoria (en el piloto, con ±1, frenar el avance sobre
# la comida correcta lo dejaba quieto en celdas vacías y moría de hambre) y ≈ ∓1 si no coincide
GENES_REGULADOS = [(gen.MEMORIA_A, 0.0, {gen.S_PISTA: 20.0}, 0),
                   (gen.COMER, -5.0, {gen.S_TIPO_AQUI: 5.0}, 1),
                   (gen.COMER, -5.0, {gen.S_TIPO_AQUI: -5.0}, 2),
                   (gen.AVANZAR, 5.0, {gen.S_TIPO_AQUI: -5.0}, 1),
                   (gen.AVANZAR, 5.0, {gen.S_TIPO_AQUI: 5.0}, 2)]


def agregar(g, conectados, genes=GENES):
    for i in range(len(g["mu"])):
        libres = np.flatnonzero(~g["activo"][i])[:len(genes)]
        if libres.size < len(genes):
            raise ValueError("genoma sin ranuras libres")
        for r, (prim, sesgo, pesos, *cond) in zip(libres, genes):
            g["activo"][i, r], g["prim"][i, r] = True, prim
            g["cond"][i, r] = cond[0] if cond and conectados else 0
            g["w"][i, r] = 0.0
            g["b"][i, r] = sesgo if conectados else 0.0
            if conectados:
                for s, v in pesos.items():
                    g["w"][i, r, s] = v


def _correr(tarea):
    ruta, semilla, pasos, castigo = tarea
    g = persistencia.cargar_genomas(Path(ruta))
    caben = np.flatnonzero((~g["activo"]).sum(axis=1) >= len(GENES))
    idx = caben[np.random.default_rng(semilla).integers(0, caben.size, 600)]
    g = {k: v[idx].copy() for k, v in g.items()}
    cepas = np.zeros(600, dtype=np.int16)
    cepas[:120], cepas[120:240] = 1, 2
    sub = {k: v[:120] for k, v in g.items()}
    agregar(sub, True)
    resto = {k: v[120:] for k, v in g.items()}
    agregar(resto, False)
    for k in g:
        g[k][:120], g[k][120:] = sub[k], resto[k]
    cfg = config.cargar(fase7.CONFIG, AJUSTES + [f"estaciones.castigo={castigo}"])
    cfg.sim.semilla = semilla
    sim = Simulacion(cfg, g, cepas)
    # el mutante arranca con la memoria de la estación vigente (como si ya hubiera visto una pista); después
    # depende de las pistas. En el piloto, arrancando en 0 ("estación B" durante la A), evitaba la comida buena
    # y moría de hambre antes de su primera pista
    m = dev.a_cpu(sim.pob["cepa"]) == 1
    sim.pob["memoria"][sim.xp.asarray(np.flatnonzero(m)), 0] = 1.0 if sim.estacion() > 0 else 0.0
    serie = []
    for t in range(pasos):
        sim.paso()
        if sim.t % 1000 == 0:
            c = dev.a_cpu(sim.pob["cepa"])
            serie.append([int((c == k).sum()) for k in range(3)])
    nm, nc = serie[-1][1], serie[-1][2]
    return {"semilla": semilla, "serie": serie, "frac_mutante": nm / (nm + nc) if nm + nc else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("poblacion", type=Path)
    ap.add_argument("--semillas", type=int, default=6)
    ap.add_argument("--semilla-inicial", type=int, default=1)
    ap.add_argument("--pasos", type=int, default=20000)
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--castigo", type=float, default=0.5)
    args = ap.parse_args()
    semillas = range(args.semilla_inicial, args.semilla_inicial + args.semillas)
    with Pool(args.procesos) as pool:
        rs = pool.map(_correr, [(str(args.poblacion), s, args.pasos, args.castigo) for s in semillas])
    print(json.dumps([{k: r[k] for k in ("semilla", "frac_mutante")} | {"final": r["serie"][-1],
                      "inicio": r["serie"][0]} for r in rs], indent=1))


if __name__ == "__main__":
    main()
