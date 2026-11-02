"""Lector del equipo: el mundo físico de LUCA es la computadora donde corre (autor, 2026-11-01).

Corre afuera del contenedor, con prioridad mínima, y cada `--cada` segundos escribe en datos/equipo/:
    actual.json            la última muestra (el universo continuo la lee; ver EquipoCfg y continuo.leer_equipo)
    registro_AAAA-MM.jsonl todas las muestras, para estudiar los ritmos del equipo
Qué mide:
    cpu_libre      fracción de CPU sin usar en el intervalo (la única que hoy alimenta al universo)
    memoria_libre  fracción de memoria disponible
    chat_bytes     cuántos bytes crecieron los registros de las sesiones de Claude Code del equipo
    chat_archivos  cuántos registros de sesión cambiaron
De las sesiones se toma solo el ritmo (cuánto y cuándo), nunca el contenido: no se abre ningún archivo, solo se mira
su tamaño. Nada sale del equipo.

Uso: pythonw experiments/herramientas/lector_equipo.py   (sin ventana; lo arranca solo el inicio de Windows)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import psutil

RAIZ = Path(__file__).resolve().parents[2]


def _bajar_prioridad() -> None:
    p = psutil.Process()
    p.nice(psutil.IDLE_PRIORITY_CLASS if sys.platform == "win32" else 19)


def _tamanos(sesiones: Path) -> dict[str, int]:
    tam = {}
    for f in sesiones.glob("*/*.jsonl"):
        try:
            tam[str(f)] = f.stat().st_size
        except OSError:
            pass
    return tam


def muestra(previos: dict[str, int], sesiones: Path) -> tuple[dict, dict[str, int]]:
    tam = _tamanos(sesiones)
    crec = [tam[k] - previos.get(k, tam[k]) for k in tam]
    m = {"hora": time.time(),
         "cpu_libre": round(1.0 - psutil.cpu_percent(interval=None) / 100.0, 4),
         "memoria_libre": round(psutil.virtual_memory().available / psutil.virtual_memory().total, 4),
         "chat_bytes": int(sum(c for c in crec if c > 0)),
         "chat_archivos": int(sum(c > 0 for c in crec))}
    return m, tam


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cada", type=float, default=10.0)
    ap.add_argument("--salida", default=str(RAIZ / "datos/equipo"))
    ap.add_argument("--sesiones", default=str(Path.home() / ".claude/projects"))
    ap.add_argument("--veces", type=int, default=0, help="0: sin fin")
    args = ap.parse_args()
    _bajar_prioridad()
    salida, sesiones = Path(args.salida), Path(args.sesiones)
    salida.mkdir(parents=True, exist_ok=True)
    psutil.cpu_percent(interval=None)  # la primera lectura no tiene intervalo
    previos = _tamanos(sesiones)
    n = 0
    while args.veces == 0 or n < args.veces:
        time.sleep(args.cada)
        m, previos = muestra(previos, sesiones)
        linea = json.dumps(m)
        tmp = salida / "actual.json.tmp"
        tmp.write_text(linea, encoding="utf-8")
        os.replace(tmp, salida / "actual.json")  # el universo nunca lee una muestra a medio escribir
        with open(salida / f"registro_{time.strftime('%Y-%m')}.jsonl", "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        n += 1


if __name__ == "__main__":
    main()
