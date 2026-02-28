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


FROM python:3.12-slim-bookworm
WORKDIR /app

# (Instalação de pacotes e criação do usuário deploy continua igual...)

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

COPY . .

# --- ADICIONE ESTAS LINHAS AQUI ---
# Dá permissão ao usuário deploy e torna o script executável
RUN chown -R deploy:deploygroup /app && \
    chmod +x /app/entrypoint.sh

USER deploy

# O ENTRYPOINT garante que as migrações rodem sempre
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000

# O CMD vira o argumento padrão para o entrypoint
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]