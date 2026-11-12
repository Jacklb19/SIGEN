FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir --no-deps .

FROM base AS pruebas
COPY requirements-dev.txt ./
RUN python -m pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
COPY scripts ./scripts
CMD ["python", "scripts/verificar_calidad.py"]

FROM base AS aplicacion
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "sigen.api:app", "--host", "0.0.0.0", "--port", "8000"]
