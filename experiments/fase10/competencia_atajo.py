"""Fase 10: competencia contra un control con el mismo gen en cero. El mutante lleva un gen de memoria escrito con
la pista ("pista", memoria real) o con el tipo de comida de la celda ("tipo", el atajo).

Mundo mosaico, castigo 0,2, rampa de toxicidad de 5000 pasos, cerrojo, sin mutación, 30 000 pasos, semillas 1–8.
Ejecutar desde la raíz del repo:
    python experiments/fase10/competencia_atajo.py pista estaciones.induccion=0.25 [estaciones.inercia_digestion=100]
    python experiments/fase10/competencia_atajo.py tipo estaciones.induccion=0.25 [estaciones.inercia_digestion=500]
Resultados (fracción final del mutante por semilla; x = extinción), en
docs/bitacora/2026-10-26-fase10-prerregistro.md.
"""
import sys
sys.path.insert(0, "experiments/fase7")
from multiprocessing import Pool
import invadir_memoria as inv, luca_memoria as lm
from simbio import genoma as gen
modo = sys.argv[1]
if modo == "tipo":  # el atajo: memoria escrita con el tipo de comida de la celda
    inv.GENES_REGULADOS = [(gen.MEMORIA_A, 0.0, {gen.S_TIPO_AQUI: 2.5}, 0)]
extra = ("estaciones.escala_parche=1.0", "estaciones.rampa_toxicidad=5000", "memoria.umbral=0.5") + tuple(sys.argv[2:])
with Pool(4) as p:
    rs = p.map(lm._correr, [(s, 30000, 0.2, extra, True, (0,)) for s in range(1, 9)])
print(modo, sys.argv[2:], " ".join("x" if r["frac_memoria"] is None else f"{r['frac_memoria']:.2f}" for r in rs))
