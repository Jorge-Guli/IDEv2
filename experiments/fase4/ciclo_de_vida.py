"""Exploración de la fase 4: ciclo de vida de los grupos en una población evolucionada.

Sigue la identidad de cada grupo (componente conexa de enlaces, de 2 o más miembros) paso a paso por máximo
solapamiento de miembros, y registra cómo se fundan los grupos nuevos:
    division   un suelto se divide quedando unido (cuello de botella unicelular, "clonal")
    union      sueltos o grupos que se unen sin un grupo previo dominante
    fision     un fragmento de 2 o más miembros que se separa de un grupo existente
Mide además el tamaño máximo de cada grupo, su duración, la heredabilidad del tamaño (grupo fundador → grupo
hijo) y la diferenciación de conducta dentro de los grupos (bordes contra interior).

Uso:
    python experiments/fase4/ciclo_de_vida.py POBLACION.npz [--pasos 4000] [--semilla 7] [--salida informe.json]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from simbio import config, genoma as gen, persistencia
from simbio import dispositivo as dev
from simbio.simulacion import Simulacion

RAIZ = Path(__file__).resolve().parents[2]
CONFIG = RAIZ / "experiments" / "configs" / "coordinacion.toml"
AJUSTES = ['asociacion.movimiento="fuerza"', "asociacion.exponente_arrastre=0.5", "coordinacion.rumbo=true",
           "coordinacion.senales=true", "herencia.mutacion=false", "depredacion.refugio=3",
           "depredacion.refugio_final=0", "sim.registrar_cada=1000"]


class Rastreador:
    def __init__(self):
        self.sig = 0
        self.grupo_de = {}          # id de organismo -> id de grupo actual (solo en grupos ≥ 2)
        self.ultimo_grupo = {}      # id de organismo -> último grupo al que perteneció
        self.info = {}              # id de grupo -> datos
        self.vivos = set()
        self.acciones = defaultdict(Counter)  # (tamaño, vecinos enlazados) -> acciones
        self.energia = defaultdict(list)      # (tamaño, vecinos enlazados) -> energías
        self.cv_grupo = []                    # coeficiente de variación de la energía dentro de cada grupo ≥ 3
        self.origen_sueltos = Counter()       # cómo aparecen los sueltos nuevos
        self.prev_ids = set()
        self.prev_tam = {}

    def _nuevo(self, t, tipo, padre, tam):
        g = self.sig
        self.sig += 1
        self.info[g] = {"inicio": t, "fin": None, "tipo": tipo, "padre": padre, "max": tam, "tam_ini": tam}
        return g

    def paso(self, sim):
        p, t = sim.pob, sim.t
        lab, _, _ = sim.grupos()
        lab = dev.a_cpu(lab)
        ids = dev.a_cpu(p["id"])
        padre = dev.a_cpu(p["padre"])
        tam = np.bincount(lab, minlength=p.n)
        miembros = defaultdict(list)
        for k in np.flatnonzero(tam[lab] >= 2):
            miembros[lab[k]].append(k)
        # cada componente nueva toma la identidad del grupo previo con el que más solapa, si es su mayor fragmento
        candidatos = []
        for comp, ks in miembros.items():
            previos = Counter(self.grupo_de.get(int(ids[k])) for k in ks)
            previos.pop(None, None)
            candidatos.append((comp, ks, previos))
        reclamado = {}
        for comp, ks, previos in candidatos:
            for g, n in previos.items():
                if n > reclamado.get(g, (0, None))[0]:
                    reclamado[g] = (n, comp)
        nuevo_grupo_de, activos = {}, set()
        for comp, ks, previos in candidatos:
            hereda = [g for g, (n, c) in reclamado.items() if c == comp]
            if hereda:
                g = max(hereda, key=lambda x: reclamado[x][0])
            elif previos:  # fragmento menor de un grupo existente
                g = self._nuevo(t, "fision", previos.most_common(1)[0][0], len(ks))
            else:
                viejos = [int(ids[k]) for k in ks if int(ids[k]) in self.ultimo_grupo or int(padre[k]) < 0]
                es_clon = len(ks) == 2 and (int(padre[ks[0]]) == int(ids[ks[1]]) or int(padre[ks[1]]) == int(ids[ks[0]]))
                origen = None
                for k in ks:
                    origen = origen or self.ultimo_grupo.get(int(ids[k]))
                g = self._nuevo(t, "division" if es_clon else "union", origen, len(ks))
            activos.add(g)
            self.info[g]["max"] = max(self.info[g]["max"], len(ks))
            for k in ks:
                nuevo_grupo_de[int(ids[k])] = g
        for g in self.vivos - activos:
            self.info[g]["fin"] = t
        self.vivos = activos
        for i, g in nuevo_grupo_de.items():
            self.ultimo_grupo[i] = g
        self.grupo_de = nuevo_grupo_de
        # conducta según el tamaño del grupo y la posición (número de socios: borde 1, interior ≥ 3)
        act = dev.a_cpu(p["ult_act"])
        nsoc = dev.a_cpu((p["socio"] >= 0).sum(axis=1))
        E = dev.a_cpu(p["E"])
        for k in range(p.n):
            clave = (int(min(tam[lab[k]], 6)), int(min(nsoc[k], 3)))
            self.acciones[clave][int(act[k])] += 1
            if t % 10 == 0:
                self.energia[clave].append(float(E[k]))
        if t % 10 == 0:
            for comp, ks in miembros.items():
                if len(ks) >= 3:
                    e = E[ks]
                    self.cv_grupo.append(float(e.std() / max(e.mean(), 1e-9)))
        # origen de cada suelto nuevo: recién nacido de un padre suelto, de un padre en grupo, o separado de un grupo
        tam_de = {int(ids[k]): int(tam[lab[k]]) for k in range(p.n)}
        for k in np.flatnonzero(tam[lab] == 1):
            i = int(ids[k])
            if i not in self.prev_ids:
                self.origen_sueltos["nace_de_" + ("padre_en_grupo" if self.prev_tam.get(int(padre[k]), 1) >= 2
                                                  else "padre_suelto")] += 1
            elif self.prev_tam.get(i, 1) >= 2:
                self.origen_sueltos["se_separa_de_grupo"] += 1
        self.prev_ids = set(tam_de)
        self.prev_tam = tam_de


def resumir(r: Rastreador, t_fin):
    terminados = [d for d in r.info.values() if d["fin"] is not None]
    todos = list(r.info.values())
    grandes = [d for d in todos if d["max"] >= 3]
    out = {"grupos_registrados": len(todos),
           "fundacion_todos": dict(Counter(d["tipo"] for d in todos)),
           "fundacion_grupos_que_llegan_a_3": dict(Counter(d["tipo"] for d in grandes)),
           "duracion_mediana": float(np.median([d["fin"] - d["inicio"] for d in terminados])) if terminados else None,
           "duracion_mediana_grupos_3": float(np.median([d["fin"] - d["inicio"] for d in terminados if d["max"] >= 3]))
           if any(d["max"] >= 3 for d in terminados) else None}
    # heredabilidad del tamaño máximo: grupo padre -> grupo hijo
    pares = [(r.info[d["padre"]]["max"], d["max"]) for d in todos if d["padre"] is not None and d["padre"] in r.info]
    for tipo in ("fision", "division", "union"):
        pt = [(r.info[d["padre"]]["max"], d["max"]) for d in todos
              if d["tipo"] == tipo and d["padre"] is not None and d["padre"] in r.info]
        if len(pt) >= 10:
            a, b = np.array(pt, dtype=float).T
            out[f"heredabilidad_tamano_{tipo}"] = {"n": len(pt), "r": round(float(np.corrcoef(a, b)[0, 1]), 3)
                                                   if a.std() > 0 and b.std() > 0 else None}
    out["pares_padre_hijo"] = len(pares)
    conducta = {}
    for (tam, nsoc), c in sorted(r.acciones.items()):
        tot = sum(c.values())
        if tot >= 500:
            conducta[f"tam{tam}_socios{nsoc}"] = {"n": tot, **{gen.PRIMITIVAS[k]: round(v / tot, 3)
                                                               for k, v in c.most_common(5)}}
    out["conducta"] = conducta
    out["energia_media"] = {f"tam{a}_socios{b}": round(float(np.mean(v)), 1)
                            for (a, b), v in sorted(r.energia.items()) if len(v) >= 200}
    out["cv_energia_en_grupos_3"] = round(float(np.mean(r.cv_grupo)), 3) if r.cv_grupo else None
    out["origen_sueltos"] = dict(r.origen_sueltos)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("poblacion", type=Path)
    ap.add_argument("--pasos", type=int, default=4000)
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--salida", type=Path, default=None)
    args = ap.parse_args()
    g = persistencia.cargar_genomas(args.poblacion)
    idx = np.random.default_rng(args.semilla).integers(0, len(g["mu"]), 600)
    cfg = config.cargar(CONFIG, AJUSTES)
    cfg.sim.semilla = args.semilla
    sim = Simulacion(cfg, {k: v[idx] for k, v in g.items()})
    sim.correr(1000)  # que se formen los grupos antes de registrar
    r = Rastreador()
    for _ in range(args.pasos):
        sim.paso()
        r.paso(sim)
    out = resumir(r, sim.t)
    out["poblacion_final"] = sim.pob.n
    texto = json.dumps(out, indent=2, ensure_ascii=False)
    if args.salida:
        args.salida.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
