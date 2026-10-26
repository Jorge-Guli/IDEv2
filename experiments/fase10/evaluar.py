"""Fase 10: peldaños para la memoria (memoria tipo cerrojo y rampa de la pista).

Mismo mundo que la fase 9 (mosaico, toxicidad diferida con rampa de 30 000 pasos, sin aprendizaje, regulación
condicionada posible). Dos cambios en la física, solos y combinados:
    cerrojo     la memoria solo cambia ante impulsos de magnitud > 0,5 (un sesgo chico no la borra)
    rampa       la pista empieza frecuente (p = 0,2) y baja a 0,01 en 150 000 pasos: al principio, una memoria
                mala sirve porque se renueva; después hace falta una que dure
    induccion   digestión inducible (0,25): lo absorbido de cada tipo de comida depende de la memoria A; una
                memoria que sigue a la estación rinde más. Verificado: el gen de memoria solo, contra un control con
                el mismo gen en cero, gana en 7/7 semillas con sobrevivientes (sin inducción: 2/5)
Condiciones (desde LUCA sembrado con un gen de memoria A conectado a la pista, como `sem_info` de la fase 9):
    sem_cerrojo_rampa   cerrojo + rampa
    sem_cerrojo         solo cerrojo
    sem_rampa           solo rampa
    ruido_cerrojo_rampa cerrojo + rampa con la pista aleatoria (control: la memoria no informa)
    luca_cerrojo_rampa  cerrojo + rampa desde LUCA puro
    sem_induccion       cerrojo + inducción
    ruido_induccion     cerrojo + inducción con la pista aleatoria (control)
    luca_induccion      cerrojo + inducción desde LUCA puro

Uso:
    python experiments/fase10/evaluar.py --salida runs/fase10 [--procesos 8] [--pasos 300000] [--semillas 8]
        [--semilla-inicial 181] [--condiciones ...] (por defecto, las cuatro del prerregistro)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("evaluar_fase9", RAIZ / "experiments" / "fase9" / "evaluar.py")
fase9 = importlib.util.module_from_spec(_spec)
sys.modules["evaluar_fase9"] = fase9
_spec.loader.exec_module(fase9)

CERROJO = ["memoria.umbral=0.5"]
RAMPA = ["estaciones.p_pista_inicial=0.2", "estaciones.rampa_pista=150000"]
RUIDO = ["estaciones.pista_informativa=false"]
INDUCCION = ["estaciones.induccion=0.25"]
CONDICIONES = {
    # digestión inducible: la memoria tiene utilidad directa (primer peldaño con premio propio)
    "sem_induccion": CERROJO + INDUCCION,
    "ruido_induccion": CERROJO + INDUCCION + RUIDO,
    "luca_induccion": CERROJO + INDUCCION,
    "sem_cerrojo_rampa": CERROJO + RAMPA,
    "sem_cerrojo": CERROJO,
    "sem_rampa": RAMPA,
    "ruido_cerrojo_rampa": CERROJO + RAMPA + RUIDO,
    "luca_cerrojo_rampa": CERROJO + RAMPA,
}


# las de la corrida prerregistrada; las de cerrojo + rampa quedan disponibles (piloto negativo)
PRINCIPALES = ["sem_induccion", "ruido_induccion", "luca_induccion", "sem_cerrojo"]


def _correr(tarea):
    salida, nombre, semilla, pasos = tarea
    return fase9.correr_condicion(salida, nombre, semilla, pasos, fase9.BASE + CONDICIONES[nombre],
                                  not nombre.startswith("luca"))


def hipotesis(rs):
    """Reglas prerregistradas (docs/bitacora/2026-10-26-fase10-prerregistro.md)."""
    def val(n, m):
        return {r["semilla"]: r[m] for r in rs if r["nombre"] == n and not r["extinta"] and r[m] == r[m]}

    def prueba(a, b, m):
        va, vb = val(a, m), val(b, m)
        comunes = sorted(set(va) & set(vb))
        d = [va[s] - vb[s] for s in comunes]
        p = fase9.fase7.fase4.permutacion_pareada(d)
        return {"n": len(d), "diferencias": [round(x, 3) for x in d], "p_una_cola": round(p, 4),
                "cumple": bool(d) and p < 0.05}

    def umbral(n, m, u):
        v = val(n, m)
        return {"valores": {s: round(x, 3) for s, x in v.items()}, "cumple": sum(x > u for x in v.values()) >= 4}
    return {
        "P1_seguimiento_induccion_mayor_a_030": umbral("sem_induccion", "seguimiento_final", 0.3),
        "P2_seguimiento_vs_ruido": prueba("sem_induccion", "ruido_induccion", "seguimiento_final"),
        "P3_acierto_vs_ruido": prueba("sem_induccion", "ruido_induccion", "acierto_final"),
        "P4_acierto_induccion_mayor_a_060": umbral("sem_induccion", "acierto_final", 0.6),
        "P5_seguimiento_vs_sin_induccion": prueba("sem_induccion", "sem_cerrojo", "seguimiento_final"),
        "P6_luca_seguimiento_mayor_a_030": umbral("luca_induccion", "seguimiento_final", 0.3),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=RAIZ / "runs" / "fase10")
    ap.add_argument("--procesos", type=int, default=4)
    ap.add_argument("--pasos", type=int, default=300000)
    ap.add_argument("--semillas", type=int, default=8)
    ap.add_argument("--semilla-inicial", type=int, default=181)
    ap.add_argument("--condiciones", nargs="*", default=PRINCIPALES)
    args = ap.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    semillas = list(range(args.semilla_inicial, args.semilla_inicial + args.semillas))
    t0 = time.time()
    with Pool(args.procesos) as pool:
        rs = pool.map(_correr, [(str(args.salida), n, s, args.pasos) for n in args.condiciones for s in semillas])
    informe = {"parametros": {"pasos": args.pasos, "semillas": semillas, "minutos": round((time.time() - t0) / 60, 1)},
               "hipotesis": hipotesis(rs), "corridas": rs}
    (args.salida / "informe.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(informe["hipotesis"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
