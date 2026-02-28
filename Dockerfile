# =============================================================================
# Estágio 1: Builder — compila as dependências Python em wheels
# =============================================================================
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt


# =============================================================================
# Estágio 2: Runtime — imagem final enxuta para produção
# =============================================================================
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Instala apenas o runtime do Postgres e cria utilizador com o mesmo UID/GID
# do utilizador 'deploy' no host (confirma com: id deploy)
ARG DEPLOY_UID=1001
ARG DEPLOY_GID=1001

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && addgroup --gid ${DEPLOY_GID} deploy \
    && adduser --uid ${DEPLOY_UID} --ingroup deploy --no-create-home --disabled-password --gecos "" deploy \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências a partir dos wheels gerados no builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copia o código da aplicação
COPY . .

# Garante permissões corretas no entrypoint e cria pastas de artefactos estáticos
RUN sed -i 's/\r$//' /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R deploy:deploy /app

USER deploy

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
