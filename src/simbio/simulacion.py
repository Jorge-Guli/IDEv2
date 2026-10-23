"""Bucle principal: percepción, decisión, física, reproducción, muerte y aprendizaje."""

from __future__ import annotations

import numpy as np

from . import genoma as gen
from .config import Config
from .entorno import Entorno
from .poblacion import Poblacion

# Las 8 orientaciones: N, NE, E, SE, S, SO, O, NO.
DY = np.array([-1, -1, 0, 1, 1, 1, 0, -1])
DX = np.array([0, 1, 1, 1, 0, -1, -1, -1])


class Simulacion:
    def __init__(self, cfg: Config, genomas: dict[str, np.ndarray] | None = None,
                 cepas: np.ndarray | None = None):
        self.cfg = cfg
        semilla_entorno, semilla_sim = np.random.SeedSequence(cfg.sim.semilla).spawn(2)
        self.rng = np.random.default_rng(semilla_sim)
        self.entorno = Entorno(cfg.mundo, np.random.default_rng(semilla_entorno))
        self.pob = Poblacion(cfg.herencia.genes_max)
        self.t = 0
        self.sig_id = 0
        self.historial: list[dict[str, float]] = []
        self.linaje: list[np.ndarray] = []  # filas (id, padre, nacimiento, generacion, cepa)
        f = cfg.fisica
        self.costo_accion = np.zeros(gen.NUM_PRIM)
        self.costo_accion[[gen.AVANZAR, gen.GIRAR_IZQ, gen.GIRAR_DER, gen.VOLTERETA, gen.COMER]] = [
            f.costo_avanzar, f.costo_girar, f.costo_girar, f.costo_voltereta, f.costo_comer]
        self._reiniciar_contadores()
        self.sembrar(genomas, cepas)

    # ------------------------------------------------------------------ siembra
    def sembrar(self, genomas: dict[str, np.ndarray] | None, cepas: np.ndarray | None) -> None:
        if genomas is None:
            genomas = gen.repetir(gen.luca(self.cfg.herencia), self.cfg.sim.poblacion_inicial)
        n = len(genomas["mu"])
        if cepas is None:
            cepas = np.zeros(n, dtype=np.int16)
        H, W = self.entorno.alto, self.entorno.ancho
        celdas = self.rng.choice(H * W, n, replace=False)
        E = np.full(n, self.cfg.fisica.energia_inicial)
        nuevos = self._nuevos(genomas, celdas // W, celdas % W, E,
                              padre=np.full(n, -1), generacion=np.zeros(n, dtype=np.int32),
                              cepa=cepas, estres=np.zeros(n))
        self.pob.agregar(nuevos)

    def _nuevos(self, genomas, y, x, E, padre, generacion, cepa, estres) -> dict[str, np.ndarray]:
        n = len(E)
        d = self.pob.vacia(n)
        for k in gen.CAMPOS:
            d[k] = genomas[k]
        d["y"], d["x"] = y.astype(np.int32), x.astype(np.int32)
        d["dir"] = self.rng.integers(0, 8, n).astype(np.int8)
        d["E"], d["E_prev"] = E.copy(), E.copy()
        d["estres"] = estres.copy()
        d["id"] = np.arange(self.sig_id, self.sig_id + n)
        self.sig_id += n
        d["padre"] = padre
        d["generacion"] = generacion
        d["nacimiento"] = np.full(n, self.t, dtype=np.int32)
        d["cepa"] = cepa.astype(np.int16)
        self.linaje.append(np.stack([d["id"], padre, d["nacimiento"], generacion, d["cepa"]], axis=1))
        return d

    # ------------------------------------------------------------------ helpers
    def ocupacion(self) -> np.ndarray:
        occ = np.full((self.entorno.alto, self.entorno.ancho), -1, dtype=np.int32)
        occ[self.pob["y"], self.pob["x"]] = np.arange(self.pob.n, dtype=np.int32)
        return occ

    def _resolver(self, candidatos: np.ndarray, celdas: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Entre candidatos que apuntan a la misma celda gana uno al azar."""
        orden = self.rng.permutation(len(candidatos))
        _, primero = np.unique(celdas[orden], return_index=True)
        elegidos = orden[primero]
        return candidatos[elegidos], celdas[elegidos]

    def _reiniciar_contadores(self) -> None:
        self.cont = {"nacimientos": 0, "muertes": 0, "comido": 0.0, "org_pasos": 0,
                     "acciones": np.zeros(gen.NUM_PRIM, dtype=np.int64)}

    # ------------------------------------------------------------------ percepción y decisión
    def sensar(self, occ: np.ndarray) -> np.ndarray:
        p, ent = self.pob, self.entorno
        H, W = ent.alto, ent.ancho
        y, x, d = p["y"], p["x"], p["dir"].astype(np.int64)
        R = ent.R / max(self.cfg.mundo.capacidad_max, 1e-12)
        s = np.zeros((p.n, gen.NUM_SENS))
        s[:, gen.S_CONST] = 1.0
        s[:, gen.S_AQUI] = R[y, x]
        ya, xa = (y + DY[d]) % H, (x + DX[d]) % W
        s[:, gen.S_FRENTE] = R[ya, xa]
        di, dd = (d - 1) % 8, (d + 1) % 8
        s[:, gen.S_FRENTE_IZQ] = R[(y + DY[di]) % H, (x + DX[di]) % W]
        s[:, gen.S_FRENTE_DER] = R[(y + DY[dd]) % H, (x + DX[dd]) % W]
        s[:, gen.S_ENERGIA] = p["E"] / self.cfg.fisica.energia_max
        ocupada = (occ >= 0).astype(np.int8)
        vecinos = sum(np.roll(np.roll(ocupada, dy, 0), dx, 1) for dy, dx in zip(DY, DX))
        s[:, gen.S_VECINOS] = vecinos[y, x] / 8.0
        s[:, gen.S_BLOQUEADO] = occ[ya, xa] >= 0
        s[:, gen.S_DELTA_E] = np.clip(p["delta_e"] / self.cfg.aprendizaje.escala_recompensa, -1, 1)
        s[:, gen.S_RUIDO] = self.rng.uniform(-1.0, 1.0, p.n)
        return s

    def decidir(self, s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve la primitiva elegida por cada organismo y la activación de cada gen."""
        p = self.pob
        w = p["w"] + p["P"]
        z = np.einsum("ngs,ns->ng", w, s) + p["b"] + p["p"]
        a = np.tanh(z) * p["activo"]
        expresa = (p["prim"][:, :, None] == np.arange(gen.NUM_PRIM)) & p["activo"][:, :, None]
        impulso = np.einsum("ng,nge->ne", a, expresa)
        impulso = np.where(expresa.any(axis=1), impulso, -np.inf)
        act = np.argmax(impulso, axis=1)
        maximo = impulso[np.arange(p.n), act]
        act = np.where(maximo > 0.0, act, gen.DESCANSAR).astype(np.int8)
        return act, a

    # ------------------------------------------------------------------ aprendizaje
    def aprender(self) -> None:
        p, c = self.pob, self.cfg.aprendizaje
        tuvo = p["ult_act"] >= 0
        dE = p["E"] - p["E_prev"]
        p["delta_e"] = np.where(tuvo, dE, 0.0)
        if c.activo:
            # dividirse no se evalúa por energía: reproducirse es aptitud, no pérdida
            valido = tuvo & (p["ult_act"] != gen.DIVIDIRSE)
            r = np.clip((dE - p["linea_base"]) / c.escala_recompensa, -1.0, 1.0) * valido
            mascara = (p["prim"] == p["ult_act"][:, None]) & p["activo"]
            grad = (1.0 - p["ult_a"] ** 2) * mascara * (p["eta"] * r)[:, None]
            # el decaimiento no puede sacar valores del rango: solo se recortan los genes actualizados
            p["P"] *= 1.0 - c.decaimiento
            p["p"] *= 1.0 - c.decaimiento
            fi, gi = np.nonzero(grad)
            if fi.size:
                p["P"][fi, gi] = np.clip(p["P"][fi, gi] + grad[fi, gi, None] * p["ult_s"][fi], -c.limite, c.limite)
                p["p"][fi, gi] = np.clip(p["p"][fi, gi] + grad[fi, gi], -c.limite, c.limite)
        p["linea_base"] = np.where(tuvo, (1 - c.memoria_linea_base) * p["linea_base"]
                                   + c.memoria_linea_base * dE, p["linea_base"])

    # ------------------------------------------------------------------ paso
    def paso(self) -> None:
        cfg, p, ent = self.cfg, self.pob, self.entorno
        f = cfg.fisica
        H, W = ent.alto, ent.ancho
        ent.paso(self.t)

        if p.n > 0:
            self.aprender()
            occ = self.ocupacion()
            s = self.sensar(occ)
            act, a = self.decidir(s)
            p["ult_s"], p["ult_a"], p["ult_act"] = s, a, act
            p["E_prev"] = p["E"].copy()

            # costos: basal + genoma + acción
            p["E"] -= f.costo_basal + f.costo_por_gen * p["activo"].sum(axis=1) + self.costo_accion[act]

            # giros
            d = p["dir"].astype(np.int64)
            d = np.where(act == gen.GIRAR_IZQ, (d - 1) % 8, d)
            d = np.where(act == gen.GIRAR_DER, (d + 1) % 8, d)
            volt = act == gen.VOLTERETA
            d[volt] = self.rng.integers(0, 8, volt.sum())
            p["dir"] = d.astype(np.int8)

            # comer
            i = np.flatnonzero(act == gen.COMER)
            yi, xi = p["y"][i], p["x"][i]
            toma = np.minimum(np.minimum(ent.R[yi, xi], f.toma_max), np.maximum(f.energia_max - p["E"][i], 0.0))
            ent.R[yi, xi] -= toma
            p["E"][i] += toma
            self.cont["comido"] += float(toma.sum())

            # avanzar (solo hacia celdas libres al inicio del paso)
            i = np.flatnonzero(act == gen.AVANZAR)
            ty = (p["y"][i] + DY[p["dir"][i]]) % H
            tx = (p["x"][i] + DX[p["dir"][i]]) % W
            libre = occ[ty, tx] < 0
            ganadores, celdas = self._resolver(i[libre], (ty * W + tx)[libre])
            p["y"][ganadores], p["x"][ganadores] = celdas // W, celdas % W

            # dividirse
            nuevos = None
            occ = self.ocupacion()
            i = np.flatnonzero((act == gen.DIVIDIRSE) & (p["E"] >= f.energia_min_division))
            if i.size:
                ny = (p["y"][i, None] + DY[None, :]) % H
                nx = (p["x"][i, None] + DX[None, :]) % W
                libres = occ[ny, nx] < 0
                elegida = np.argmax(self.rng.random(libres.shape) * libres, axis=1)
                tiene = libres.any(axis=1)
                fila = np.flatnonzero(tiene)
                celdas = ny[fila, elegida[fila]] * W + nx[fila, elegida[fila]]
                padres, celdas = self._resolver(i[fila], celdas)
                if padres.size:
                    p["E"][padres] = (p["E"][padres] - f.costo_division) / 2.0
                    hijos = p.genomas(padres)
                    m = gen.tasa_efectiva(hijos["mu"], hijos["sens"], p["estres"][padres], cfg.herencia)
                    gen.mutar(hijos, m, cfg.herencia, self.rng)
                    nuevos = self._nuevos(hijos, celdas // W, celdas % W, p["E"][padres],
                                          padre=p["id"][padres], generacion=p["generacion"][padres] + 1,
                                          cepa=p["cepa"][padres], estres=p["estres"][padres])
                    self.cont["nacimientos"] += padres.size

            # muerte (los recién nacidos siempre tienen energía positiva) y altas en una sola operación
            vivos = p["E"] > 0.0
            self.cont["muertes"] += int((~vivos).sum())
            p.actualizar(vivos, nuevos)

            # estrés: promedio móvil del déficit de energía
            alfa = cfg.herencia.memoria_estres
            p["estres"] = (1 - alfa) * p["estres"] + alfa * (1.0 - p["E"] / f.energia_max)

            self.cont["acciones"] += np.bincount(act, minlength=gen.NUM_PRIM)
            self.cont["org_pasos"] += len(act)

        if self.t % cfg.sim.registrar_cada == 0:
            self.historial.append(self.medir())
            self._reiniciar_contadores()
        self.t += 1

    def correr(self, pasos: int | None = None, al_paso=None) -> list[dict[str, float]]:
        for _ in range(self.cfg.sim.pasos if pasos is None else pasos):
            self.paso()
            if al_paso is not None:
                al_paso(self)
        return self.historial

    # ------------------------------------------------------------------ métricas
    def medir(self) -> dict[str, float]:
        p, c = self.pob, self.cont
        n = p.n
        fila: dict[str, float] = {"t": self.t, "poblacion": n,
                                  "nacimientos": c["nacimientos"], "muertes": c["muertes"],
                                  "recurso_total": float(self.entorno.R.sum())}
        org_pasos = max(c["org_pasos"], 1)
        fila["comido_por_org_paso"] = c["comido"] / org_pasos
        if n:
            activo = p["activo"]
            fila.update({
                "energia_media": float(p["E"].mean()),
                "genes_medios": float(activo.sum(1).mean()),
                "mu_media": float(p["mu"].mean()),
                "sens_media": float(p["sens"].mean()),
                "eta_media": float(p["eta"].mean()),
                "estres_medio": float(p["estres"].mean()),
                "tasa_efectiva_media": float(gen.tasa_efectiva(p["mu"], p["sens"], p["estres"],
                                                               self.cfg.herencia).mean()),
                "generacion_media": float(p["generacion"].mean()),
                "generacion_max": int(p["generacion"].max()),
                "frac_cepa1": float((p["cepa"] == 1).mean()),
            })
            perfil = np.stack([((p["prim"] == k) & activo).sum(1) for k in range(gen.NUM_PRIM)], axis=1)
            fila["perfiles_distintos"] = int(len(np.unique(perfil, axis=0)))
            for k, nombre in enumerate(gen.PRIMITIVAS):
                fila[f"tiene_{nombre}"] = float((perfil[:, k] > 0).mean())
        for k, nombre in enumerate(gen.PRIMITIVAS):
            fila[f"usa_{nombre}"] = float(c["acciones"][k] / org_pasos)
        return fila
