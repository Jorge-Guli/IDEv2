"""Imágenes del mundo y gráficos de métricas."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import genoma as gen  # noqa: E402


def imagen_mundo(sim, ruta: Path, titulo: str = "") -> None:
    p = sim.pob
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.imshow(sim.entorno.R, cmap="Greens", vmin=0, vmax=sim.cfg.mundo.capacidad_max, interpolation="nearest")
    if p.n:
        if (p["cepa"] > 0).any():
            color = np.where(p["cepa"] == 1, "tab:red", "tab:blue")
            ax.scatter(p["x"], p["y"], s=4, c=color, linewidths=0)
        else:
            ax.scatter(p["x"], p["y"], s=4, c=p["activo"].sum(1), cmap="plasma", linewidths=0,
                       vmin=0, vmax=sim.cfg.herencia.genes_max)
    ax.set_title(titulo or f"t = {sim.t}  ·  población = {p.n}")
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

    fig, axs = plt.subplots(3, 2, figsize=(12, 10), sharex=True)
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
    axs[2, 0].legend(fontsize=7)
    for ax in axs[2]:
        ax.set_xlabel("paso")
    if titulo:
        fig.suptitle(titulo)
    fig.tight_layout()
    fig.savefig(ruta, dpi=100)
    plt.close(fig)
