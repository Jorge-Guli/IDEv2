"""Bucle principal: percepción, decisión, física, asociación, reproducción, muerte y aprendizaje."""

from __future__ import annotations

import numpy as np

from . import genoma as gen
from .config import Config
from .entorno import Entorno
from .poblacion import Poblacion

# Las 8 orientaciones: N, NE, E, SE, S, SO, O, NO. La opuesta de k es (k + 4) % 8.
DY = np.array([-1, -1, 0, 1, 1, 1, 0, -1])
DX = np.array([0, 1, 1, 1, 0, -1, -1, -1])
OPUESTA = (np.arange(8) + 4) % 8


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
        f, a = cfg.fisica, cfg.asociacion
        self.costo_accion = np.zeros(gen.NUM_PRIM)
        self.costo_accion[[gen.AVANZAR, gen.GIRAR_IZQ, gen.GIRAR_DER, gen.VOLTERETA, gen.COMER,
                           gen.UNIRSE, gen.SOLTARSE, gen.COMPARTIR, gen.CONJUGAR]] = [
            f.costo_avanzar, f.costo_girar, f.costo_girar, f.costo_voltereta, f.costo_comer,
            a.costo_unirse, a.costo_soltarse, a.costo_compartir, a.costo_conjugar]
        self.permitidas = gen.primitivas_permitidas(a.activa, a.conjugacion)
        self.bloqueadas = ~np.isin(np.arange(gen.NUM_PRIM), self.permitidas)
        self._reiniciar_contadores()
        self.sembrar(genomas, cepas)

    # ------------------------------------------------------------------ siembra
    def sembrar(self, genomas: dict[str, np.ndarray] | None, cepas: np.ndarray | None) -> None:
        if genomas is None:
            genomas = gen.repetir(gen.luca(self.cfg.herencia), self.cfg.sim.poblacion_inicial)
            genomas["etiqueta"] = self.rng.random((len(genomas["mu"]), 2))
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
    def ocupacion(self, vivos: np.ndarray | None = None) -> np.ndarray:
        occ = np.full((self.entorno.alto, self.entorno.ancho), -1, dtype=np.int32)
        idx = np.arange(self.pob.n, dtype=np.int32) if vivos is None else np.flatnonzero(vivos).astype(np.int32)
        occ[self.pob["y"][idx], self.pob["x"][idx]] = idx
        return occ

    def _resolver(self, candidatos: np.ndarray, celdas: np.ndarray) -> np.ndarray:
        """Entre candidatos que apuntan a la misma celda gana uno al azar. Devuelve las posiciones ganadoras."""
        orden = self.rng.permutation(len(candidatos))
        _, primero = np.unique(celdas[orden], return_index=True)
        return orden[primero]

    def _reiniciar_contadores(self) -> None:
        self.cont = {"nacimientos": 0, "muertes": 0, "comido": 0.0, "org_pasos": 0,
                     "compartido": 0.0, "recibido": 0.0, "conjugaciones": 0, "enlaces_creados": 0,
                     "acciones": np.zeros(gen.NUM_PRIM, dtype=np.int64)}

    def vecinos_enlazados(self, occ: np.ndarray) -> np.ndarray:
        """Índice del organismo en cada dirección enlazada (n, 8), o −1."""
        p = self.pob
        H, W = self.entorno.alto, self.entorno.ancho
        ny = (p["y"][:, None] + DY[None, :]) % H
        nx = (p["x"][:, None] + DX[None, :]) % W
        return np.where(p["socio"] >= 0, occ[ny, nx], -1)

    def validar_enlaces(self, occ: np.ndarray) -> np.ndarray:
        """Rompe los enlaces cuyo socio ya no está en la misma posición relativa. Devuelve los vecinos enlazados."""
        p = self.pob
        j = self.vecinos_enlazados(occ)
        ok = j >= 0
        ok[ok] = p["id"][j[ok]] == p["socio"][ok]
        p["socio"][~ok] = -1
        return np.where(ok, j, -1)

    # ------------------------------------------------------------------ percepción y decisión
    def sensar(self, occ: np.ndarray, socios: np.ndarray) -> np.ndarray:
        p, ent = self.pob, self.entorno
        H, W = ent.alto, ent.ancho
        Emax = self.cfg.fisica.energia_max
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
        s[:, gen.S_ENERGIA] = p["E"] / Emax
        ocupada = (occ >= 0).astype(np.int8)
        vecinos = sum(np.roll(np.roll(ocupada, dy, 0), dx, 1) for dy, dx in zip(DY, DX))
        s[:, gen.S_VECINOS] = vecinos[y, x] / 8.0
        frente = occ[ya, xa]
        s[:, gen.S_BLOQUEADO] = frente >= 0
        s[:, gen.S_DELTA_E] = np.clip(p["delta_e"] / self.cfg.aprendizaje.escala_recompensa, -1, 1)
        s[:, gen.S_RUIDO] = self.rng.uniform(-1.0, 1.0, p.n)
        # sensores sociales
        enlazado = socios >= 0
        n_enl = enlazado.sum(axis=1)
        s[:, gen.S_ENLACES] = n_enl / 8.0
        e_socios = np.where(enlazado, p["E"][np.maximum(socios, 0)], 0.0).sum(axis=1)
        s[:, gen.S_ENERGIA_SOCIOS] = np.where(n_enl > 0, e_socios / np.maximum(n_enl, 1), 0.0) / Emax
        s[:, gen.S_SOCIO_FRENTE] = p["socio"][np.arange(p.n), d] >= 0
        hay = frente >= 0
        dist = np.linalg.norm(p["etiqueta"] - p["etiqueta"][np.maximum(frente, 0)], axis=1)
        hay &= self.cfg.asociacion.activa  # sin asociación, los cuatro sensores sociales valen 0
        s[:, gen.S_SIMILITUD_FRENTE] = np.where(hay, 1.0 - dist / np.sqrt(2.0), 0.0)
        return s

    def decidir(self, s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve la primitiva elegida por cada organismo y la activación de cada gen."""
        p = self.pob
        w = p["w"] + p["P"]
        z = np.einsum("ngs,ns->ng", w, s) + p["b"] + p["p"]
        a = np.tanh(z) * p["activo"]
        expresa = (p["prim"][:, :, None] == np.arange(gen.NUM_PRIM)) & p["activo"][:, :, None]
        impulso = np.einsum("ng,nge->ne", a, expresa)
        disponible = expresa.any(axis=1) & ~self.bloqueadas
        impulso = np.where(disponible, impulso, -np.inf)
        act = np.argmax(impulso, axis=1)
        maximo = impulso[np.arange(p.n), act]
        act = np.where(maximo > 0.0, act, gen.DESCANSAR).astype(np.int8)
        return act, a

    # ------------------------------------------------------------------ aprendizaje
    def aprender(self) -> None:
        p, c = self.pob, self.cfg.aprendizaje
        tuvo = p["ult_act"] >= 0
        # la energía recibida de otros no es resultado de la acción propia: no se refuerza por ella
        dE = p["E"] - p["E_prev"] - p["recibido_paso"]
        p["recibido_paso"] = np.zeros(p.n)
        # acciones sin retorno energético propio (reproducirse, ceder energía o genes) no se evalúan
        valido = tuvo & ~np.isin(p["ult_act"], gen.PRIM_SIN_REFUERZO)
        p["delta_e"] = np.where(valido, dE, 0.0)
        if c.activo:
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
        p["linea_base"] = np.where(valido, (1 - c.memoria_linea_base) * p["linea_base"]
                                   + c.memoria_linea_base * dE, p["linea_base"])

    # ------------------------------------------------------------------ asociación
    def _compartir(self, act: np.ndarray, socios: np.ndarray) -> None:
        p, a = self.pob, self.cfg.asociacion
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        n_enl = (socios >= 0).sum(axis=1)
        donantes = np.flatnonzero((act == gen.COMPARTIR) & (n_enl > 0))
        if donantes.size == 0:
            return
        cedido = a.fraccion_compartir * p["E"][donantes]
        p["E"][donantes] -= cedido
        p["dado"][donantes] += cedido
        filas, dirs = np.nonzero(socios[donantes] >= 0)
        receptores = socios[donantes][filas, dirs]
        cuota = cedido[filas] / n_enl[donantes][filas] * a.eficiencia_compartir
        antes = p["E"].copy()
        np.add.at(p["E"], receptores, cuota)
        np.minimum(p["E"], self.cfg.fisica.energia_max, out=p["E"])
        recibido = p["E"] - antes
        p["recibido"] += recibido
        p["recibido_paso"] += recibido
        self.cont["compartido"] += float(cedido.sum())
        self.cont["recibido"] += float(recibido.sum())

    def _soltarse(self, act: np.ndarray, socios: np.ndarray) -> None:
        p = self.pob
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        filas = np.flatnonzero(act == gen.SOLTARSE)
        if filas.size == 0:
            return
        f, k = np.nonzero(socios[filas] >= 0)
        p["socio"][socios[filas][f, k], OPUESTA[k]] = -1
        p["socio"][filas] = -1

    def _unirse(self, act: np.ndarray, occ: np.ndarray) -> None:
        p = self.pob
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        H, W = self.entorno.alto, self.entorno.ancho
        u = np.flatnonzero(act == gen.UNIRSE)
        if u.size == 0:
            return
        d = p["dir"][u].astype(np.int64)
        j = occ[(p["y"][u] + DY[d]) % H, (p["x"][u] + DX[d]) % W]
        ok = (j >= 0) & (p["socio"][u, d] < 0)
        u, d, j = u[ok], d[ok], j[ok]
        p["socio"][u, d] = p["id"][j]
        p["socio"][j, OPUESTA[d]] = p["id"][u]
        self.cont["enlaces_creados"] += int(u.size)

    def _conjugar(self, act: np.ndarray, socios: np.ndarray) -> None:
        p = self.pob
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        donantes = np.flatnonzero((act == gen.CONJUGAR) & (socios >= 0).any(axis=1))
        for i in donantes:  # evento poco frecuente: bucle explícito
            receptor = self.rng.choice(socios[i][socios[i] >= 0])
            genes = np.flatnonzero(p["activo"][i])
            libres = np.flatnonzero(~p["activo"][receptor])
            if genes.size == 0 or libres.size == 0:
                continue
            g, k = self.rng.choice(genes), libres[0]
            p["activo"][receptor, k] = True
            p["prim"][receptor, k] = p["prim"][i, g]
            p["w"][receptor, k] = p["w"][i, g]
            p["b"][receptor, k] = p["b"][i, g]
            p["P"][receptor, k] = 0.0
            p["p"][receptor, k] = 0.0
            p["ult_a"][receptor, k] = 1.0  # el gen recién llegado no participó de la última acción
            self.cont["conjugaciones"] += 1

    # ------------------------------------------------------------------ movimiento
    def _avanzar(self, act: np.ndarray, occ: np.ndarray, socios: np.ndarray) -> None:
        """Movimiento simultáneo.

        Se puede entrar a una celda libre o a una que deja, en el mismo paso, alguien que avanza en la
        misma dirección (así una fila puede desplazarse entera). Con adhesión, un enlazado solo avanza si
        todos sus enlazados efectivamente avanzan en su misma dirección: el grupo se mueve junto o no se
        mueve; quien queda frenado por la adhesión no paga el costo de avanzar.
        """
        p = self.pob
        H, W = self.entorno.alto, self.entorno.ancho
        i = np.flatnonzero(act == gen.AVANZAR)
        if i.size == 0:
            return
        d = p["dir"].astype(np.int64)
        ty, tx = (p["y"][i] + DY[d[i]]) % H, (p["x"][i] + DX[d[i]]) % W
        ocupante = occ[ty, tx]
        o = np.maximum(ocupante, 0)
        mueve = act == gen.AVANZAR
        candidato = (ocupante < 0) | (mueve[o] & (d[o] == d[i]))
        # adhesión (según la intención): enlazados que no avanzan en la misma dirección frenan al resto
        adhesion = self.cfg.asociacion.adhesion
        if adhesion:
            s_i = socios[i]
            sm = np.maximum(s_i, 0)
            frenado = ((s_i >= 0) & ~(mueve[sm] & (d[sm] == d[i][:, None]))).any(axis=1)
            candidato &= ~frenado
        # conflictos por la misma celda destino: gana uno al azar
        avanza = np.zeros(p.n, dtype=bool)
        g = self._resolver(i[candidato], (ty * W + tx)[candidato])
        avanza[i[candidato][g]] = True
        # punto fijo: se cancela quien entra a la celda de alguien que finalmente no se mueve,
        # o (con adhesión) quien tiene un enlazado que finalmente no se mueve
        while True:
            sigue = avanza[i] & ~((ocupante >= 0) & ~avanza[o])
            if adhesion:
                sigue &= ~((s_i >= 0) & ~avanza[sm]).any(axis=1)
            if np.array_equal(sigue, avanza[i]):
                break
            avanza[i] = sigue
        if adhesion:
            p["E"][i[frenado]] += self.cfg.fisica.costo_avanzar
        m = avanza[i]
        p["y"][i[m]], p["x"][i[m]] = ty[m], tx[m]

    # ------------------------------------------------------------------ paso
    def paso(self) -> None:
        cfg, p, ent = self.cfg, self.pob, self.entorno
        f = cfg.fisica
        H, W = ent.alto, ent.ancho
        ent.paso(self.t)

        if p.n > 0:
            self.aprender()
            occ = self.ocupacion()
            socios = self.validar_enlaces(occ)
            s = self.sensar(occ, socios)
            act, a = self.decidir(s)
            p["ult_s"], p["ult_a"], p["ult_act"] = s, a, act
            p["E_prev"] = p["E"].copy()

            # costos: basal + genoma + acción + enlaces
            p["E"] -= (f.costo_basal + f.costo_por_gen * p["activo"].sum(axis=1) + self.costo_accion[act]
                       + cfg.asociacion.costo_enlace * (socios >= 0).sum(axis=1))

            # quien queda sin energía tras pagar sus costos muere antes de actuar: no come, no se mueve,
            # no ocupa su celda ni sostiene enlaces; se retira al final del paso
            vivos = p["E"] > 0.0
            self.cont["acciones"] += np.bincount(act[vivos], minlength=gen.NUM_PRIM)
            self.cont["org_pasos"] += int(vivos.sum())
            if not vivos.all():
                self.cont["muertes"] += int((~vivos).sum())
                act = np.where(vivos, act, gen.DESCANSAR).astype(np.int8)
                occ = self.ocupacion(vivos)
                socios = self.validar_enlaces(occ)

            # giros
            d = p["dir"].astype(np.int64)
            d = np.where(act == gen.GIRAR_IZQ, (d - 1) % 8, d)
            d = np.where(act == gen.GIRAR_DER, (d + 1) % 8, d)
            volt = act == gen.VOLTERETA
            d[volt] = self.rng.integers(0, 8, volt.sum())
            p["dir"] = d.astype(np.int8)

            # compartir (antes de comer: así quien recibe ajusta lo que toma y el recurso queda en la celda)
            self._compartir(act, socios)

            # comer
            i = np.flatnonzero(act == gen.COMER)
            yi, xi = p["y"][i], p["x"][i]
            toma = np.minimum(np.minimum(ent.R[yi, xi], f.toma_max), np.maximum(f.energia_max - p["E"][i], 0.0))
            ent.R[yi, xi] -= toma
            p["E"][i] += toma
            self.cont["comido"] += float(toma.sum())

            # avanzar
            self._avanzar(act, occ, socios)

            # enlaces: se rompen los estirados, luego soltarse, unirse y conjugar
            occ = self.ocupacion(vivos)
            socios = self.validar_enlaces(occ)
            self._soltarse(act, socios)
            self._unirse(act, occ)
            socios = self.vecinos_enlazados(occ)
            self._conjugar(act, socios)

            # estrés: promedio móvil del hambre (energía bajo el umbral), antes de que dividirse la reparta
            h = cfg.herencia
            hambre = np.clip((h.umbral_hambre - p["E"]) / h.umbral_hambre, 0.0, 1.0)
            p["estres"] = (1 - h.memoria_estres) * p["estres"] + h.memoria_estres * hambre

            # dividirse (suelto o unido)
            nuevos = None
            divide = (act == gen.DIVIDIRSE) | (act == gen.DIVIDIRSE_UNIDO)
            i = np.flatnonzero(divide & (p["E"] >= f.energia_min_division))
            if i.size:
                ny = (p["y"][i, None] + DY[None, :]) % H
                nx = (p["x"][i, None] + DX[None, :]) % W
                libres = occ[ny, nx] < 0
                elegida = np.argmax(np.where(libres, self.rng.random(libres.shape), -1.0), axis=1)
                fila = np.flatnonzero(libres.any(axis=1))
                celdas = ny[fila, elegida[fila]] * W + nx[fila, elegida[fila]]
                g = self._resolver(i[fila], celdas)
                padres, celdas, dirs = i[fila][g], celdas[g], elegida[fila][g]
                if padres.size:
                    p["E"][padres] = (p["E"][padres] - f.costo_division) / 2.0
                    hijos = p.genomas(padres)
                    estres = p["estres"]
                    if h.estres_modo == "barajado":  # control: rompe el vínculo con la condición propia
                        estres = estres[self.rng.permutation(p.n)]
                    m = gen.tasa_efectiva(hijos["mu"], hijos["sens"], estres[padres], h)
                    gen.mutar(hijos, m, h, self.rng, self.permitidas)
                    nuevos = self._nuevos(hijos, celdas // W, celdas % W, p["E"][padres],
                                          padre=p["id"][padres], generacion=p["generacion"][padres] + 1,
                                          cepa=p["cepa"][padres], estres=np.zeros(padres.size))
                    unido = (act[padres] == gen.DIVIDIRSE_UNIDO) & (not cfg.asociacion.inerte)
                    nuevos["dir"][unido] = p["dir"][padres[unido]]  # el clon pegado nace orientado como su progenitor
                    p["socio"][padres[unido], dirs[unido]] = nuevos["id"][unido]
                    nuevos["socio"][np.flatnonzero(unido), OPUESTA[dirs[unido]]] = p["id"][padres[unido]]
                    self.cont["enlaces_creados"] += int(unido.sum())
                    self.cont["nacimientos"] += padres.size

            # bajas y altas en una sola operación (comer, compartir y dividirse no dejan la energía en cero)
            p.actualizar(vivos & (p["E"] > 0.0), nuevos)

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
    def grupos(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Etiqueta de grupo conexo de cada organismo y las aristas (i, j) de los enlaces válidos."""
        p = self.pob
        socios = self.validar_enlaces(self.ocupacion())
        ii, kk = np.nonzero(socios >= 0)
        jj = socios[ii, kk]
        lab = np.arange(p.n)
        while ii.size:
            m = np.minimum(lab[ii], lab[jj])
            nuevo = lab.copy()
            np.minimum.at(nuevo, ii, m)
            np.minimum.at(nuevo, jj, m)
            nuevo = nuevo[nuevo]  # salto de punteros: acelera la convergencia
            if np.array_equal(nuevo, lab):
                break
            lab = nuevo
        return lab, ii, jj

    def medir(self) -> dict[str, float]:
        p, c = self.pob, self.cont
        n = p.n
        fila: dict[str, float] = {"t": self.t, "poblacion": n,
                                  "nacimientos": c["nacimientos"], "muertes": c["muertes"],
                                  "recurso_total": float(self.entorno.R.sum())}
        org_pasos = max(c["org_pasos"], 1)
        fila["comido_por_org_paso"] = c["comido"] / org_pasos
        fila["compartido_por_org_paso"] = c["compartido"] / org_pasos
        fila["recibido_por_org_paso"] = c["recibido"] / org_pasos
        fila["conjugaciones"] = c["conjugaciones"]
        fila["enlaces_creados"] = c["enlaces_creados"]
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
            # organización
            lab, ii, jj = self.grupos()
            tam = np.bincount(lab, minlength=n)[lab]
            n_enl = (p["socio"] >= 0).sum(axis=1)
            enlazado = n_enl > 0
            fila["frac_enlazados"] = float(enlazado.mean())
            fila["enlaces_medios"] = float(n_enl.mean())
            fila["tamano_grupo_medio"] = float(tam.mean())
            fila["tamano_grupo_max"] = int(tam.max())
            fila["grupos_de_3_o_mas"] = float((tam >= 3).mean())
            et = p["etiqueta"]
            fila["dist_etiqueta_enlazados"] = float(np.linalg.norm(et[ii] - et[jj], axis=1).mean()) if ii.size \
                else float("nan")
            azar = np.random.default_rng(self.t)  # generador propio: medir no altera la simulación
            a1, a2 = azar.integers(0, n, (2, min(n, 500)))
            fila["dist_etiqueta_azar"] = float(np.linalg.norm(et[a1] - et[a2], axis=1).mean())
            aprovecha = enlazado & (p["recibido"] > 2.0 * p["dado"] + 5.0)
            fila["frac_aprovechados"] = float(aprovecha.sum() / max(enlazado.sum(), 1))
        for k, nombre in enumerate(gen.PRIMITIVAS):
            fila[f"usa_{nombre}"] = float(c["acciones"][k] / org_pasos)
        return fila
