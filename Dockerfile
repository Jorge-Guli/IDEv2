# Universo vivo (fase 12): imagen para correr un universo de simbio sin plazo.
# La simulación no necesita red: docker-compose.yml la arranca sin acceso a internet (network_mode: none).
FROM python:3.12-slim

WORKDIR /simbio
COPY pyproject.toml README.md ./
COPY src ./src
COPY experiments/configs ./experiments/configs
RUN pip install --no-cache-dir .

# los datos del universo (estado, métricas, linaje) viven en /datos, montado desde el equipo
VOLUME ["/datos"]
ENV PYTHONUNBUFFERED=1 SIMBIO_DISPOSITIVO=cpu
ENTRYPOINT ["python", "-m", "simbio", "vivir"]
CMD ["experiments/configs/vivo.toml", "--salida", "/datos/universo", "--guardar-cada", "10000"]
