"""Configuración de una corrida: dataclasses con valores por defecto y carga desde TOML."""

from __future__ import annotations

import ast
import dataclasses
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MundoCfg:
    alto: int = 128
    ancho: int = 128
    capacidad_max: float = 10.0  # recurso máximo por celda
    regeneracion: float = 0.02  # fracción de (K - R) que se recupera por paso
    escala_parche: float = 6.0  # sigma del suavizado gaussiano, en celdas
    contraste: float = 2.0  # exponente aplicado al campo normalizado
    recurso_inicial: float = 1.0  # fracción de K presente al inicio
    amplitud_estacional: float = 0.0  # A en K·(1 + A·sin(2πt/P))
    periodo_estacional: int = 2000
    cambio_en_paso: int = -1  # regenerar el mapa de parches en este paso (-1: nunca)


@dataclass
class FisicaCfg:
    energia_max: float = 100.0
    energia_inicial: float = 50.0
    costo_basal: float = 0.3
    costo_por_gen: float = 0.01
    costo_avanzar: float = 0.4
    costo_girar: float = 0.05
    costo_voltereta: float = 0.1
    costo_comer: float = 0.05
    toma_max: float = 4.0
    costo_division: float = 2.0
    energia_min_division: float = 20.0


@dataclass
class HerenciaCfg:
    mutacion: bool = True
    estres: bool = True  # mutagénesis por estrés
    genes_max: int = 24
    sigma_peso: float = 0.3
    k_primitiva: float = 0.3
    k_duplicacion: float = 0.5
    k_eliminacion: float = 0.5
    k_gen_nuevo: float = 0.2
    k_rasgo: float = 10.0  # prob. de mutar cada rasgo = min(1, k_rasgo·m)
    sigma_log_rasgo: float = 0.2
    sigma_etiqueta: float = 0.05
    tasa_max: float = 0.2  # tope de la tasa de mutación efectiva
    memoria_estres: float = 0.05  # peso del paso actual en el promedio móvil del estrés
    umbral_hambre: float = 25.0  # energía por debajo de la cual el organismo acumula estrés
    estres_modo: str = "propio"  # "propio" o "barajado" (control: estrés de otro organismo al azar)
    # rasgos de LUCA
    mu_inicial: float = 0.02
    sensibilidad_inicial: float = 2.0
    eta_inicial: float = 0.05
    # límites de los rasgos
    mu_min: float = 1e-4
    mu_max: float = 0.3
    sensibilidad_max: float = 20.0
    eta_max: float = 1.0


@dataclass
class AprendizajeCfg:
    activo: bool = True
    escala_recompensa: float = 5.0
    memoria_linea_base: float = 0.1
    decaimiento: float = 0.01
    limite: float = 2.0


@dataclass
class AsociacionCfg:
    activa: bool = True
    conjugacion: bool = True
    adhesion: bool = True  # el grupo enlazado se mueve junto o no se mueve
    inerte: bool = False  # control: las primitivas de asociación cuestan pero no tienen efecto
    costo_enlace: float = 0.02  # por enlace y paso, para cada extremo
    costo_unirse: float = 0.1
    costo_soltarse: float = 0.05
    costo_compartir: float = 0.05
    fraccion_compartir: float = 0.2
    eficiencia_compartir: float = 0.9
    costo_conjugar: float = 0.5


@dataclass
class SimCfg:
    semilla: int = 0
    pasos: int = 5000
    poblacion_inicial: int = 200
    registrar_cada: int = 50
    imagen_cada: int = 0  # 0: solo imagen final
    dispositivo: str = "auto"  # "auto" (GPU si hay), "cpu" o "gpu"


@dataclass
class Config:
    mundo: MundoCfg = field(default_factory=MundoCfg)
    fisica: FisicaCfg = field(default_factory=FisicaCfg)
    herencia: HerenciaCfg = field(default_factory=HerenciaCfg)
    aprendizaje: AprendizajeCfg = field(default_factory=AprendizajeCfg)
    asociacion: AsociacionCfg = field(default_factory=AsociacionCfg)
    sim: SimCfg = field(default_factory=SimCfg)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_toml(self) -> str:
        lineas = []
        for seccion, valores in self.to_dict().items():
            lineas.append(f"[{seccion}]")
            for k, v in valores.items():
                if isinstance(v, bool):
                    v = "true" if v else "false"
                elif isinstance(v, str):
                    v = f'"{v}"'
                lineas.append(f"{k} = {v}")
            lineas.append("")
        return "\n".join(lineas)


def _aplicar(cfg: Config, seccion: str, clave: str, valor: Any) -> None:
    sub = getattr(cfg, seccion, None)
    if sub is None or not hasattr(sub, clave):
        raise KeyError(f"parámetro desconocido: {seccion}.{clave}")
    tipo = type(getattr(sub, clave))
    if tipo is bool and isinstance(valor, str):
        valor = valor.lower() in ("1", "true", "si", "sí", "yes")
    setattr(sub, clave, tipo(valor))


def desde_dict(datos: dict[str, dict[str, Any]], base: Config | None = None) -> Config:
    cfg = base if base is not None else Config()
    for seccion, valores in datos.items():
        for clave, valor in valores.items():
            _aplicar(cfg, seccion, clave, valor)
    return cfg


def cargar(ruta: str | Path | None = None, ajustes: list[str] | None = None) -> Config:
    """Carga una configuración TOML (opcional) y aplica ajustes "seccion.clave=valor"."""
    cfg = Config()
    if ruta is not None:
        with open(ruta, "rb") as f:
            desde_dict(tomllib.load(f), cfg)
    for ajuste in ajustes or []:
        ruta_clave, valor = ajuste.split("=", 1)
        seccion, clave = ruta_clave.strip().split(".", 1)
        try:
            valor = ast.literal_eval(valor.strip())
        except (ValueError, SyntaxError):
            valor = valor.strip()
        _aplicar(cfg, seccion, clave, valor)
    return cfg
