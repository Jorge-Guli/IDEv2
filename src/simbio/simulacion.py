"""Bucle principal: percepción, decisión, física, asociación, reproducción, muerte y aprendizaje."""

from __future__ import annotations

import numpy as np

from . import dispositivo as dev
from . import genoma as gen
from .config import Config
from .entorno import Entorno, generar_parches
from .poblacion import Poblacion

# Las 8 orientaciones: N, NE, E, SE, S, SO, O, NO. La opuesta de k es (k + 4) % 8.
DY = np.array([-1, -1, 0, 1, 1, 1, 0, -1])
DX = np.array([0, 1, 1, 1, 0, -1, -1, -1])
OPUESTA = (np.arange(8) + 4) % 8


def componentes(socios: np.ndarray) -> np.ndarray:
    """Etiqueta de componente conexa de cada organismo (en CPU) a partir de la matriz de vecinos enlazados."""
    ii, kk = np.nonzero(socios >= 0)
    jj = socios[ii, kk]
    lab = np.arange(len(socios))
    while True:  # propagación de etiquetas mínimas con salto de punteros
        nuevo = lab.copy()
        np.minimum.at(nuevo, ii, lab[jj])
        np.minimum.at(nuevo, jj, lab[ii])
        nuevo = nuevo[nuevo]
        if np.array_equal(nuevo, lab):
            return lab
        lab = nuevo


class Simulacion:
    def __init__(self, cfg: Config, genomas: dict[str, np.ndarray] | None = None,
                 cepas: np.ndarray | None = None):
        self.cfg = cfg
        self.xp, self.dispositivo = dev.elegir(cfg.sim.dispositivo, cfg.mundo.alto * cfg.mundo.ancho,
                                               cfg.sim.umbral_gpu_celdas)
        xp = self.xp
        self.DY, self.DX, self.OPUESTA = xp.asarray(DY), xp.asarray(DX), xp.asarray(OPUESTA)
        # spawn(4) conserva los primeros flujos de spawn(2) y spawn(3): las corridas anteriores no cambian
        semilla_entorno, semilla_sim, semilla_dep, semilla_est = np.random.SeedSequence(cfg.sim.semilla).spawn(4)
        self.rng = np.random.default_rng(semilla_sim)
        self.rng_dep = np.random.default_rng(semilla_dep)  # depredador: mismos sorteos en todos los modos
        self.rng_est = np.random.default_rng(semilla_est)  # estaciones: mapa de tipos y pistas (fase 7)
        self.entorno = Entorno(cfg.mundo, np.random.default_rng(semilla_entorno), xp, cfg.bien_publico)
        if cfg.estaciones.activa:  # tipo de comida de cada celda: +1 (A) o −1 (B), en parches
            campo = generar_parches(cfg.mundo.alto, cfg.mundo.ancho, cfg.estaciones.escala_parche, 1.0, self.rng_est)
            self.tipo = xp.asarray(np.where(campo > np.median(campo), 1.0, -1.0))
        self.pob = Poblacion(cfg.herencia.genes_max, xp)
        self.t = 0
        self.sig_id = 0
        self.historial: list[dict[str, float]] = []
        self.linaje: list[np.ndarray] = []  # filas (id, padre, nacimiento, generacion, cepa)
        f, a = cfg.fisica, cfg.asociacion
        costo = np.zeros(gen.NUM_PRIM)
        costo[[gen.AVANZAR, gen.GIRAR_IZQ, gen.GIRAR_DER, gen.VOLTERETA, gen.COMER,
               gen.UNIRSE, gen.SOLTARSE, gen.COMPARTIR, gen.CONJUGAR, gen.SECRETAR]] = [
            f.costo_avanzar, f.costo_girar, f.costo_girar, f.costo_voltereta, f.costo_comer,
            a.costo_unirse, a.costo_soltarse, a.costo_compartir, a.costo_conjugar, cfg.bien_publico.costo_secretar]
        self.costo_accion = xp.asarray(costo)
        self.sin_refuerzo = xp.asarray(gen.PRIM_SIN_REFUERZO)
        self.permitidas = gen.primitivas_permitidas(a.activa, a.conjugacion, cfg.bien_publico.activo,
                                                    a.division_unida, cfg.coordinacion.senales, cfg.memoria.activa)
        self.bloqueadas = xp.asarray(~np.isin(np.arange(gen.NUM_PRIM), self.permitidas))
        self.no_accion = xp.asarray(np.isin(np.arange(gen.NUM_PRIM), gen.PRIM_NO_ACCION))
        self._reiniciar_contadores()
        self.sembrar(genomas, cepas)

    # ------------------------------------------------------------------ siembra
    def sembrar(self, genomas: dict[str, np.ndarray] | None, cepas: np.ndarray | None) -> None:
        xp = self.xp
        if genomas is None:
            genomas = gen.repetir(gen.luca(self.cfg.herencia), self.cfg.sim.poblacion_inicial)
            genomas["etiqueta"] = self.rng.random((len(genomas["mu"]), 2))
        genomas = gen.a_dispositivo(genomas, xp)
        n = len(genomas["mu"])
        cepas = xp.zeros(n, dtype=xp.int16) if cepas is None else xp.asarray(cepas)
        H, W = self.entorno.alto, self.entorno.ancho
        celdas = xp.asarray(self.rng.choice(H * W, n, replace=False))
        E = xp.full(n, self.cfg.fisica.energia_inicial)
        nuevos = self._nuevos(genomas, celdas // W, celdas % W, E,
                              padre=xp.full(n, -1), generacion=xp.zeros(n, dtype=xp.int32),
                              cepa=cepas, estres=xp.zeros(n))
        self.pob.agregar(nuevos)

    def _nuevos(self, genomas, y, x, E, padre, generacion, cepa, estres) -> dict[str, np.ndarray]:
        xp = self.xp
        # acepta arreglos de CPU o del dispositivo
        genomas = gen.a_dispositivo(genomas, xp)
        y, x, E, padre, generacion, cepa, estres = (xp.asarray(v) for v in (y, x, E, padre, generacion, cepa,
                                                                            estres))
        n = len(E)
        d = self.pob.vacia(n)
        for k in gen.CAMPOS:
            d[k] = genomas[k]
        d["y"], d["x"] = y.astype(xp.int32), x.astype(xp.int32)
        d["dir"] = xp.asarray(self.rng.integers(0, 8, n).astype(np.int8))
        d["E"], d["E_prev"] = E.copy(), E.copy()
        d["estres"] = estres.copy()
        d["memoria"][:] = self.cfg.memoria.inicial
        d["digestion"][:] = 0.5  # neutro: digiere igual los dos tipos
        d["uso_comer"][:] = self.cfg.fisica.maquinaria_ref  # maquinaria de un generalista (fase 5)
        d["uso_avanzar"][:] = self.cfg.fisica.maquinaria_ref
        d["id"] = xp.arange(self.sig_id, self.sig_id + n)
        self.sig_id += n
        d["padre"] = padre
        d["generacion"] = generacion
        d["nacimiento"] = xp.full(n, self.t, dtype=xp.int32)
        d["cepa"] = cepa.astype(xp.int16)
        self.linaje.append(dev.a_cpu(xp.stack([d["id"], padre, d["nacimiento"], generacion, d["cepa"]], axis=1)))
        return d

    # ------------------------------------------------------------------ helpers
    def ocupacion(self, vivos: np.ndarray | None = None) -> np.ndarray:
        xp = self.xp
        occ = xp.full((self.entorno.alto, self.entorno.ancho), -1, dtype=xp.int32)
        idx = xp.arange(self.pob.n, dtype=xp.int32) if vivos is None else xp.flatnonzero(vivos).astype(xp.int32)
        occ[self.pob["y"][idx], self.pob["x"][idx]] = idx
        return occ

    def _resolver(self, candidatos: np.ndarray, celdas: np.ndarray) -> np.ndarray:
        """Entre candidatos que apuntan a la misma celda gana uno al azar. Devuelve las posiciones ganadoras."""
        xp = self.xp
        orden = xp.asarray(self.rng.permutation(len(candidatos)))
        _, primero = xp.unique(celdas[orden], return_index=True)
        return orden[primero]

    def _reiniciar_contadores(self) -> None:
        xp = self.xp
        self.cont = {"nacimientos": 0, "muertes": 0, "comido": 0.0, "org_pasos": 0,
                     "compartido": 0.0, "recibido": 0.0, "comido_libre": 0.0,
                     "comido_libre_sec": 0.0, "comido_libre_nosec": 0.0, "depredados": 0,
                     "depredados_en_refugio": 0, "enlaces_por_union": 0, "enlaces_por_division": 0,
                     "grupos_empujan": 0, "grupos_mueven": 0, "grupos3_empujan": 0, "grupos3_mueven": 0,
                     "grupos_bloqueados": 0, "difundido": 0.0, "comida_buena": 0.0, "comida_mala": 0.0, "conjugaciones": 0, "enlaces_creados": 0,
                     "acciones": xp.zeros(gen.NUM_PRIM, dtype=xp.int64)}

    def vecinos_enlazados(self, occ: np.ndarray) -> np.ndarray:
        """Índice del organismo en cada dirección enlazada (n, 8), o −1."""
        xp = self.xp
        p = self.pob
        H, W = self.entorno.alto, self.entorno.ancho
        ny = (p["y"][:, None] + self.DY[None, :]) % H
        nx = (p["x"][:, None] + self.DX[None, :]) % W
        return xp.where(p["socio"] >= 0, occ[ny, nx], -1)

    def validar_enlaces(self, occ: np.ndarray) -> np.ndarray:
        """Rompe los enlaces cuyo socio ya no está en la misma posición relativa. Devuelve los vecinos enlazados."""
        xp = self.xp
        p = self.pob
        j = self.vecinos_enlazados(occ)
        ok = j >= 0
        ok[ok] = p["id"][j[ok]] == p["socio"][ok]
        p["socio"][~ok] = -1
        return xp.where(ok, j, -1)

    # ------------------------------------------------------------------ percepción y decisión
    def sensar(self, occ: np.ndarray, socios: np.ndarray) -> np.ndarray:
        xp = self.xp
        p, ent = self.pob, self.entorno
        H, W = ent.alto, ent.ancho
        Emax = self.cfg.fisica.energia_max
        y, x, d = p["y"], p["x"], p["dir"].astype(xp.int64)
        R = ent.comestible() / max(self.cfg.mundo.capacidad_max, 1e-12)
        s = xp.zeros((p.n, gen.NUM_SENS))
        s[:, gen.S_CONST] = 1.0
        s[:, gen.S_AQUI] = R[y, x]
        ya, xa = (y + self.DY[d]) % H, (x + self.DX[d]) % W
        s[:, gen.S_FRENTE] = R[ya, xa]
        di, dd = (d - 1) % 8, (d + 1) % 8
        s[:, gen.S_FRENTE_IZQ] = R[(y + self.DY[di]) % H, (x + self.DX[di]) % W]
        s[:, gen.S_FRENTE_DER] = R[(y + self.DY[dd]) % H, (x + self.DX[dd]) % W]
        s[:, gen.S_ENERGIA] = p["E"] / Emax
        ocupada = (occ >= 0).astype(xp.int8)
        vecinos = sum(xp.roll(xp.roll(ocupada, dy, 0), dx, 1) for dy, dx in zip(self.DY, self.DX))
        s[:, gen.S_VECINOS] = vecinos[y, x] / 8.0
        frente = occ[ya, xa]
        s[:, gen.S_BLOQUEADO] = frente >= 0
        s[:, gen.S_DELTA_E] = xp.clip(p["delta_e"] / self.cfg.aprendizaje.escala_recompensa, -1, 1)
        s[:, gen.S_RUIDO] = xp.asarray(self.rng.uniform(-1.0, 1.0, p.n))
        # sensores sociales
        enlazado = socios >= 0
        n_enl = enlazado.sum(axis=1)
        s[:, gen.S_ENLACES] = n_enl / 8.0
        e_socios = xp.where(enlazado, p["E"][xp.maximum(socios, 0)], 0.0).sum(axis=1)
        s[:, gen.S_ENERGIA_SOCIOS] = xp.where(n_enl > 0, e_socios / xp.maximum(n_enl, 1), 0.0) / Emax
        s[:, gen.S_SOCIO_FRENTE] = p["socio"][xp.arange(p.n), d] >= 0
        hay = frente >= 0
        dist = xp.linalg.norm(p["etiqueta"] - p["etiqueta"][xp.maximum(frente, 0)], axis=1)
        hay &= self.cfg.asociacion.activa  # sin asociación, los cuatro sensores sociales valen 0
        s[:, gen.S_SIMILITUD_FRENTE] = xp.where(hay, 1.0 - dist / xp.sqrt(2.0), 0.0)
        if self.cfg.bien_publico.activo:
            s[:, gen.S_COMPLEJO_AQUI] = ent.C[y, x] / max(self.cfg.bien_publico.capacidad_complejo_max, 1e-12)
        self._sensar_coordinacion(s, socios, enlazado, n_enl)
        if self.cfg.memoria.activa:
            s[:, gen.S_MEMORIA_A] = p["memoria"][:, 0]
            s[:, gen.S_MEMORIA_B] = p["memoria"][:, 1]
        e = self.cfg.estaciones
        if e.activa:
            s[:, gen.S_TIPO_AQUI] = self.tipo[y, x]
            u = self.rng_est.random((2, p.n))
            ve = xp.asarray(u[0] < self.p_pista())
            valor = self.estacion() if e.pista_informativa else xp.asarray(np.where(u[1] < 0.5, 1.0, -1.0))
            s[:, gen.S_PISTA] = xp.where(ve, valor, 0.0)
        return s

    def _sensar_coordinacion(self, s, socios, enlazado, n_enl) -> None:
        """Sensores de la fase 3, todos sobre los enlazados (percepción local por contacto): rumbo medio de
        los socios relativo al propio (seno: hacia qué lado girar; coseno: cuán alineados), fracción de socios
        que avanzaron en el paso anterior, señal media de los socios y señal propia del paso anterior."""
        xp, p, c = self.xp, self.pob, self.cfg.coordinacion
        cols = []
        hay = xp.maximum(n_enl, 1)
        sm = xp.maximum(socios, 0)
        if c.rumbo:
            d = p["dir"].astype(xp.int64)
            delta = ((d[sm] - d[:, None] + 4) % 8 - 4) * (np.pi / 4)  # ángulo de cada socio respecto del propio
            s[:, gen.S_RUMBO_SOCIOS_SIN] = xp.where(enlazado, xp.sin(delta), 0.0).sum(axis=1) / hay
            s[:, gen.S_RUMBO_SOCIOS_COS] = xp.where(enlazado, xp.cos(delta), 0.0).sum(axis=1) / hay
            s[:, gen.S_EMPUJE_SOCIOS] = (enlazado & (p["ult_act"][sm] == gen.AVANZAR)).sum(axis=1) / hay
            cols += list(gen.SENS_RUMBO)
        if c.senales:
            s[:, gen.S_SENAL_SOCIOS] = xp.where(enlazado, p["senal"][sm], 0.0).sum(axis=1) / hay
            s[:, gen.S_SENAL_PROPIA] = p["senal"]
            cols += [gen.S_SENAL_SOCIOS]  # la señal propia es memoria, no información sobre los socios
        if c.barajar and cols:
            # control: cada enlazado recibe los valores de otro enlazado al azar (los sueltos siguen en 0); se
            # conserva la distribución condicional a estar enlazado, sin relación con los socios propios
            enl = xp.flatnonzero(n_enl > 0)
            if enl.size > 1:
                cols = xp.asarray(np.array(cols))
                otro = enl[xp.asarray(self.rng.permutation(int(enl.size)))]
                s[enl[:, None], cols[None, :]] = s[otro[:, None], cols[None, :]]

    def decidir(self, s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve la primitiva elegida por cada organismo y la activación de cada gen."""
        xp = self.xp
        p = self.pob
        w = p["w"] + p["P"]
        ws = xp.einsum("ngs,ns->ng", w, s)
        if self.cfg.memoria.activa and self.cfg.herencia.modulacion:
            # modulación (fase 11): en los genes con condición 5 o 6, la memoria A o B cambia el signo de la
            # respuesta a los receptores químicos (gen.SENS_MODULABLES): z = b + w·s + (2m − 1 − 1)·w_q·s_q.
            # Modular un gen que no mira esos receptores es neutro; el uso se construye con sus pesos
            signo = 2.0 * p["memoria"] - 1.0
            mod = xp.where(p["cond"] == gen.COND_MODULA_A, signo[:, 0:1],
                           xp.where(p["cond"] == gen.COND_MODULA_B, signo[:, 1:2], 1.0))
            q = gen.SENS_MODULABLES
            quimico = xp.einsum("ngs,ns->ng", w[:, :, q], s[:, q])
            ws = ws + (mod - 1.0) * quimico
        z = ws + p["b"] + p["p"]
        a = xp.tanh(z) * p["activo"]
        if self.cfg.memoria.activa:  # regulación (fase 9): cada gen se expresa según su condición
            alta = p["memoria"] > 0.5
            uno = xp.ones_like(alta[:, 0])
            puerta = xp.stack([uno, alta[:, 0], ~alta[:, 0], alta[:, 1], ~alta[:, 1], uno, uno], axis=1)
            a = a * xp.take_along_axis(puerta, p["cond"].astype(xp.int64), axis=1)
        expresa = (p["prim"][:, :, None] == xp.arange(gen.NUM_PRIM)) & p["activo"][:, :, None]
        impulso = xp.einsum("ng,nge->ne", a, expresa)
        disponible = expresa.any(axis=1) & ~self.bloqueadas
        # la señal es una salida continua aparte: sus genes no compiten por la acción del paso
        p["senal"] = xp.where(disponible[:, gen.SENALAR], xp.clip(impulso[:, gen.SENALAR], 0.0, 1.0), 0.0)
        if self.cfg.memoria.activa:  # memoria interna: los genes de memoria la suben o bajan
            dm = xp.where(disponible[:, gen.PRIM_MEMORIA], impulso[:, gen.PRIM_MEMORIA], 0.0)
            if self.cfg.memoria.umbral > 0:  # cerrojo (fase 10): los impulsos chicos no mueven la memoria
                dm = xp.where(xp.abs(dm) > self.cfg.memoria.umbral, dm, 0.0)
            p["memoria"] = xp.clip(p["memoria"] + self.cfg.memoria.tasa * dm, 0.0, 1.0)
        impulso = xp.where(disponible & ~self.no_accion, impulso, -xp.inf)
        # restricción flagelar: quien está en período refractario no puede avanzar (elige otra acción)
        impulso[:, gen.AVANZAR] = xp.where(p["refractario"] > 0, -xp.inf, impulso[:, gen.AVANZAR])
        act = xp.argmax(impulso, axis=1)
        maximo = impulso[xp.arange(p.n), act]
        act = xp.where(maximo > 0.0, act, gen.DESCANSAR).astype(xp.int8)
        return act, a

    # ------------------------------------------------------------------ aprendizaje
    def aprender(self) -> None:
        xp = self.xp
        p, c = self.pob, self.cfg.aprendizaje
        tuvo = p["ult_act"] >= 0
        # la energía recibida de otros no es resultado de la acción propia: no se refuerza por ella
        dE = p["E"] - p["E_prev"] - p["recibido_paso"]
        p["recibido_paso"] = xp.zeros(p.n)
        # acciones sin retorno energético propio (reproducirse, ceder energía o genes) no se evalúan
        valido = tuvo & ~xp.isin(p["ult_act"], self.sin_refuerzo)
        p["delta_e"] = xp.where(valido, dE, 0.0)
        if c.activo:
            r = xp.clip((dE - p["linea_base"]) / c.escala_recompensa, -1.0, 1.0) * valido
            mascara = (p["prim"] == p["ult_act"][:, None]) & p["activo"]
            grad = (1.0 - p["ult_a"] ** 2) * mascara * (p["eta"] * r)[:, None]
            # el decaimiento no puede sacar valores del rango: solo se recortan los genes actualizados
            p["P"] *= 1.0 - c.decaimiento
            p["p"] *= 1.0 - c.decaimiento
            fi, gi = xp.nonzero(grad)
            if fi.size:
                p["P"][fi, gi] = xp.clip(p["P"][fi, gi] + grad[fi, gi, None] * p["ult_s"][fi], -c.limite, c.limite)
                p["p"][fi, gi] = xp.clip(p["p"][fi, gi] + grad[fi, gi], -c.limite, c.limite)
        p["linea_base"] = xp.where(valido, (1 - c.memoria_linea_base) * p["linea_base"]
                                   + c.memoria_linea_base * dE, p["linea_base"])

    # ------------------------------------------------------------------ asociación
    def _compartir(self, act: np.ndarray, socios: np.ndarray) -> None:
        xp = self.xp
        p, a = self.pob, self.cfg.asociacion
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        n_enl = (socios >= 0).sum(axis=1)
        donantes = xp.flatnonzero((act == gen.COMPARTIR) & (n_enl > 0))
        if donantes.size == 0:
            return
        cedido = a.fraccion_compartir * p["E"][donantes]
        p["E"][donantes] -= cedido
        p["dado"][donantes] += cedido
        filas, dirs = xp.nonzero(socios[donantes] >= 0)
        receptores = socios[donantes][filas, dirs]
        cuota = cedido[filas] / n_enl[donantes][filas] * a.eficiencia_compartir
        antes = p["E"].copy()
        dev.sumar_en(p["E"], receptores, cuota)
        xp.minimum(p["E"], self.cfg.fisica.energia_max, out=p["E"])
        recibido = p["E"] - antes
        p["recibido"] += recibido
        p["recibido_paso"] += recibido
        self.cont["compartido"] += float(cedido.sum())
        self.cont["recibido"] += float(recibido.sum())

    def _soltarse(self, act: np.ndarray, socios: np.ndarray) -> None:
        xp = self.xp
        p = self.pob
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        filas = xp.flatnonzero(act == gen.SOLTARSE)
        if filas.size == 0:
            return
        f, k = xp.nonzero(socios[filas] >= 0)
        p["socio"][socios[filas][f, k], self.OPUESTA[k]] = -1
        p["socio"][filas] = -1

    def _unirse(self, act: np.ndarray, occ: np.ndarray) -> None:
        xp = self.xp
        p = self.pob
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        H, W = self.entorno.alto, self.entorno.ancho
        u = xp.flatnonzero(act == gen.UNIRSE)
        if u.size == 0:
            return
        d = p["dir"][u].astype(xp.int64)
        j = occ[(p["y"][u] + self.DY[d]) % H, (p["x"][u] + self.DX[d]) % W]
        ok = (j >= 0) & (p["socio"][u, d] < 0)
        u, d, j = u[ok], d[ok], j[ok]
        p["socio"][u, d] = p["id"][j]
        p["socio"][j, self.OPUESTA[d]] = p["id"][u]
        self.cont["enlaces_creados"] += int(u.size)
        self.cont["enlaces_por_union"] += int(u.size)

    def _conjugar(self, act: np.ndarray, socios: np.ndarray) -> None:
        xp = self.xp
        p = self.pob
        if self.cfg.asociacion.inerte:  # control: la acción cuesta pero no tiene efecto
            return
        donantes = dev.a_cpu(xp.flatnonzero((act == gen.CONJUGAR) & (socios >= 0).any(axis=1)))
        for i in donantes:  # evento poco frecuente: bucle explícito en CPU
            fila = dev.a_cpu(socios[i])
            receptor = int(self.rng.choice(fila[fila >= 0]))
            genes = np.flatnonzero(dev.a_cpu(p["activo"][i]))
            libres = np.flatnonzero(~dev.a_cpu(p["activo"][receptor]))
            if genes.size == 0 or libres.size == 0:
                continue
            g, k = int(self.rng.choice(genes)), int(libres[0])
            p["activo"][receptor, k] = True
            p["prim"][receptor, k] = p["prim"][i, g]
            p["w"][receptor, k] = p["w"][i, g]
            p["b"][receptor, k] = p["b"][i, g]
            p["P"][receptor, k] = 0.0
            p["p"][receptor, k] = 0.0
            p["ult_a"][receptor, k] = 1.0  # el gen recién llegado no participó de la última acción
            self.cont["conjugaciones"] += 1

    # ------------------------------------------------------------------ movimiento
    def _avanzar(self, act: np.ndarray, occ: np.ndarray, socios: np.ndarray, vivos=None) -> None:
        """Movimiento simultáneo.

        Se puede entrar a una celda libre o a una que deja, en el mismo paso, alguien que avanza en la
        misma dirección (así una fila puede desplazarse entera). Con adhesión, un enlazado solo avanza si
        todos sus enlazados efectivamente avanzan en su misma dirección: el grupo se mueve junto o no se
        mueve; quien queda frenado por la adhesión no paga el costo de avanzar.
        """
        xp = self.xp
        p = self.pob
        H, W = self.entorno.alto, self.entorno.ancho
        if self.cfg.asociacion.movimiento in ("empuje", "fuerza") and bool((socios >= 0).any()):
            # los grupos enlazados se mueven por empuje colectivo; los sueltos, con la regla común
            enlazado = self._mover_grupos(act, occ, socios)
            act = xp.where(enlazado, gen.DESCANSAR, act).astype(xp.int8)
            occ = self.ocupacion(vivos)
        i = xp.flatnonzero(act == gen.AVANZAR)
        if self.cfg.fisica.maquinaria_gamma > 0 and i.size:
            # maquinaria por uso: un suelto avanza con probabilidad min(1, eficiencia)
            ok = xp.asarray(self.rng.random(int(i.size))) < self.eficiencia(p["uso_avanzar"][i])
            act = act.copy()
            act[i[~ok]] = gen.DESCANSAR
            i = i[ok]
        if i.size == 0:
            return
        d = p["dir"].astype(xp.int64)
        ty, tx = (p["y"][i] + self.DY[d[i]]) % H, (p["x"][i] + self.DX[d[i]]) % W
        ocupante = occ[ty, tx]
        o = xp.maximum(ocupante, 0)
        mueve = act == gen.AVANZAR
        candidato = (ocupante < 0) | (mueve[o] & (d[o] == d[i]))
        # adhesión (según la intención): enlazados que no avanzan en la misma dirección frenan al resto
        adhesion = self.cfg.asociacion.adhesion
        if adhesion:
            s_i = socios[i]
            sm = xp.maximum(s_i, 0)
            frenado = ((s_i >= 0) & ~(mueve[sm] & (d[sm] == d[i][:, None]))).any(axis=1)
            candidato &= ~frenado
        # conflictos por la misma celda destino: gana uno al azar
        avanza = xp.zeros(p.n, dtype=bool)
        g = self._resolver(i[candidato], (ty * W + tx)[candidato])
        avanza[i[candidato][g]] = True
        # punto fijo: se cancela quien entra a la celda de alguien que finalmente no se mueve,
        # o (con adhesión) quien tiene un enlazado que finalmente no se mueve
        while True:
            sigue = avanza[i] & ~((ocupante >= 0) & ~avanza[o])
            if adhesion:
                sigue &= ~((s_i >= 0) & ~avanza[sm]).any(axis=1)
            if xp.array_equal(sigue, avanza[i]):
                break
            avanza[i] = sigue
        if adhesion:
            p["E"][i[frenado]] += self.cfg.fisica.costo_avanzar
        m = avanza[i]
        p["y"][i[m]], p["x"][i[m]] = ty[m], tx[m]

    def eficiencia(self, uso):
        """Maquinaria por uso (fase 5): eficiencia de una acción según su uso reciente."""
        f = self.cfg.fisica
        return self.xp.minimum(f.maquinaria_max, (uso / f.maquinaria_ref) ** f.maquinaria_gamma)

    def estacion(self) -> float:
        """Estación vigente (fase 7): +1 nutre el tipo A, −1 nutre el tipo B."""
        return 1.0 if (self.t // self.cfg.estaciones.periodo) % 2 == 0 else -1.0

    def p_pista(self) -> float:
        """Probabilidad vigente de percibir la pista (fase 10: rampa desde `p_pista_inicial`)."""
        e = self.cfg.estaciones
        if e.rampa_pista <= 0:
            return e.p_pista
        f = min(1.0, self.t / e.rampa_pista)
        return e.p_pista_inicial + f * (e.p_pista - e.p_pista_inicial)

    def factor_toxicidad(self) -> float:
        """Fracción de la toxicidad plena vigente (fase 9: rampa desde 0)."""
        r = self.cfg.estaciones.rampa_toxicidad
        return min(1.0, self.t / r) if r > 0 else 1.0

    def refugio_actual(self) -> float:
        """Tamaño de refugio vigente: `refugio`, o la interpolación lineal hacia `refugio_final` si hay escalada."""
        d = self.cfg.depredacion
        if d.refugio_final <= 0 or self.t < d.escalada_inicio:
            return float(d.refugio)
        f = min(1.0, (self.t - d.escalada_inicio) / d.escalada_pasos) if d.escalada_pasos > 0 else 1.0
        return d.refugio + f * (d.refugio_final - d.refugio)

    def _depredar(self, socios) -> None:
        """Ataques del depredador sobre los vivos (tras pagar los costos del paso). Modo "tamano": el ataque
        mata según el tamaño del grupo conexo de vivos (refugio); "uniforme": siempre mata; "aleatorio":
        perdona con prob_perdon, sin relación con los enlaces. Se sortean siempre los mismos números con un
        generador propio, de modo que los modos son comparables semilla a semilla. Los muertos quedan sin
        energía y mueren antes de actuar en este paso."""
        p, d = self.pob, self.cfg.depredacion
        u_ataque, u_letal = self.rng_dep.random(p.n), self.rng_dep.random(p.n)
        if self.t < d.inicio:
            return
        vivo = dev.a_cpu(p["E"]) > 0.0
        intensidad = d.prob_ataque * (min(1.0, (self.t - d.inicio + 1) / d.rampa) if d.rampa > 0 else 1.0)
        atacado = vivo & (u_ataque < intensidad)
        if d.modo == "tamano":
            soc = dev.a_cpu(socios).copy()
            soc[~vivo] = -1
            soc[(soc >= 0) & ~vivo[np.maximum(soc, 0)]] = -1  # quien muere de hambre en este paso no protege
            lab = componentes(soc)
            tam = np.bincount(lab, minlength=p.n)[lab]
            R = self.refugio_actual()
            if d.gradual and R > 1:
                # cuanto más grande el grupo, más difícil de tragar: muerte con prob. 1 − (tam − 1)/(R − 1)
                mata = np.clip(1.0 - (tam - 1) / (R - 1), 0.0, 1.0)
            else:
                mata = (tam < R).astype(float)
            letal = atacado & (u_letal < mata)
            self.cont["depredados_en_refugio"] += int((letal & (tam >= R)).sum())
        elif d.modo == "aleatorio":
            letal = atacado & (u_letal >= d.prob_perdon)
        else:
            letal = atacado
        p["E"][self.xp.asarray(np.flatnonzero(letal))] = -1.0
        self.cont["depredados"] += int(letal.sum())

    def _mover_grupos(self, act, occ, socios):
        """Empuje colectivo: cada grupo conexo se desplaza una celda en la dirección (de las 8) más alineada
        con la suma de las orientaciones de sus miembros que eligieron avanzar, si esa suma alcanza
        `fraccion_empuje` × tamaño (modo "empuje") o con probabilidad fuerza/tamaño^α (modo "fuerza"), y si todas
        las celdas de destino están libres o son del propio grupo.
        Los grupos se procesan en orden aleatorio. Devuelve la máscara de organismos enlazados."""
        xp, p, cfg = self.xp, self.pob, self.cfg.asociacion
        H, W = self.entorno.alto, self.entorno.ancho
        soc = dev.a_cpu(socios)
        enlazado = (soc >= 0).any(axis=1)
        lab = componentes(soc)
        y, x = dev.a_cpu(p["y"]).copy(), dev.a_cpu(p["x"]).copy()
        d, a = dev.a_cpu(p["dir"]).astype(np.int64), dev.a_cpu(act)
        ocup = dev.a_cpu(occ).copy()
        # grupos en orden de su menor índice (la etiqueta de componentes es el menor índice del grupo)
        idx = np.flatnonzero(enlazado)
        etiquetas, gi = np.unique(lab[idx], return_inverse=True)
        n_g = etiquetas.size
        orden = np.argsort(gi, kind="stable")
        inicio = np.r_[0, np.cumsum(np.bincount(gi, minlength=n_g))]
        tam = np.diff(inicio)
        # empujes sumados por grupo, vectorizados; el bucle solo recorre los grupos que alcanzan el umbral
        emp = a[idx] == gen.AVANZAR
        n_emp = np.bincount(gi, weights=emp, minlength=n_g)
        vx = np.bincount(gi, weights=emp * DX[d[idx]], minlength=n_g)
        vy = np.bincount(gi, weights=emp * DY[d[idx]], minlength=n_g)
        hay = n_emp > 0
        self.cont["grupos_empujan"] += int(hay.sum())
        self.cont["grupos3_empujan"] += int((hay & (tam >= 3)).sum())
        norma = np.hypot(DX, DY)
        if cfg.movimiento == "fuerza":
            # fuerza neta sobre arrastre: cada empuje es un vector unitario (sin ventaja diagonal); el grupo se
            # desplaza con probabilidad (fuerza en la dirección elegida) / tamaño^α, sin umbral
            if self.cfg.fisica.maquinaria_gamma > 0:  # cada empuje pesa según la maquinaria de quien empuja
                emp = emp * dev.a_cpu(self.eficiencia(p["uso_avanzar"]))[idx]
            vx = np.bincount(gi, weights=emp * (DX / norma)[d[idx]], minlength=n_g)
            vy = np.bincount(gi, weights=emp * (DY / norma)[d[idx]], minlength=n_g)
            kg = np.argmax((DX[None, :] * vx[:, None] + DY[None, :] * vy[:, None]) / norma[None, :], axis=1)
            proyeccion = (vx * DX[kg] + vy * DY[kg]) / norma[kg]
            prob = np.minimum(1.0, proyeccion / tam ** cfg.exponente_arrastre)
            candidato = hay & (self.rng.random(n_g) < prob)
        else:
            candidato = hay & (np.hypot(vx, vy) >= cfg.fraccion_empuje * tam)
            kg = np.argmax((DX[None, :] * vx[:, None] + DY[None, :] * vy[:, None]) / norma[None, :], axis=1)
        # camino rápido exacto (mismo resultado que procesar todo en orden aleatorio):
        # - bloqueado fijo: alguna celda de destino la ocupa alguien que no se moverá en esta etapa
        #   (un suelto o un grupo que no alcanza el umbral);
        # - independiente: todas las celdas de destino están libres o son del propio grupo, ningún otro
        #   candidato apunta a ellas ni a las celdas que el grupo deja. Su movimiento no depende del orden.
        cand_i = candidato[gi]
        ki = kg[gi]
        ny_i, nx_i = (y[idx] + DY[ki]) % H, (x[idx] + DX[ki]) % W
        dc = ny_i * W + nx_i
        sc = y[idx] * W + x[idx]
        o = ocup[ny_i, nx_i]
        grupo_de = np.full(len(a), -1)
        grupo_de[idx] = gi
        propio = (o >= 0) & (grupo_de[np.maximum(o, 0)] == gi)
        go = grupo_de[np.maximum(o, 0)]
        ocupante_fijo = (o >= 0) & ~propio & ((go < 0) | ~candidato[np.maximum(go, 0)])
        ocupado_ajeno = (o >= 0) & ~propio
        celdas = H * W
        n_dest = np.bincount(dc[cand_i], minlength=celdas)
        propio_destino = np.zeros(len(a), dtype=bool)  # su celda de origen es destino de su propio grupo
        propio_destino[o[propio & cand_i]] = True
        ajeno_en_origen = n_dest[sc] - propio_destino[idx]
        malo = ocupado_ajeno | (n_dest[dc] > 1) | (ajeno_en_origen > 0)
        fijo = candidato & (np.bincount(gi, weights=ocupante_fijo, minlength=n_g) > 0)
        indep = candidato & ~fijo & (np.bincount(gi, weights=malo, minlength=n_g) == 0)
        self.cont["grupos_bloqueados"] += int(fijo.sum())
        self.cont["grupos_mueven"] += int(indep.sum())
        self.cont["grupos3_mueven"] += int((indep & (tam >= 3)).sum())
        mi = indep[gi]
        if mi.any():
            ocup[y[idx[mi]], x[idx[mi]]] = -1
            ocup[ny_i[mi], nx_i[mi]] = idx[mi]
            y[idx[mi]], x[idx[mi]] = ny_i[mi], nx_i[mi]
        resto = candidato & ~fijo & ~indep
        for g in self.rng.permutation(n_g):
            if not resto[g]:
                continue
            m = idx[orden[inicio[g]:inicio[g + 1]]]
            k = int(kg[g])
            ny, nx = (y[m] + DY[k]) % H, (x[m] + DX[k]) % W
            destino = ocup[ny, nx]
            if not np.all((destino < 0) | (lab[np.maximum(destino, 0)] == lab[m[0]])):
                self.cont["grupos_bloqueados"] += 1
                continue
            self.cont["grupos_mueven"] += 1
            self.cont["grupos3_mueven"] += int(m.size >= 3)
            ocup[y[m], x[m]] = -1
            ocup[ny, nx] = m
            y[m], x[m] = ny, nx
        p["y"], p["x"] = xp.asarray(y.astype(np.int32)), xp.asarray(x.astype(np.int32))
        return xp.asarray(enlazado)

    # ------------------------------------------------------------------ paso
    def paso(self) -> None:
        xp = self.xp
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

            # veneno diferido (fase 7): se descuenta de a poco
            if cfg.estaciones.activa and cfg.estaciones.toxicidad == "diferido":
                dosis = cfg.estaciones.tasa_veneno * p["veneno"]
                p["veneno"] -= dosis
                p["E"] -= dosis

            # costos: basal + genoma + acción + enlaces
            p["E"] -= (f.costo_basal + f.costo_por_gen * p["activo"].sum(axis=1) + self.costo_accion[act]
                       + cfg.asociacion.costo_enlace * (socios >= 0).sum(axis=1)
                       + cfg.coordinacion.costo_senal * p["senal"])

            # depredación (tras los costos, para no alterar lo que perciben los vecinos en este paso)
            if cfg.depredacion.activa:
                self._depredar(socios)

            # quien queda sin energía tras pagar sus costos muere antes de actuar: no come, no se mueve,
            # no ocupa su celda ni sostiene enlaces; se retira al final del paso
            vivos = p["E"] > 0.0
            self.cont["acciones"] += xp.bincount(act[vivos], minlength=gen.NUM_PRIM)
            p["n_avances"] += (act == gen.AVANZAR) & vivos
            # uso reciente (se registra siempre, también para medir roles en el control γ = 0)
            r = f.maquinaria_memoria
            p["uso_comer"] += r * ((act == gen.COMER) - p["uso_comer"])
            p["uso_avanzar"] += r * ((act == gen.AVANZAR) - p["uso_avanzar"])
            p["refractario"] = xp.maximum(p["refractario"] - 1, 0).astype(xp.int16)
            if cfg.estaciones.induccion > 0 and cfg.memoria.activa:
                # las enzimas siguen a la memoria A con inercia: una memoria que cambia de celda en celda se
                # promedia y no prepara nada; solo una sostenida (como la estación) da ventaja
                p["digestion"] += (p["memoria"][:, 0] - p["digestion"]) / max(cfg.estaciones.inercia_digestion, 1)
            self.cont["org_pasos"] += int(vivos.sum())
            if not vivos.all():
                self.cont["muertes"] += int((~vivos).sum())
                act = xp.where(vivos, act, gen.DESCANSAR).astype(xp.int8)
                occ = self.ocupacion(vivos)
                socios = self.validar_enlaces(occ)
                socios[~vivos] = -1  # los muertos no sostienen enlaces ni empujan

            # giros
            d = p["dir"].astype(xp.int64)
            d = xp.where(act == gen.GIRAR_IZQ, (d - 1) % 8, d)
            d = xp.where(act == gen.GIRAR_DER, (d + 1) % 8, d)
            volt = act == gen.VOLTERETA
            d[volt] = xp.asarray(self.rng.integers(0, 8, int(volt.sum())))
            p["dir"] = d.astype(xp.int8)

            # compartir (antes de comer: así quien recibe ajusta lo que toma y el recurso queda en la celda)
            self._compartir(act, socios)

            # comer
            i = xp.flatnonzero(act == gen.COMER)
            yi, xi = p["y"][i], p["x"][i]
            # maquinaria por uso (fase 5): el rendimiento (energía por unidad de recurso) depende del uso reciente;
            # con γ = 0 el rendimiento es 1 y todo queda como antes
            rinde = self.eficiencia(p["uso_comer"][i]) if f.maquinaria_gamma > 0 else 1.0
            toma = xp.minimum(xp.minimum(ent.comestible()[yi, xi], f.toma_max),
                              xp.maximum(f.energia_max - p["E"][i], 0.0) / rinde)
            del_simple = xp.minimum(toma, ent.R[yi, xi])  # primero el recurso simple, después el libre
            ent.R[yi, xi] -= del_simple
            if cfg.bien_publico.activo:
                libre = toma - del_simple
                ent.A[yi, xi] -= libre
                xp.maximum(ent.A, 0.0, out=ent.A)  # (R + A) − R puede diferir de A en el redondeo
                secretor = (p["prim"][i] == gen.SECRETAR).any(axis=1) & p["activo"][i].any(axis=1)
                self.cont["comido_libre"] += float(libre.sum())
                self.cont["comido_libre_sec"] += float(libre[secretor].sum())
                self.cont["comido_libre_nosec"] += float(libre[~secretor].sum())
            if cfg.estaciones.activa:  # fase 7: la comida del tipo fuera de estación es tóxica
                buena = self.tipo[yi, xi] * self.estacion() > 0
                ind = cfg.estaciones.induccion
                if ind > 0 and cfg.memoria.activa:
                    # digestión inducible (fase 10): el estado digestivo (que sigue a la memoria A) prepara un
                    # tipo (alto: A, bajo: B); se absorbe más (nutrientes y veneno) del preparado y menos del otro
                    rinde = rinde * (1.0 + ind * (2.0 * p["digestion"][i] - 1.0) * self.tipo[yi, xi])
                tox = (1.0 + cfg.estaciones.castigo) * self.factor_toxicidad()
                if cfg.estaciones.toxicidad == "diferido":
                    p["veneno"][i] += xp.where(buena, 0.0, tox * toma * rinde)
                else:
                    rinde = rinde * xp.where(buena, 1.0, 1.0 - tox)
                self.cont["comida_buena"] += float(toma[buena].sum())
                self.cont["comida_mala"] += float(toma[~buena].sum())
            p["E"][i] += toma * rinde
            self.cont["comido"] += float(toma.sum())

            # puentes citoplasmáticos (fase 5): la energía se difunde por los enlaces, sin decisión del genoma
            kappa = cfg.asociacion.difusion_energia
            if kappa > 0 and not cfg.asociacion.inerte:
                hay = socios >= 0
                E = p["E"]
                flujo = kappa * xp.where(hay, E[xp.maximum(socios, 0)] - E[:, None], 0.0).sum(axis=1) / 8.0
                p["E"] = E + flujo
                if not cfg.asociacion.difusion_aprende:
                    p["recibido_paso"] += flujo  # no es resultado de la acción propia: no entra al aprendizaje
                self.cont["difundido"] += float(xp.abs(flujo).sum()) / 2.0

            # secretar enzima (después de comer, en la propia celda)
            bp = cfg.bien_publico
            if bp.activo and not bp.secrecion_inerte:
                i = xp.flatnonzero(act == gen.SECRETAR)
                yi, xi = p["y"][i], p["x"][i]
                if bp.privado:
                    # control de bien privado: digiere ya en su celda lo que la enzima digeriría en su vida
                    # (exponente k·Z/δ) y se lo queda el secretor; no deja enzima
                    d = ent.C[yi, xi] * (1.0 - xp.exp(-bp.tasa_digestion * bp.enzima_por_secrecion
                                                       / max(bp.degradacion_enzima, 1e-9)))
                    ent.C[yi, xi] -= d
                    p["E"][i] = xp.minimum(p["E"][i] + bp.rendimiento * d, f.energia_max)
                else:
                    ent.Z[yi, xi] += bp.enzima_por_secrecion

            # avanzar
            self._avanzar(act, occ, socios, vivos)

            # enlaces: se rompen los estirados, luego soltarse, unirse y conjugar
            occ = self.ocupacion(vivos)
            socios = self.validar_enlaces(occ)
            self._soltarse(act, socios)
            self._unirse(act, occ)
            socios = self.vecinos_enlazados(occ)
            self._conjugar(act, socios)

            # estrés: promedio móvil del hambre (energía bajo el umbral), antes de que dividirse la reparta
            h = cfg.herencia
            hambre = xp.clip((h.umbral_hambre - p["E"]) / h.umbral_hambre, 0.0, 1.0)
            p["estres"] = (1 - h.memoria_estres) * p["estres"] + h.memoria_estres * hambre

            # dividirse (suelto o unido)
            nuevos = None
            divide = (act == gen.DIVIDIRSE) | (act == gen.DIVIDIRSE_UNIDO)
            i = xp.flatnonzero(divide & (p["E"] >= f.energia_min_division))
            if i.size:
                ny = (p["y"][i, None] + self.DY[None, :]) % H
                nx = (p["x"][i, None] + self.DX[None, :]) % W
                libres = occ[ny, nx] < 0
                elegida = xp.argmax(xp.where(libres, xp.asarray(self.rng.random(libres.shape)), -1.0), axis=1)
                fila = xp.flatnonzero(libres.any(axis=1))
                celdas = ny[fila, elegida[fila]] * W + nx[fila, elegida[fila]]
                g = self._resolver(i[fila], celdas)
                padres, celdas, dirs = i[fila][g], celdas[g], elegida[fila][g]
                if padres.size:
                    p["E"][padres] = (p["E"][padres] - f.costo_division) / 2.0
                    hijos = p.genomas(padres)
                    estres = p["estres"]
                    if h.estres_modo == "barajado":  # control: rompe el vínculo con la condición propia
                        estres = estres[xp.asarray(self.rng.permutation(p.n))]
                    m = gen.tasa_efectiva(hijos["mu"], hijos["sens"], estres[padres], h)
                    gen.mutar(hijos, m, h, self.rng, self.permitidas)
                    nuevos = self._nuevos(hijos, celdas // W, celdas % W, p["E"][padres],
                                          padre=p["id"][padres], generacion=p["generacion"][padres] + 1,
                                          cepa=p["cepa"][padres], estres=xp.zeros(padres.size))
                    unido = (act[padres] == gen.DIVIDIRSE_UNIDO) & (not cfg.asociacion.inerte)
                    nuevos["dir"][unido] = p["dir"][padres[unido]]  # el clon pegado nace orientado como su progenitor
                    p["socio"][padres[unido], dirs[unido]] = nuevos["id"][unido]
                    nuevos["socio"][xp.flatnonzero(unido), self.OPUESTA[dirs[unido]]] = p["id"][padres[unido]]
                    self.cont["enlaces_creados"] += int(unido.sum())
                    self.cont["enlaces_por_division"] += int(unido.sum())
                    self.cont["nacimientos"] += padres.size
                    p["n_divisiones"][padres] += 1
                    nuevos["memoria"] = p["memoria"][padres].copy()  # memoria epigenética
                    nuevos["digestion"] = p["digestion"][padres].copy()
                    # el veneno pendiente se reparte como la energía (antes el hijo nacía limpio: una laguna)
                    p["veneno"][padres] = p["veneno"][padres] / 2.0
                    nuevos["veneno"] = p["veneno"][padres].copy()
                    nuevos["uso_comer"] = p["uso_comer"][padres].copy()  # el hijo hereda la maquinaria
                    nuevos["uso_avanzar"] = p["uso_avanzar"][padres].copy()
                    T = f.refractario_division
                    if T > 0 and f.refractario_modo == "division":
                        p["refractario"][padres] = T
                        nuevos["refractario"][:] = T
            T = f.refractario_division
            if T > 0 and f.refractario_modo == "aleatorio" and p.n:
                # control: la misma frecuencia de períodos refractarios por organismo, sin relación con dividirse
                n_div = 0 if nuevos is None else len(nuevos["id"])
                tasa = 2.0 * n_div / p.n  # progenitor e hijo
                sorteo = xp.asarray(self.rng.random(p.n)) < tasa
                p["refractario"] = xp.where(sorteo, T, p["refractario"]).astype(xp.int16)
                if nuevos is not None:
                    nuevos["refractario"][:] = 0

            # bajas y altas en una sola operación (comer, compartir y dividirse no dejan la energía en cero)
            p.actualizar(vivos & (p["E"] > 0.0), nuevos)

        if self.t % cfg.sim.registrar_cada == 0:
            self.historial.append(self.medir())
            self._reiniciar_contadores()
        self.t += 1

    def correr(self, pasos: int | None = None, al_paso=None) -> list[dict[str, float]]:
        xp = self.xp
        for _ in range(self.cfg.sim.pasos if pasos is None else pasos):
            self.paso()
            if al_paso is not None:
                al_paso(self)
        return self.historial

    # ------------------------------------------------------------------ métricas
    def grupos(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Etiqueta de grupo conexo de cada organismo y las aristas (i, j) de los enlaces válidos."""
        xp = self.xp
        p = self.pob
        socios = self.validar_enlaces(self.ocupacion())
        ii, kk = xp.nonzero(socios >= 0)
        jj = socios[ii, kk]
        lab = xp.arange(p.n)
        while ii.size:
            m = xp.minimum(lab[ii], lab[jj])
            nuevo = lab.copy()
            dev.minimo_en(nuevo, ii, m)
            dev.minimo_en(nuevo, jj, m)
            nuevo = nuevo[nuevo]  # salto de punteros: acelera la convergencia
            if xp.array_equal(nuevo, lab):
                break
            lab = nuevo
        return lab, ii, jj

    def _especializacion(self, lab, tam) -> dict[str, float]:
        """División del trabajo reproductivo en grupos de 3 o más (fase 4), con las tasas de vida de cada miembro
        (divisiones y avances por paso de edad, edad ≥ 100):
        - concentración: fracción de las divisiones del grupo que hizo el tercio más reproductivo de sus miembros
          (≈ 1/3 sin especialización, más el ruido de muestreo);
        - correlación media, dentro de los grupos, entre la tasa de avanzar y la de dividirse (negativa: unos
          empujan y otros se reproducen);
        - fracción de miembros que nunca se dividieron."""
        p = self.pob
        lab, tam = dev.a_cpu(lab), dev.a_cpu(tam)
        edad = self.t - dev.a_cpu(p["nacimiento"]).astype(float)
        nd, na = dev.a_cpu(p["n_divisiones"]).astype(float), dev.a_cpu(p["n_avances"]).astype(float)
        ok = (tam >= 3) & (edad >= 100)
        conc, corr, nunca = [], [], []
        for g in np.unique(lab[ok]):
            m = ok & (lab == g)
            if m.sum() < 3:
                continue
            d, a = nd[m] / edad[m], na[m] / edad[m]
            nunca.append(float((nd[m] == 0).mean()))
            if nd[m].sum() > 0:
                k = int(np.ceil(m.sum() / 3))
                conc.append(float(np.sort(nd[m])[::-1][:k].sum() / nd[m].sum()))
            if d.std() > 0 and a.std() > 0:
                corr.append(float(np.corrcoef(d, a)[0, 1]))
        media = lambda v: float(np.mean(v)) if v else float("nan")  # noqa: E731
        # roles (fase 5): índice (uso_comer − uso_avanzar) / (uso_comer + uso_avanzar), dispersión dentro de los
        # grupos de 3 o más (media de los desvíos por grupo) y en toda la población
        uc, ua = dev.a_cpu(p["uso_comer"]), dev.a_cpu(p["uso_avanzar"])
        rol = (uc - ua) / np.maximum(uc + ua, 1e-9)
        disp = [float(rol[(tam >= 3) & (lab == g)].std()) for g in np.unique(lab[tam >= 3])]
        extra = {"dispersion_roles_grupos": media(disp), "dispersion_roles_poblacion": float(rol.std()) if rol.size else float("nan")}
        if self.cfg.memoria.activa:
            mem = dev.a_cpu(p["memoria"])
            dm = [float(mem[(tam >= 3) & (lab == g)].std(axis=0).mean()) for g in np.unique(lab[tam >= 3])]
            extra["memoria_media"] = float(mem.mean()) if mem.size else float("nan")
            extra["dispersion_memoria_grupos"] = media(dm)
            # ¿la memoria se asocia al rol? correlación entre memoria A y el índice de rol, en grupos ≥ 3
            m = tam >= 3
            extra["corr_memoria_rol"] = (float(np.corrcoef(mem[m, 0], rol[m])[0, 1])
                                         if m.sum() > 10 and mem[m, 0].std() > 0 and rol[m].std() > 0 else float("nan"))
        return {**extra, "concentracion_reproductiva": media(conc), "corr_avanzar_dividir": media(corr),
                "frac_nunca_dividio": media(nunca), "frac_refractarios": float((dev.a_cpu(p["refractario"]) > 0).mean())}

    def medir(self) -> dict[str, float]:
        xp = self.xp
        p, c = self.pob, self.cont
        n = p.n
        fila: dict[str, float] = {"t": self.t, "poblacion": n,
                                  "nacimientos": c["nacimientos"], "muertes": c["muertes"],
                                  "recurso_total": float(self.entorno.R.sum())}
        org_pasos = max(c["org_pasos"], 1)
        fila["comido_por_org_paso"] = c["comido"] / org_pasos
        fila["compartido_por_org_paso"] = c["compartido"] / org_pasos
        fila["recibido_por_org_paso"] = c["recibido"] / org_pasos
        if self.cfg.bien_publico.activo:
            ent = self.entorno
            fila["complejo_total"] = float(ent.C.sum())
            fila["enzima_total"] = float(ent.Z.sum())
            fila["libre_total"] = float(ent.A.sum())
            fila["comido_libre_por_org_paso"] = c["comido_libre"] / org_pasos
        fila["conjugaciones"] = c["conjugaciones"]
        fila["enlaces_creados"] = c["enlaces_creados"]
        fila["enlaces_por_union"] = c["enlaces_por_union"]  # origen: unión activa con un vecino
        fila["enlaces_por_division"] = c["enlaces_por_division"]  # origen: división unida
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
            perfil = xp.stack([((p["prim"] == k) & activo).sum(1) for k in range(gen.NUM_PRIM)], axis=1)
            fila["perfiles_distintos"] = int(len(np.unique(dev.a_cpu(perfil), axis=0)))
            for k, nombre in enumerate(gen.PRIMITIVAS):
                fila[f"tiene_{nombre}"] = float((perfil[:, k] > 0).mean())
            if self.cfg.memoria.activa:  # fase 9: genes que se expresan solo según la memoria
                cond = (p["cond"] > 0) & activo
                fila["con_gen_condicionado"] = float(cond.any(axis=1).mean())
                fila["frac_genes_condicionados"] = float(cond.sum() / max(int(activo.sum()), 1))
            # organización
            lab, ii, jj = self.grupos()
            tam = xp.bincount(lab, minlength=n)[lab]
            n_enl = (p["socio"] >= 0).sum(axis=1)
            enlazado = n_enl > 0
            fila["frac_enlazados"] = float(enlazado.mean())
            fila["enlaces_medios"] = float(n_enl.mean())
            fila["tamano_grupo_medio"] = float(tam.mean())
            fila["tamano_grupo_max"] = int(tam.max())
            fila["grupos_de_3_o_mas"] = float((tam >= 3).mean())
            if self.cfg.depredacion.activa:
                fila["frac_en_refugio"] = float((tam >= self.refugio_actual()).mean())
                fila["refugio"] = self.refugio_actual()
                fila["depredados"] = c["depredados"]
                fila["depredados_en_refugio"] = c["depredados_en_refugio"]
            # coordinación (fase 3): alineación del rumbo entre enlazados, éxito del empuje y señal
            if ii.size:
                dd = p["dir"].astype(xp.int64)
                fila["alineacion_enlazados"] = float(xp.cos(((dd[jj] - dd[ii]) % 8) * (np.pi / 4)).mean())
            else:
                fila["alineacion_enlazados"] = float("nan")
            for nombre in ("grupos", "grupos3"):
                fila[f"exito_empuje_{nombre}"] = (c[f"{nombre}_mueven"] / c[f"{nombre}_empujan"]
                                                  if c[f"{nombre}_empujan"] else float("nan"))
            fila["grupos_bloqueados"] = c["grupos_bloqueados"]
            fila.update(self._especializacion(lab, tam))
            if self.cfg.estaciones.activa:
                tot = c["comida_buena"] + c["comida_mala"]
                fila["acierto_comida"] = c["comida_buena"] / tot if tot > 0 else float("nan")
                fila["estacion"] = self.estacion()
                if self.cfg.memoria.activa:  # ¿la memoria sigue a la estación? (+1: la codifica en un sentido)
                    mem = dev.a_cpu(p["memoria"])
                    al = [float(((2 * mem[:, k] - 1) * self.estacion()).mean()) for k in range(2)]
                    fila["memoria_alineada_a"], fila["memoria_alineada_b"] = al
            fila["senal_media"] = float(p["senal"].mean())
            et = p["etiqueta"]
            fila["dist_etiqueta_enlazados"] = float(xp.linalg.norm(et[ii] - et[jj], axis=1).mean()) if ii.size \
                else float("nan")
            azar = np.random.default_rng(self.t)  # generador propio: medir no altera la simulación
            a1, a2 = xp.asarray(azar.integers(0, n, (2, min(n, 500))))
            fila["dist_etiqueta_azar"] = float(xp.linalg.norm(et[a1] - et[a2], axis=1).mean())
            aprovecha = enlazado & (p["recibido"] > 2.0 * p["dado"] + 5.0)
            fila["frac_aprovechados"] = float(aprovecha.sum() / max(enlazado.sum(), 1))
            if self.cfg.bien_publico.activo:
                secretor = perfil[:, gen.SECRETAR] > 0
                fila["frac_no_secretores"] = float((~secretor).mean())
                for nombre, m in (("secretores", secretor), ("no_secretores", ~secretor)):
                    k = int(m.sum())
                    fila[f"frac_enlazados_{nombre}"] = float(enlazado[m].mean()) if k else float("nan")
                    fila[f"energia_{nombre}"] = float(p["E"][m].mean()) if k else float("nan")
                    # alimento libre comido en el intervalo, por organismo del grupo (al momento de medir)
                    clave = "comido_libre_sec" if nombre == "secretores" else "comido_libre_nosec"
                    fila[f"libre_por_{nombre}"] = c[clave] / max(k, 1) / max(self.cfg.sim.registrar_cada, 1)
        for k, nombre in enumerate(gen.PRIMITIVAS):
            fila[f"usa_{nombre}"] = float(c["acciones"][k] / org_pasos)
        return fila
