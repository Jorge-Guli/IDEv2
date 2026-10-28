"""Modo continuo (fase 12, universo vivo): un universo que corre sin plazo, guarda su estado cada tanto y retoma
después de un corte (apagado, reinicio, Ctrl+C) exactamente donde estaba.

    python -m simbio vivir experiments/configs/vivo.toml --salida runs/vivo [--guardar-cada 10000] [--pasos N]

En la carpeta de salida:
    estado.pkl        estado completo de la simulación (incluye los generadores de azar): retomar desde aquí da
                      lo mismo que no haber cortado
    entradas/         estímulos que esperan (con estimulos.activo; `python -m simbio estimular`)
    estimulos.jsonl   cada estímulo aplicado, con el paso: con ellos la corrida se puede repetir
    metricas.jsonl    una fila JSON por medición (se agrega; las columnas pueden crecer con el tiempo)
    linaje/           el linaje en bloques (id, padre, nacimiento, generación, cepa)
    poblacion.npz     genomas de la población en el último guardado
    eventos.jsonl     inicio, guardados, cortes, extinciones y resiembras
    config.toml       la configuración del universo

El estado se escribe primero en un archivo temporal y después se reemplaza: un corte en medio del guardado no
deja un estado roto.
"""

from __future__ import annotations

import dataclasses
import io
import json
import os
import pickle
import signal
import time
from pathlib import Path
from types import ModuleType

import numpy as np

from . import dispositivo as dev
from . import estimulos, persistencia
from .config import Config
from .simulacion import Simulacion


class _Guardador(pickle.Pickler):
    """Guarda el módulo de arreglos (numpy o cupy) como una referencia y los arreglos de GPU como arreglos de CPU:
    el estado se puede retomar en otro dispositivo."""

    def persistent_id(self, obj):
        if isinstance(obj, ModuleType):
            return ("modulo", obj.__name__)
        modulo = type(obj).__module__  # en tipos de Cython (p. ej. funciones de numpy.random) no es un str
        if isinstance(modulo, str) and modulo.startswith("cupy") and hasattr(obj, "get"):
            return ("arreglo", obj.get())
        return None


class _Cargador(pickle.Unpickler):
    def __init__(self, archivo, xp):
        super().__init__(archivo)
        self.xp = xp

    def persistent_load(self, pid):
        tipo, valor = pid
        if tipo == "modulo":
            if valor in ("numpy", "cupy"):
                return self.xp
            import importlib

            return importlib.import_module(valor)
        if tipo == "arreglo":
            return self.xp.asarray(valor)
        raise pickle.UnpicklingError(f"referencia desconocida: {pid!r}")


def guardar_estado(sim: Simulacion, ruta: Path) -> None:
    buf = io.BytesIO()
    pickle.dump({"version": 1, "dispositivo": sim.cfg.sim.dispositivo,
                 "celdas": sim.cfg.mundo.alto * sim.cfg.mundo.ancho,
                 "umbral": sim.cfg.sim.umbral_gpu_celdas}, buf)
    _Guardador(buf, protocol=pickle.HIGHEST_PROTOCOL).dump(sim)
    tmp = ruta.with_suffix(".tmp")
    tmp.write_bytes(buf.getvalue())
    os.replace(tmp, ruta)


def cargar_estado(ruta: Path) -> Simulacion:
    with open(ruta, "rb") as f:
        cab = pickle.load(f)
        xp, nombre = dev.elegir(cab["dispositivo"], cab["celdas"], cab["umbral"])
        sim = _Cargador(f, xp).load()
    sim.xp, sim.dispositivo = xp, nombre
    # estados guardados antes de las etapas 2 y 3: secciones de configuración nuevas (apagadas) y menos sensores
    for campo in dataclasses.fields(Config):
        if not hasattr(sim.cfg, campo.name):
            setattr(sim.cfg, campo.name, campo.default_factory())
    sim.pob.compatibilizar()
    return sim


def _anotar(ruta: Path, filas: list[dict]) -> None:
    if not filas:
        return
    with open(ruta, "a", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False, default=float) + "\n")


def _volcar(sim: Simulacion, salida: Path) -> None:
    """Pasa a disco las mediciones y el linaje acumulados en memoria (en una corrida sin plazo crecerían sin fin)."""
    _anotar(salida / "metricas.jsonl", sim.historial)
    sim.historial = []
    if sim.linaje:
        (salida / "linaje").mkdir(exist_ok=True)
        bloque = np.concatenate([np.atleast_2d(x) for x in sim.linaje])
        n = len(list((salida / "linaje").glob("linaje_*.npy")))  # numerado: dos volcados en el mismo paso no se pisan
        np.save(salida / "linaje" / f"linaje_{n:06d}_t{sim.t:012d}.npy", bloque)
        sim.linaje = []


def vivir(cfg: Config, salida: Path, guardar_cada: int = 10_000, pasos: int | None = None,
          resembrar: bool = True, verbose: bool = True) -> Simulacion:
    """Corre el universo de `salida` (lo crea si no existe) hasta `pasos` pasos totales, o sin plazo si es None.

    Si la población se extingue y `resembrar` es verdadero, el universo sigue con LUCA desde cero (nueva semilla,
    mismo reloj); queda registrado en eventos.jsonl."""
    salida.mkdir(parents=True, exist_ok=True)
    estado = salida / "estado.pkl"
    eventos = salida / "eventos.jsonl"
    if estado.exists():
        sim = cargar_estado(estado)
        _anotar(eventos, [{"evento": "retoma", "t": sim.t, "hora": time.time(), "poblacion": sim.pob.n}])
    else:
        sim = Simulacion(cfg)
        persistencia.guardar_config(cfg, salida / "config.toml")
        _anotar(eventos, [{"evento": "inicio", "t": 0, "hora": time.time(), "semilla": cfg.sim.semilla}])
    sim.resiembras = getattr(sim, "resiembras", 0)

    cortar = {"pedido": False}

    def _pedir_corte(signum, frame):  # Ctrl+C o `docker stop`: termina el paso, guarda y sale
        cortar["pedido"] = True

    anteriores = {s: signal.signal(s, _pedir_corte) for s in (signal.SIGINT, signal.SIGTERM)}
    inicio, t0 = time.time(), sim.t
    try:
        while (pasos is None or sim.t < pasos) and not cortar["pedido"]:
            if sim.luz is not None and sim.t % sim.cfg.estimulos.revisar_cada == 0:
                for fila in estimulos.recibir(sim, salida):  # estímulos desde afuera (etapa 3)
                    if verbose:
                        print(f"t={sim.t} estímulo {fila.get('dato', fila.get('error'))}", flush=True)
            sim.paso()
            if sim.pob.n == 0:
                _volcar(sim, salida)
                _anotar(eventos, [{"evento": "extincion", "t": sim.t, "hora": time.time()}])
                if not resembrar:
                    break
                sim = _resembrar(sim)
                _anotar(eventos, [{"evento": "resiembra", "t": sim.t, "hora": time.time(),
                                   "semilla": sim.cfg.sim.semilla}])
            if sim.t % guardar_cada == 0:
                _guardar(sim, salida, eventos)
                if verbose:
                    vel = (sim.t - t0) / max(time.time() - inicio, 1e-9)
                    print(f"t={sim.t} población={sim.pob.n} ({vel:.0f} pasos/s)", flush=True)
    finally:
        _guardar(sim, salida, eventos, motivo="corte" if cortar["pedido"] else "fin")
        for s, h in anteriores.items():
            signal.signal(s, h)
    return sim


def _guardar(sim: Simulacion, salida: Path, eventos: Path, motivo: str = "guardado") -> None:
    _volcar(sim, salida)
    guardar_estado(sim, salida / "estado.pkl")
    if sim.pob.n:
        persistencia.guardar_poblacion(sim, salida / "poblacion.npz")
    _anotar(eventos, [{"evento": motivo, "t": sim.t, "hora": time.time(), "poblacion": sim.pob.n}])


def _resembrar(sim: Simulacion) -> Simulacion:
    """Universo nuevo con LUCA tras una extinción: misma configuración, semilla derivada, mismo reloj."""
    import copy

    cfg = copy.deepcopy(sim.cfg)
    cfg.sim.semilla = int(np.random.SeedSequence([sim.cfg.sim.semilla, sim.t]).generate_state(1)[0])
    nuevo = Simulacion(cfg)
    nuevo.t = sim.t
    nuevo.resiembras = getattr(sim, "resiembras", 0) + 1
    return nuevo


def leer_metricas(salida: Path) -> list[dict]:
    with open(Path(salida) / "metricas.jsonl", encoding="utf-8") as f:
        return [json.loads(linea) for linea in f if linea.strip()]


def resumen(salida: Path) -> str:
    """Estado de un universo, para mirarlo sin detenerlo (lee los archivos que escribe en cada guardado)."""
    salida = Path(salida)
    eventos = [json.loads(x) for x in (salida / "eventos.jsonl").read_text(encoding="utf-8").splitlines() if x]
    filas = leer_metricas(salida) if (salida / "metricas.jsonl").exists() else []
    lineas = [f"Universo en {salida}"]
    inicio = next((e for e in eventos if e["evento"] == "inicio"), None)
    if inicio:
        lineas.append(f"  nacido: {time.strftime('%Y-%m-%d %H:%M', time.localtime(inicio['hora']))}"
                      f" (semilla {inicio.get('semilla')})")
    ultimo = eventos[-1]
    lineas.append(f"  último evento: {ultimo['evento']} en t = {ultimo['t']}"
                  f" ({time.strftime('%Y-%m-%d %H:%M', time.localtime(ultimo['hora']))})")
    for tipo in ("extincion", "resiembra", "retoma"):
        k = sum(e["evento"] == tipo for e in eventos)
        if k:
            lineas.append(f"  {tipo}: {k}")
    if filas:
        f = filas[-1]
        claves = [("poblacion", "población"), ("generacion_media", "generación media"),
                  ("acierto_comida", "acierto de comida"), ("tiene_memoria_a", "con gen de memoria"),
                  ("grupos_de_3_o_mas", "en grupos de 3 o más"), ("tasa_efectiva_media", "tasa de mutación")]
        lineas.append(f"  última medición (t = {f['t']}):")
        for k, nombre in claves:
            if k in f and f[k] == f[k]:
                lineas.append(f"    {nombre}: {f[k]:.4g}")
    return "\n".join(lineas)
