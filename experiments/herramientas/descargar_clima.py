"""Descarga una serie horaria de clima real desde la API de archivo de Open-Meteo (libre, sin clave) y la guarda
en datos/clima/<nombre>.npz con sus metadatos.

Corre en un proceso aparte de la simulación: los organismos nunca tocan la red. La simulación solo lee el .npz.

Uso:
    python experiments/herramientas/descargar_clima.py                      # Capitán Bermúdez, 2000-2025
    python experiments/herramientas/descargar_clima.py --nombre rosario --lat -32.95 --lon -60.64 --desde 2010-01-01

Variables (una por hora, hora local de la ciudad):
    temperatura (°C), precipitacion (mm), presion (hPa, en superficie), radiacion (W/m², onda corta) y
    nubosidad (%).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
URL = "https://archive-api.open-meteo.com/v1/archive"
# nombre en el archivo -> variable de Open-Meteo
VARIABLES = {
    "temperatura": "temperature_2m",
    "precipitacion": "precipitation",
    "presion": "surface_pressure",
    "radiacion": "shortwave_radiation",
    "nubosidad": "cloud_cover",
}


def descargar_tramo(lat: float, lon: float, desde: str, hasta: str, zona: str) -> dict:
    params = {"latitude": lat, "longitude": lon, "start_date": desde, "end_date": hasta,
              "hourly": ",".join(VARIABLES.values()), "timezone": zona}
    with urllib.request.urlopen(URL + "?" + urllib.parse.urlencode(params), timeout=120) as r:
        return json.loads(r.read().decode())


def rellenar(x: np.ndarray) -> tuple[np.ndarray, int]:
    """Reemplaza los huecos (NaN) por interpolación lineal; devuelve la serie y cuántos había."""
    faltan = np.isnan(x)
    n = int(faltan.sum())
    if n and n < len(x):
        i = np.arange(len(x))
        x = x.copy()
        x[faltan] = np.interp(i[faltan], i[~faltan], x[~faltan])
    return x, n


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nombre", default="capitan_bermudez")
    p.add_argument("--lugar", default="Capitán Bermúdez, Santa Fe, Argentina")
    p.add_argument("--lat", type=float, default=-32.826)
    p.add_argument("--lon", type=float, default=-60.720)
    p.add_argument("--desde", default="2000-01-01")
    p.add_argument("--hasta", default="2025-12-31")
    p.add_argument("--zona", default="America/Argentina/Buenos_Aires")
    a = p.parse_args()

    # de a un año por pedido, para no exceder los límites de la API
    series = {k: [] for k in VARIABLES}
    horas: list[str] = []
    ini, fin = dt.date.fromisoformat(a.desde), dt.date.fromisoformat(a.hasta)
    anio = ini.year
    while anio <= fin.year:
        d = max(ini, dt.date(anio, 1, 1))
        h = min(fin, dt.date(anio, 12, 31))
        print(f"descargando {d} .. {h}", flush=True)
        datos = descargar_tramo(a.lat, a.lon, d.isoformat(), h.isoformat(), a.zona)["hourly"]
        horas += datos["time"]
        for k, v in VARIABLES.items():
            series[k] += [np.nan if x is None else x for x in datos[v]]
        anio += 1

    salida = RAIZ / "datos" / "clima" / f"{a.nombre}.npz"
    salida.parent.mkdir(parents=True, exist_ok=True)
    arrays, huecos = {}, {}
    for k in VARIABLES:
        arrays[k], huecos[k] = rellenar(np.asarray(series[k], dtype=np.float32))
    meta = {"lugar": a.lugar, "latitud": a.lat, "longitud": a.lon, "zona_horaria": a.zona,
            "desde": horas[0], "hasta": horas[-1], "horas": len(horas), "fuente": URL,
            "variables": VARIABLES, "huecos_interpolados": huecos,
            "descargado": dt.datetime.now().isoformat(timespec="seconds")}
    np.savez_compressed(salida, **arrays, hora=np.asarray(horas), meta=json.dumps(meta, ensure_ascii=False))
    meta["sha256"] = hashlib.sha256(salida.read_bytes()).hexdigest()
    salida.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"guardado {salida} ({len(horas)} horas)")
    for k in VARIABLES:
        x = arrays[k]
        print(f"  {k:14s} min {x.min():8.2f}  media {x.mean():8.2f}  max {x.max():8.2f}  huecos {huecos[k]}")


if __name__ == "__main__":
    main()
