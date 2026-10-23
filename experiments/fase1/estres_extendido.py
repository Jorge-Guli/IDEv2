"""E1 extendido: ¿la mutagénesis por estrés ayuda? Pensado para el equipo local (muchas semillas, corridas largas).

Compara tres condiciones en el entorno variable, con la misma semilla (y por lo tanto el mismo mapa):
estrés propio, estrés barajado (misma distribución de tasas, sin vínculo con el hambre propio) y sin estrés.

Uso:
    python experiments/fase1/estres_extendido.py --salida runs/e1 --semillas 20 --pasos 100000 --procesos 8
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from simbio import config, corrida

RAIZ = Path(__file__).resolve().parents[2]
CONDICIONES = {
    "propio": [],
    "barajado": ['herencia.estres_modo="barajado"'],
    "sin_estres": ["herencia.estres=false"],
}


def _correr(tarea):
    salida, condicion, semilla, pasos = tarea
    registrar = max(1, min(200, pasos // 100))
    # física de la fase 1: sin asociación ni bien público (agregados después)
    ajustes = CONDICIONES[condicion] + [f"mundo.cambio_en_paso={pasos // 2}", f"sim.registrar_cada={registrar}",
                                        "asociacion.activa=false", "bien_publico.activo=false"]
    cfg = config.cargar(RAIZ / "experiments" / "configs" / "variable.toml", ajustes)
    cfg.sim.semilla, cfg.sim.pasos = semilla, pasos
    sim = corrida.correr(cfg, Path(salida) / condicion / f"semilla_{semilla}", imagenes=False)
    h = sim.historial
    t = np.array([r["t"] for r in h])
    pob = np.array([r["poblacion"] for r in h])
    ultimo = t >= 0.75 * pasos
    tras = (t >= pasos // 2) & (t < pasos // 2 + pasos // 10)
    return {"condicion": condicion, "semilla": semilla, "sobrevivio": sim.pob.n > 0,
            "poblacion_final": float(pob[ultimo].mean()), "minimo_tras_cambio": float(pob[tras].min()) if tras.any() else float("nan"),
            "sens_final": float(np.mean([r.get("sens_media", np.nan) for r, u in zip(h, ultimo) if u]))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "e1")
    ap.add_argument("--semillas", type=int, default=20)
    ap.add_argument("--pasos", type=int, default=100_000)
    ap.add_argument("--procesos", type=int, default=4)
    args = ap.parse_args()
    tareas = [(str(args.salida), c, s, args.pasos) for s in range(1, args.semillas + 1) for c in CONDICIONES]
    with Pool(args.procesos) as pool:
        res = pool.map(_correr, tareas)
    por = {(r["condicion"], r["semilla"]): r for r in res}
    informe = {"parametros": vars(args) | {"salida": str(args.salida)}, "condiciones": {}, "pareado": {}}
    for c in CONDICIONES:
        rs = [r for r in res if r["condicion"] == c]
        informe["condiciones"][c] = {
            k: {"media": float(np.mean([r[k] for r in rs])), "desvio": float(np.std([r[k] for r in rs], ddof=1))}
            for k in ("poblacion_final", "minimo_tras_cambio", "sens_final")}
        informe["condiciones"][c]["sobrevivieron"] = sum(r["sobrevivio"] for r in rs)
    for control in ("barajado", "sin_estres"):
        d = [por[("propio", s)]["poblacion_final"] / por[(control, s)]["poblacion_final"] - 1
             for s in range(1, args.semillas + 1)]
        informe["pareado"][f"propio_vs_{control}"] = {
            "diferencia_media_%": round(100 * float(np.mean(d)), 2),
            "error_estandar_%": round(100 * float(np.std(d, ddof=1) / np.sqrt(len(d))), 2),
            "semillas_a_favor": int(sum(x > 0 for x in d))}
    args.salida.mkdir(parents=True, exist_ok=True)
    (args.salida / "informe_e1.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
