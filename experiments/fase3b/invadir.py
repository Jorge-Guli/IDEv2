"""Fase 3b: prueba de invasión de un mutante coordinado diseñado a mano.

Para cada semilla se genera un ancestro (LUCA, 30 000 pasos en la ecología de la fase 2c con depredador gradual,
igual que en la fase 3). De su población se siembran 600 organismos: 60 % residentes, 20 % mutantes
coordinados (cepa 1) y 20 % control marcado (cepa 2). **Todos** reciben los mismos tres genes extra con los mismos
sesgos (mismo costo genético: en el piloto, 3 genes extra solo en los mutantes, +0,03 por paso, alcanzaban para
eliminarlos); solo en el coordinado esos genes están conectados a los sensores de rumbo y empuje de los socios.
El control marcado es idéntico a los residentes y mide la deriva. Sin mutación: es una prueba de selección.

Los sesgos son 0 a propósito: el impulso de una primitiva es la SUMA de tanh de sus genes, así que un gen con
sesgo negativo restaría impulso a avanzar o girar aunque nunca "gane" (en el piloto, con sesgos negativos, ambos
mutantes se extinguieron en 300 pasos). Con sesgo 0, los genes aportan 0 cuando los sensores de socios valen 0
(sueltos, socios alineados, nadie empuja); los del control aportan siempre 0.

Variantes del coordinado (ver VARIANTES; las prerregistradas son seguir, alinear y ambos):
    girar_der:  4·rumbo_sin       (girar hacia el rumbo de los socios)
    girar_izq:  −4·rumbo_sin      (ídem hacia el otro lado)
    avanzar:    3·empuje_socios   (seguir al que empuja)

Uso:
    python experiments/fase3b/invadir.py --salida runs/fase3b [--procesos 8] [--semillas 10] [--semilla-inicial 51]
        [--variantes seguir alinear ambos]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "experiments" / "fase3"))

from simbio import config, corrida, genoma as gen, persistencia  # noqa: E402
from simbio import dispositivo as dev  # noqa: E402
from simbio.simulacion import Simulacion  # noqa: E402

import evaluar as fase3  # noqa: E402  (generación de ancestros)

CONFIG = RAIZ / "experiments" / "configs" / "coordinacion.toml"
SIEMBRA, FRAC_MUTANTE = 600, 0.20
PASOS = 20_000
CONDICIONES = {
    # el depredador ya escaló: los pares están a salvo solo a medias y los tríos del todo
    "refugio3": ["depredacion.refugio=3", "depredacion.refugio_final=0"],
    # control ecológico: con refugio 2 los pares bastan y coordinarse no debería pagar
    "refugio2": ["depredacion.refugio=2", "depredacion.refugio_final=0"],
}
AJUSTES = ["coordinacion.rumbo=true", "herencia.mutacion=false", "sim.registrar_cada=500"]
VARIANTES = {  # pesos de los tres genes del coordinado: (girar_der, girar_izq, avanzar)
    "ambos": ({gen.S_RUMBO_SOCIOS_SIN: 4.0}, {gen.S_RUMBO_SOCIOS_SIN: -4.0}, {gen.S_EMPUJE_SOCIOS: 3.0}),
    "alinear": ({gen.S_RUMBO_SOCIOS_SIN: 4.0}, {gen.S_RUMBO_SOCIOS_SIN: -4.0}, {}),
    "seguir": ({}, {}, {gen.S_EMPUJE_SOCIOS: 3.0}),
    "ambos_suave": ({gen.S_RUMBO_SOCIOS_SIN: 1.5}, {gen.S_RUMBO_SOCIOS_SIN: -1.5}, {gen.S_EMPUJE_SOCIOS: 1.5}),
    # seguir al que empuja solo si no hay comida en la celda propia
    "ambos_hambre": ({gen.S_RUMBO_SOCIOS_SIN: 1.5}, {gen.S_RUMBO_SOCIOS_SIN: -1.5},
                     {gen.S_EMPUJE_SOCIOS: 3.0, gen.S_AQUI: -10.0}),
}
GENES = [(gen.GIRAR_DER, 0.0), (gen.GIRAR_IZQ, 0.0), (gen.AVANZAR, 0.0)]  # (primitiva, sesgo)


def agregar_genes(g: dict, conectados: bool, variante: str = "ambos") -> dict:
    """Agrega los tres genes en las primeras ranuras libres de cada genoma (in situ)."""
    for i in range(len(g["mu"])):
        libres = np.flatnonzero(~g["activo"][i])
        if libres.size < len(GENES):
            raise ValueError("genoma sin ranuras libres")
        for ranura, (prim, sesgo), pesos in zip(libres, GENES, VARIANTES[variante]):
            g["activo"][i, ranura] = True
            g["prim"][i, ranura] = prim
            g["w"][i, ranura] = 0.0
            g["b"][i, ranura] = sesgo
            if conectados:
                for s, v in pesos.items():
                    g["w"][i, ranura, s] = v
    return g


def siembra(salida, semilla, variante="ambos"):
    g = fase3.siembra(salida, semilla)  # 600 genomas del ancestro, pesos nulos en los sensores nuevos
    if g is None:
        return None, None
    n_mut = int(FRAC_MUTANTE * SIEMBRA)
    cepas = np.zeros(SIEMBRA, dtype=np.int16)
    cepas[:n_mut], cepas[n_mut:2 * n_mut] = 1, 2
    sub = {k: v[:n_mut] for k, v in g.items()}
    agregar_genes(sub, conectados=True, variante=variante)
    for k in g:
        g[k][:n_mut] = sub[k]
    sub = {k: v[n_mut:] for k, v in g.items()}  # control marcado y residentes: los mismos genes, sin conectar
    agregar_genes(sub, conectados=False)
    for k in g:
        g[k][n_mut:] = sub[k]
    return g, cepas


class Observador:
    """Cada 100 pasos, por cepa: cantidad, fracción en grupos ≥ 3 y alineación entre enlazados; y en cada paso,
    la fracción de miembros de grupos ≥ 3 que se desplazaron (movilidad de los grupos grandes)."""

    def __init__(self):
        self.serie = []
        self.mov = np.zeros((3, 2))  # por cepa: [se movieron, observados]
        self.prev = None

    def __call__(self, sim):
        p = sim.pob
        if p.n == 0:
            return
        lab, ii, jj = sim.grupos()
        lab, ii, jj = dev.a_cpu(lab), dev.a_cpu(ii), dev.a_cpu(jj)
        tam = np.bincount(lab, minlength=p.n)[lab]
        ids, cepa = dev.a_cpu(p["id"]), dev.a_cpu(p["cepa"])
        y, x = dev.a_cpu(p["y"]), dev.a_cpu(p["x"])
        if self.prev is not None:
            pid, py, px, ptam = self.prev
            comun, a, b = np.intersect1d(pid, ids, return_indices=True)
            grande = ptam[a] >= 3
            movio = (py[a] != y[b]) | (px[a] != x[b])
            for c in range(3):
                m = grande & (cepa[b] == c)
                self.mov[c] += [movio[m].sum(), m.sum()]
        self.prev = (ids, y, x, tam)
        if sim.t % 100 == 0:
            d = dev.a_cpu(p["dir"]).astype(int)
            fila = {"t": sim.t, "n": p.n}
            for c, nombre in ((0, "residente"), (1, "coordinado"), (2, "control")):
                m = cepa == c
                fila[f"n_{nombre}"] = int(m.sum())
                fila[f"g3_{nombre}"] = float((tam[m] >= 3).mean()) if m.any() else float("nan")
                e = m[ii]
                fila[f"alin_{nombre}"] = (float(np.cos(((d[jj[e]] - d[ii[e]]) % 8) * np.pi / 4).mean())
                                          if e.sum() >= 40 else float("nan"))  # ≥ 20 pares
            self.serie.append(fila)


def _correr(tarea):
    salida, condicion, semilla, variante = tarea
    nombre = f"{condicion}_{variante}"
    g, cepas = siembra(salida, semilla, variante)
    if g is None:
        return {"nombre": nombre, "semilla": semilla, "sin_ancestro": True}
    cfg = config.cargar(CONFIG, AJUSTES + CONDICIONES[condicion])
    cfg.sim.semilla, cfg.sim.pasos = semilla, PASOS
    obs = Observador()
    sim = Simulacion(cfg, g, cepas)
    sim.correr(al_paso=obs)
    destino = Path(salida) / nombre / f"semilla_{semilla}"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "serie.json").write_text(json.dumps(obs.serie), encoding="utf-8")
    final = obs.serie[-1] if obs.serie else {}
    nc, nk = final.get("n_coordinado", 0), final.get("n_control", 0)
    ultimo = [f for f in obs.serie if f["t"] >= 0.75 * PASOS]
    def media(k):
        vals = np.array([f[k] for f in ultimo], dtype=float)
        return float(np.nanmean(vals)) if vals.size and not np.isnan(vals).all() else float("nan")
    return {
        "nombre": nombre, "semilla": semilla, "sin_ancestro": False, "poblacion_final": sim.pob.n,
        "n_residente": final.get("n_residente", 0), "n_coordinado": nc, "n_control": nk,
        "frac_coordinado": nc / (nc + nk) if nc + nk else None,
        "movilidad_g3": {c: (float(obs.mov[i, 0] / obs.mov[i, 1]) if obs.mov[i, 1] >= 200 else None)
                         for i, c in enumerate(("residente", "coordinado", "control"))},
        "g3": {c: media(f"g3_{c}") for c in ("residente", "coordinado", "control")},
        "alineacion": {c: media(f"alin_{c}") for c in ("residente", "coordinado", "control")},
    }


def evaluar_hipotesis(por, variantes):
    """Reglas prerregistradas (docs/bitacora/2026-10-24-fase3b-prerregistro.md). Fracción del coordinado:
    coordinados / (coordinados + control marcado) al final; si se extinguen las dos líneas, no invade."""
    def frac(nombre):
        return {r["semilla"]: r["frac_coordinado"] for r in por.get(nombre, []) if not r["sin_ancestro"]}

    h = {}
    for v in variantes:
        f3 = frac(f"refugio3_{v}")
        if f3:
            inv = [f is not None and f >= 0.7 for f in f3.values()]
            h[f"I1_invade_refugio3_{v}"] = {"frac_coordinado": [None if f is None else round(f, 3) for f in f3.values()],
                                            "invade": sum(inv), "cumple": sum(inv) >= 0.7 * len(inv)}
        f2 = frac(f"refugio2_{v}")
        if f2:
            inv = [f is not None and f >= 0.7 for f in f2.values()]
            h[f"invade_refugio2_{v}"] = {"frac_coordinado": [None if f is None else round(f, 3) for f in f2.values()],
                                         "invade": sum(inv)}
        if f3 and f2:
            pares = [(f3[s], f2[s]) for s in f3 if s in f2]
            mayor = [(a or 0.0) > (b or 0.0) for a, b in pares]
            h[f"I3_mas_ventaja_con_refugio3_{v}"] = {"mayor": sum(mayor), "cumple": sum(mayor) >= 0.7 * len(pares)}
        dif = []
        for r in por.get(f"refugio3_{v}", []):
            m = r.get("movilidad_g3") or {}
            if m.get("coordinado") is not None and m.get("control") is not None:
                dif.append(m["coordinado"] - m["control"])
        h[f"I2_movilidad_g3_{v}"] = {"diferencias": [round(d, 3) for d in dif],
                                      "cumple": bool(dif) and sum(d > 0 for d in dif) >= 0.7 * len(dif)}
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase3b")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--semillas", type=int, default=10)
    ap.add_argument("--semilla-inicial", type=int, default=51)
    ap.add_argument("--variantes", nargs="*", default=["seguir", "alinear", "ambos"])
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    t0 = time.time()
    with Pool(args.procesos) as pool:
        ancestros = pool.map(fase3._ancestro, [(str(args.salida), s) for s in semillas])
        resultados = pool.map(_correr, [(str(args.salida), n, s, v) for v in args.variantes for n in CONDICIONES
                                        for s in semillas])
    por = {}
    for r in resultados:
        por.setdefault(r["nombre"], []).append(r)
    informe = {"parametros": {"pasos": PASOS, "semillas": semillas, "variantes": args.variantes,
                              "minutos": round((time.time() - t0) / 60, 1)},
               "ancestros": ancestros, "hipotesis": evaluar_hipotesis(por, args.variantes), "corridas": resultados}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ancestros": ancestros, "hipotesis": informe["hipotesis"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
