"""La versión vectorizada del empuje colectivo da exactamente lo mismo que la original (bucle por grupo)."""
import numpy as np

from simbio import dispositivo as dev
from simbio import genoma as gen
from simbio.simulacion import DX, DY, Simulacion, componentes


def _referencia(self, act, occ, socios):
    xp, p, cfg = self.xp, self.pob, self.cfg.asociacion
    H, W = self.entorno.alto, self.entorno.ancho
    soc = dev.a_cpu(socios)
    enlazado = (soc >= 0).any(axis=1)
    lab = componentes(soc)
    y, x = dev.a_cpu(p["y"]).copy(), dev.a_cpu(p["x"]).copy()
    d, a = dev.a_cpu(p["dir"]).astype(np.int64), dev.a_cpu(act)
    ocup = dev.a_cpu(occ).copy()
    miembros_de = {}
    for idx in np.flatnonzero(enlazado):
        miembros_de.setdefault(lab[idx], []).append(idx)
    grupos = list(miembros_de.values())
    norma = np.hypot(DX, DY)
    for g in self.rng.permutation(len(grupos)):
        m = np.array(grupos[g])
        empujan = m[a[m] == gen.AVANZAR]
        if empujan.size == 0:
            continue
        grande = m.size >= 3
        self.cont["grupos_empujan"] += 1
        self.cont["grupos3_empujan"] += int(grande)
        vx, vy = DX[d[empujan]].sum(), DY[d[empujan]].sum()
        if np.hypot(vx, vy) < cfg.fraccion_empuje * m.size:
            continue
        k = int(np.argmax((DX * vx + DY * vy) / norma))
        ny, nx = (y[m] + DY[k]) % H, (x[m] + DX[k]) % W
        destino = ocup[ny, nx]
        if not np.all((destino < 0) | (lab[np.maximum(destino, 0)] == lab[m[0]])):
            self.cont["grupos_bloqueados"] += 1
            continue
        self.cont["grupos_mueven"] += 1
        self.cont["grupos3_mueven"] += int(grande)
        ocup[y[m], x[m]] = -1
        ocup[ny, nx] = m
        y[m], x[m] = ny, nx
    p["y"], p["x"] = xp.asarray(y.astype(np.int32)), xp.asarray(x.astype(np.int32))
    return xp.asarray(enlazado)


def _correr(cfg, metodo, monkeypatch):
    with monkeypatch.context() as m:
        if metodo is not None:
            m.setattr(Simulacion, "_mover_grupos", metodo)
        sim = Simulacion(cfg)
        p = sim.pob
        for k, prim in enumerate([gen.DIVIDIRSE_UNIDO, gen.UNIRSE, gen.AVANZAR, gen.SOLTARSE]):
            p["activo"][:, 4 + k] = True
            p["prim"][:, 4 + k] = prim
            p["w"][:, 4 + k, gen.S_RUIDO] = 2.0
        h = sim.correr(400)
    return h, {k: dev.a_cpu(v).copy() for k, v in sim.pob.d.items()}


def test_vectorizado_igual_a_referencia(cfg, monkeypatch):
    cfg.asociacion.movimiento = "empuje"
    cfg.sim.poblacion_inicial = 500  # mundo de 32×32 casi lleno: muchos conflictos entre grupos
    cfg.sim.registrar_cada = 20
    for fraccion in (0.5, 0.1):
        cfg.asociacion.fraccion_empuje = fraccion
        h1, d1 = _correr(cfg, None, monkeypatch)
        h2, d2 = _correr(cfg, _referencia, monkeypatch)
        assert repr(h1) == repr(h2)
        assert d1.keys() == d2.keys() and all(np.array_equal(d1[k], d2[k]) for k in d1)
        assert sum(r.get("grupos_bloqueados", 0) for r in h1) > 0
