"""Imágenes del mundo y gráficos de métricas."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import genoma as gen  # noqa: E402
from .dispositivo import a_cpu  # noqa: E402


def imagen_mundo(sim, ruta: Path, titulo: str = "") -> None:
    campos = ("x", "y", "socio", "cepa", "activo")
    p = {k: a_cpu(sim.pob[k]) for k in campos}
    n = sim.pob.n
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.imshow(a_cpu(sim.entorno.R), cmap="Greens", vmin=0, vmax=sim.cfg.mundo.capacidad_max,
              interpolation="nearest")
    if n and (p["socio"] >= 0).any():
        from matplotlib.collections import LineCollection

        socios = a_cpu(sim.validar_enlaces(sim.ocupacion()))
        i, k = np.nonzero(socios >= 0)
        j = socios[i, k]
        sel = i < j  # cada enlace una vez
        i, j = i[sel], j[sel]
        # sin dibujar los enlaces que cruzan el borde toroidal
        corto = (np.abs(p["x"][i] - p["x"][j]) <= 1) & (np.abs(p["y"][i] - p["y"][j]) <= 1)
        seg = np.stack([np.stack([p["x"][i], p["y"][i]], 1), np.stack([p["x"][j], p["y"][j]], 1)], 1)[corto]
        ax.add_collection(LineCollection(seg, colors="black", linewidths=0.6, alpha=0.8))
    if n:
        if (p["cepa"] > 0).any():
            color = np.where(p["cepa"] == 1, "tab:red", "tab:blue")
            ax.scatter(p["x"], p["y"], s=4, c=color, linewidths=0)
        else:
            ax.scatter(p["x"], p["y"], s=4, c=p["activo"].sum(1), cmap="plasma", linewidths=0,
                       vmin=0, vmax=sim.cfg.herencia.genes_max)
    ax.set_title(titulo or f"t = {sim.t}  ·  población = {n}")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(ruta, dpi=110)
    plt.close(fig)


def graficos(historial: list[dict[str, float]], ruta: Path, titulo: str = "") -> None:
    if not historial:
        return
    t = np.array([h["t"] for h in historial])

    def serie(clave):
        return np.array([h.get(clave, np.nan) for h in historial], dtype=float)

    asociacion = any("frac_enlazados" in h for h in historial)
    bien_publico = any("complejo_total" in h for h in historial)
    filas = 3 + asociacion + bien_publico
    fig, axs = plt.subplots(filas, 2, figsize=(12, 3.3 * filas), sharex=True)
    axs[0, 0].plot(t, serie("poblacion"))
    axs[0, 0].set_title("Población")
    axs[0, 1].plot(t, serie("energia_media"), label="energía media")
    axs[0, 1].plot(t, 100 * serie("estres_medio"), label="estrés ×100")
    axs[0, 1].legend()
    axs[0, 1].set_title("Energía y estrés")
    axs[1, 0].plot(t, serie("genes_medios"), label="genes activos")
    axs[1, 0].plot(t, serie("perfiles_distintos") / 10, label="perfiles distintos / 10")
    axs[1, 0].legend()
    axs[1, 0].set_title("Genoma")
    axs[1, 1].plot(t, serie("mu_media"), label="μ base")
    axs[1, 1].plot(t, serie("tasa_efectiva_media"), label="tasa efectiva")
    axs[1, 1].plot(t, serie("eta_media") / 10, label="η / 10")
    axs[1, 1].legend()
    axs[1, 1].set_title("Rasgos heredables")
    for nombre in gen.PRIMITIVAS:
        axs[2, 0].plot(t, serie(f"usa_{nombre}"), label=nombre)
        axs[2, 1].plot(t, serie(f"tiene_{nombre}"), label=nombre)
    axs[2, 0].set_title("Uso de cada primitiva (fracción de acciones)")
    axs[2, 1].set_title("Fracción de organismos con el gen")
    axs[2, 0].legend(fontsize=6, ncol=2)
    if asociacion:
        axs[3, 0].plot(t, serie("frac_enlazados"), label="fracción enlazados")
        axs[3, 0].plot(t, serie("grupos_de_3_o_mas"), label="en grupos de 3+")
        axs[3, 0].plot(t, serie("frac_aprovechados"), label="aprovechados (entre enlazados)")
        axs[3, 0].legend(fontsize=7)
        axs[3, 0].set_title("Asociación")
        axs[3, 1].plot(t, serie("tamano_grupo_medio"), label="tamaño de grupo medio")
        axs[3, 1].plot(t, serie("tamano_grupo_max") / 10, label="tamaño máximo / 10")
        axs[3, 1].plot(t, 10 * serie("compartido_por_org_paso"), label="compartido ×10")
        axs[3, 1].legend(fontsize=7)
        axs[3, 1].set_title("Grupos e intercambio")
    if bien_publico:
        f = 3 + asociacion
        axs[f, 0].plot(t, serie("tiene_secretar"), label="con gen de secretar")
        axs[f, 0].plot(t, serie("frac_enlazados_secretores"), label="enlazados entre secretores")
        axs[f, 0].plot(t, serie("frac_enlazados_no_secretores"), label="enlazados entre no secretores")
        axs[f, 0].legend(fontsize=7)
        axs[f, 0].set_title("Bien público: secretores")
        axs[f, 1].plot(t, serie("complejo_total") / 1000, label="recurso complejo / 1000")
        axs[f, 1].plot(t, serie("libre_total") / 100, label="alimento libre / 100")
        axs[f, 1].plot(t, 10 * serie("comido_libre_por_org_paso"), label="libre comido por org ×10")
        axs[f, 1].legend(fontsize=7)
        axs[f, 1].set_title("Bien público: campos")
    for ax in axs[-1]:
        ax.set_xlabel("paso")
    if titulo:
        fig.suptitle(titulo)
    fig.tight_layout()
    fig.savefig(ruta, dpi=100)
    plt.close(fig)
