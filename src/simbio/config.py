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
    # fase 4, restricción flagelar: tras dividirse, progenitor e hijo no pueden avanzar durante estos pasos (0: no)
    refractario_division: int = 0
    # "division": el período lo dispara la división; "aleatorio" (control): lo dispara un sorteo con la misma
    # frecuencia por organismo que las divisiones del paso, sin relación con dividirse
    refractario_modo: str = "division"
    # fase 5, maquinaria por uso: cada organismo lleva un promedio móvil del uso de comer y de avanzar (k); la
    # eficiencia de cada acción es min(maquinaria_max, (k / maquinaria_ref)^γ): al comer, multiplica la energía
    # obtenida por unidad de recurso; al avanzar, el peso del empuje. γ = 0: sin efecto (física anterior)
    maquinaria_gamma: float = 0.0
    maquinaria_memoria: float = 0.05  # peso del paso actual en el promedio móvil del uso
    maquinaria_ref: float = 0.35  # uso de referencia (eficiencia 1); ~ el de un generalista
    maquinaria_max: float = 2.5
    # fase 11, regla de decisión: "argmax" (el impulso mayor; descansar si ninguno es positivo) o "softmax"
    # (elección al azar con probabilidad ∝ exp(impulso / temperatura), con descansar siempre disponible con
    # impulso ≥ 0). Con softmax, un cambio chico de impulso cambia un poco la probabilidad: la selección tiene
    # gradiente aunque los genes estén saturados
    decision: str = "argmax"
    temperatura: float = 0.25


@dataclass
class HerenciaCfg:
    mutacion: bool = True
    estres: bool = True  # mutagénesis por estrés
    genes_max: int = 24
    sigma_peso: float = 0.3
    k_primitiva: float = 0.3
    k_condicion: float = 0.3  # fase 9: prob. de cambiar la condición de expresión de un gen = k_condicion · m
    modulacion: bool = False  # fase 11: la condición también puede ser "entrada modulada por la memoria A/B"
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
    # "unanime": el grupo avanza solo si todos sus miembros avanzan en la misma dirección;
    # "empuje": el grupo se desplaza en la dirección de la suma de los empujes de sus miembros
    movimiento: str = "unanime"
    # "fuerza" (fase 3c): se desplaza con probabilidad (suma de empujes unitarios en la dirección elegida) / tamaño^α
    fraccion_empuje: float = 0.5  # en "empuje": |suma de empujes| mínimo, como fracción del tamaño del grupo
    exponente_arrastre: float = 1.0  # α en "fuerza"
    inerte: bool = False  # control: las primitivas de asociación cuestan pero no tienen efecto
    division_unida: bool = True  # False: la primitiva dividirse unido no existe (solo unirse crea enlaces)
    costo_enlace: float = 0.02  # por enlace y paso, para cada extremo
    costo_unirse: float = 0.1
    costo_soltarse: float = 0.05
    costo_compartir: float = 0.05
    fraccion_compartir: float = 0.2
    eficiencia_compartir: float = 0.9
    costo_conjugar: float = 0.5
    # fase 5, puentes citoplasmáticos: cada paso, la energía se difunde por los enlaces (se conserva):
    # ΔE_i = κ · Σ_socios (E_j − E_i) / 8. κ = 0: sin difusión
    difusion_energia: float = 0.0
    # si la energía recibida por los puentes cuenta para el aprendizaje (recompensa en parte compartida con el grupo)
    difusion_aprende: bool = False


@dataclass
class BienPublicoCfg:
    activo: bool = False
    secrecion_inerte: bool = False  # control: secretar cuesta pero no produce enzima
    privado: bool = False  # control: lo que digeriría la enzima en la propia celda va directo al secretor
    capacidad_complejo_max: float = 20.0
    regeneracion_complejo: float = 0.01
    escala_parche_complejo: float = 8.0
    contraste_complejo: float = 1.0
    # calibrado con experiments/fase2b/calibrar.py: un secretor solo no recupera su costo (0,81),
    # un bloque de secretores sí (1,39); lo producido en total es ~2 veces el costo
    costo_secretar: float = 0.3
    enzima_por_secrecion: float = 1.0
    degradacion_enzima: float = 0.3
    difusion_enzima: float = 0.1
    tasa_digestion: float = 0.05  # k en C·(1 − exp(−k·Z))
    rendimiento: float = 1.0
    degradacion_libre: float = 0.02
    difusion_libre: float = 0.8


@dataclass
class DepredacionCfg:
    activa: bool = False
    # "tamano": refugio por tamaño de grupo; "uniforme": todo ataque es mortal (control);
    # "aleatorio": un ataque perdona con prob_perdon, sin relación con los enlaces (control de protección igualada)
    modo: str = "tamano"
    prob_ataque: float = 0.002  # por organismo y paso
    prob_perdon: float = 0.9  # solo en modo "aleatorio"
    inicio: int = 0  # paso desde el que actúa el depredador (aclimatación previa)
    rampa: int = 0  # pasos en los que la probabilidad de ataque sube linealmente desde 0 (0: de golpe)
    refugio: int = 4  # grupos de este tamaño o mayores no pueden ser comidos
    gradual: bool = True  # bajo el refugio, un ataque mata con prob. 1 − (tamaño − 1)/(refugio − 1)
    # escalada (fase 3): el refugio sube linealmente de `refugio` a `refugio_final` entre `escalada_inicio`
    # y `escalada_inicio + escalada_pasos` (un depredador que traga presas cada vez más grandes); 0: sin escalada
    refugio_final: float = 0.0
    escalada_inicio: int = 0
    escalada_pasos: int = 0


@dataclass
class CoordinacionCfg:
    # fase 3: percepción local para coordinar al grupo; desactivada, los sensores nuevos valen 0
    rumbo: bool = False  # sensores del rumbo de los enlazados (seno y coseno del ángulo medio) y de su empuje
    senales: bool = False  # primitiva senalar (no ocupa la acción del paso) y sensores de señal propia y de socios
    barajar: bool = False  # control: los sensores nuevos reciben los valores de otro organismo al azar
    costo_senal: float = 0.05  # por unidad de señal emitida y paso


@dataclass
class MemoriaCfg:
    # paso C: memoria interna persistente (2 variables en [0, 1]) que el genoma escribe con las primitivas
    # memoria_a y memoria_b (no ocupan la acción) y lee con dos sensores; el hijo la hereda
    activa: bool = False
    tasa: float = 0.1  # m ← clip(m + tasa · impulso, 0, 1)
    inicial: float = 0.0
    # fase 10, memoria tipo cerrojo: solo cambia ante impulsos de magnitud mayor que `umbral` (zona muerta);
    # 0 = sin umbral. Un gen de memoria con un sesgo chico deja de borrar lo recordado
    umbral: float = 0.0


@dataclass
class EstacionesCfg:
    # fase 7, memoria de contexto: dos tipos de comida (parches A y B); una estación oculta, que se alterna cada
    # `periodo` pasos, decide cuál nutre y cuál es tóxica (energía = −castigo × lo comido); una pista de la
    # estación se percibe en cada paso con probabilidad `p_pista`
    activa: bool = False
    periodo: int = 2000
    castigo: float = 1.0
    p_pista: float = 0.01
    escala_parche: float = 10.0
    # "inmediato": la comida tóxica resta castigo × lo comido al instante (detectable con el sensor de ΔE);
    # "diferido": da energía como la buena, pero deja un veneno de (1 + castigo) × lo comido que se descuenta
    # a razón de `tasa_veneno` por paso (mismo saldo neto, sin aviso inmediato)
    toxicidad: str = "inmediato"
    pista_informativa: bool = True  # False (control): la pista es +1 o −1 al azar, sin relación con la estación
    tasa_veneno: float = 0.05
    # fase 9: la toxicidad crece linealmente de 0 (la comida fuera de estación nutre como la buena) a su valor
    # pleno en `rampa_toxicidad` pasos; 0 = plena desde el inicio. Evita el colapso inicial de LUCA, que come de
    # todo y acumula veneno diferido
    rampa_toxicidad: int = 0
    # fase 10, currículo de la pista: la probabilidad baja linealmente de `p_pista_inicial` a `p_pista` en
    # `rampa_pista` pasos (0 = sin rampa)
    p_pista_inicial: float = 0.0
    rampa_pista: int = 0
    # fase 10, digestión inducible: lo absorbido de la comida de tipo t se multiplica por 1 + induccion·(2d − 1)·t,
    # con d el estado digestivo
    # (nutrientes y veneno). Una memoria que sigue a la estación rinde más en ambos tipos: el primer peldaño
    # tiene premio propio. 0 = apagada
    induccion: float = 0.0
    # el estado digestivo sigue a la memoria A con esta inercia (pasos): d ← d + (m_A − d) / inercia. Bloquea el
    # atajo de escribir la memoria con el tipo de comida de la celda (en el piloto sin inercia, eso ganaba)
    inercia_digestion: int = 100


@dataclass
class RealidadCfg:
    # fase 12, etapa 2: el clima real de una ciudad (serie horaria, ver experiments/herramientas/descargar_clima.py)
    # regula el mundo. La simulación solo lee el archivo; nunca toca la red
    activa: bool = False
    archivo: str = "datos/clima/capitan_bermudez.npz"
    pasos_por_hora: int = 20  # un año real son 175 200 pasos
    hora_inicial: int = 0  # hora de la serie en el paso 0 (al terminar la serie, vuelve a empezar)
    # control: los días (bloques de 24 horas) se recorren en un orden al azar; mismas cantidades, sin las
    # secuencias de varios días (frentes, rachas de lluvia)
    barajar_dias: bool = False
    # radiación → recrecimiento: regeneracion · (1 − a + a · radiación / radiación media); a = 0: sin efecto.
    # Con a = 1 no crece nada de noche y LUCA se extingue (auge de día, hambre de noche): ver clima.toml
    acople_radiacion: float = 0.5
    # temperatura → costo basal: costo_basal · (1 + k · ((T − T_óptima) / 10)²); k = 0: sin efecto
    acople_temperatura: float = 0.25
    temperatura_optima: float = 20.0
    # lluvia → qué comida nutre (reemplaza a la estación artificial; requiere estaciones.activa): húmedo (tipo B)
    # cuando la lluvia acumulada reciente (promedio móvil exponencial de `ventana_lluvia` horas) está en la
    # fracción `fraccion_humeda` más alta de la serie; seco (tipo A) si no
    lluvia: bool = True
    ventana_lluvia: float = 48.0
    fraccion_humeda: float = 0.3
    # presión → sensor local "presion": su tendencia en las últimas `ventana_presion` horas, en desvíos típicos,
    # recortada a [−1, 1]. Antes de una lluvia la presión suele bajar: premia anticipar. Con 24 horas se cancela
    # la marea diaria de la presión; en Capitán Bermúdez, con la tendencia bajo −0,5, la probabilidad de que
    # empiece una racha húmeda en las 12 horas siguientes es 0,12 (0,06 en general; 0,02 con la tendencia sobre 0,5)
    sensor_presion: bool = True
    ventana_presion: int = 24
    # control: el sensor lee la presión de otro momento de la serie (corrida circular de medio registro): misma
    # distribución y misma dinámica, sin relación con la lluvia vigente
    presion_desacoplada: bool = False


@dataclass
class AtaqueCfg:
    # fase 12, etapa 4: depredación evolucionada. La primitiva atacar quita energía al organismo de enfrente y le
    # pasa una parte al atacante: el ambiente pasan a ser otros organismos que también evolucionan (Reina Roja)
    activo: bool = False
    costo_atacar: float = 0.3
    fuerza: float = 10.0  # energía que quita un ataque (antes de la protección)
    eficiencia: float = 0.6  # fracción de lo quitado que gana el atacante (pérdida trófica)
    # protección por enlaces: el daño se divide por (1 + enlaces del atacado); asociarse defiende
    proteccion_enlaces: bool = True


@dataclass
class EstimulosCfg:
    # fase 12, etapa 3: estímulos desde afuera (un humano, Claude, una interfaz). Entran como eventos de luz: un
    # campo que se percibe con el sensor local "luz" y hace crecer comida donde cae. Un texto se vuelve una
    # secuencia de pulsos (cada letra, un lugar y un tamaño). En el modo continuo llegan como archivos JSON en
    # <universo>/entradas/ y quedan grabados en estimulos.jsonl con el paso en que se aplicaron
    activo: bool = False
    # luz → recrecimiento extra: R += acople_luz · luz · (K − R); 0 (control): la luz se ve pero no alimenta
    acople_luz: float = 0.05
    decaimiento_luz: float = 0.02  # fracción de la luz que se apaga por paso
    pasos_por_letra: int = 40  # separación entre los pulsos de un texto
    revisar_cada: int = 100  # cada cuántos pasos el modo continuo mira la carpeta de entradas


@dataclass
class SimCfg:
    semilla: int = 0
    pasos: int = 5000
    poblacion_inicial: int = 200
    registrar_cada: int = 50
    imagen_cada: int = 0  # 0: solo imagen final
    dispositivo: str = "auto"  # "auto" (GPU si hay y el mundo es grande), "cpu" o "gpu"
    umbral_gpu_celdas: int = 90_000  # en "auto", mundos más chicos corren en CPU (más rápida ahí)


@dataclass
class Config:
    mundo: MundoCfg = field(default_factory=MundoCfg)
    fisica: FisicaCfg = field(default_factory=FisicaCfg)
    herencia: HerenciaCfg = field(default_factory=HerenciaCfg)
    aprendizaje: AprendizajeCfg = field(default_factory=AprendizajeCfg)
    asociacion: AsociacionCfg = field(default_factory=AsociacionCfg)
    bien_publico: BienPublicoCfg = field(default_factory=BienPublicoCfg)
    depredacion: DepredacionCfg = field(default_factory=DepredacionCfg)
    coordinacion: CoordinacionCfg = field(default_factory=CoordinacionCfg)
    memoria: MemoriaCfg = field(default_factory=MemoriaCfg)
    estaciones: EstacionesCfg = field(default_factory=EstacionesCfg)
    realidad: RealidadCfg = field(default_factory=RealidadCfg)
    estimulos: EstimulosCfg = field(default_factory=EstimulosCfg)
    ataque: AtaqueCfg = field(default_factory=AtaqueCfg)
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
