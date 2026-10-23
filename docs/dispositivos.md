# Dispositivos de cálculo: CPU y GPU

El simulador **detecta el hardware automáticamente**. Si hay una GPU NVIDIA y CuPy está instalado, usa la GPU. Si no, usa la CPU con NumPy. No hace falta cambiar nada para replicar un experimento en otro equipo.

## Elegir el dispositivo

- Automático (por defecto): `--set sim.dispositivo=auto`
- Forzar CPU: `--set sim.dispositivo=cpu`, o la variable de entorno `SIMBIO_DISPOSITIVO=cpu`
- Forzar GPU: `--set sim.dispositivo=gpu`. Falla con un mensaje claro si no hay GPU utilizable.

Cada corrida registra en `resumen.json` qué dispositivo usó.

## Verificar

```bash
python -m simbio dispositivo
```
Muestra qué se detectó, cuántos pasos por segundo rinde cada dispositivo según el tamaño del mundo y si CPU y GPU coinciden. Con GPU, además, `python -m pytest -q` ejecuta las pruebas de GPU (determinismo, invariantes y coincidencia con la CPU), que sin GPU se omiten.

## Reproducibilidad

- Los números aleatorios se generan **siempre en la CPU** con la semilla y se copian al dispositivo. CPU y GPU consumen la misma secuencia aleatoria.
- **Mismo dispositivo y misma semilla = mismo resultado exacto.**
- Entre CPU y GPU, el redondeo de punto flotante difiere en la última cifra. Las trayectorias arrancan iguales y con el tiempo pueden separarse, pero sus resultados son **estadísticamente equivalentes**. Por eso las conclusiones del proyecto se basan siempre en varias semillas, nunca en una trayectoria puntual.

## Cuándo conviene la GPU

Mover datos a la GPU tiene un costo fijo por paso, y con pocos organismos (~2000) la CPU puede ser igual o más rápida. La GPU rinde con mundos grandes y decenas o cientos de miles de organismos. `python -m simbio dispositivo` lo mide en tu equipo.

## Instalar soporte de GPU (NVIDIA)

> Si la detección encuentra la GPU pero no puede usarla (por ejemplo, faltan las cabeceras de CUDA), el modo automático **avisa y sigue en CPU**: nunca interrumpe una corrida.

1. Mira tu versión de CUDA con `nvidia-smi` (arriba a la derecha, "CUDA Version").
2. Instala CuPy para esa versión, dentro del entorno virtual del proyecto:
   ```bash
   pip install -e ".[gpu-cuda13]"   # CUDA 13.x
   # o bien
   pip install -e ".[gpu-cuda12]"   # CUDA 12.x
   ```
   Las GPU recientes (serie RTX 50) requieren CUDA 12.8 o superior. Si la instalación para CUDA 13 no está disponible para tu plataforma, prueba la de CUDA 12: el controlador de una versión 13 también ejecuta programas compilados para la 12.
   El extra incluye `[ctk]`, que instala por pip las cabeceras de CUDA que CuPy necesita para compilar. Sin ellas aparece *"Failed to find CUDA headers"*.
3. **Instala un solo paquete de CuPy.** Si instalaste más de uno, desinstálalos todos primero (`pip uninstall cupy-cuda12x cupy-cuda13x`).
4. Verifica con `python -m simbio dispositivo`.

Sin GPU NVIDIA (AMD, Intel, Apple), el simulador funciona igual en CPU.
