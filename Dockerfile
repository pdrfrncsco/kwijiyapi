# --- Estágio 1: Builder ---
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# --- Estágio 2: Final (Produção) ---
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos libpq5 e criamos o usuário 'deploy'
RUN apt-get update && apt-get install -y libpq5 \
    && addgroup --system deploygroup \
    && adduser --system --group deploy \
    && rm -rf /var/lib/apt/lists/*

# Copiamos as dependências do builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

# Copiamos o código
COPY . .

# Garantimos que o usuário 'deploy' seja dono da pasta /app
RUN chown -R deploy:deploygroup /app

# Mudamos para o usuário de produção
USER deploy

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]