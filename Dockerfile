# --- Estágio 1: Builder (Compilação) ---
FROM python:3.12-slim-bookworm AS builder

# Impede que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos as dependências de compilação apenas aqui
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criamos um "wheels" das dependências (pacotes pré-compilados)
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# --- Estágio 2: Final (Produção) ---
FROM python:3.12-slim-bookworm

WORKDIR /app

# Variáveis de ambiente mantidas para execução
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos APENAS a biblioteca de runtime do Postgres (necessária para rodar o app)
# Criamos um usuário comum para não rodar a aplicação como root (segurança)
RUN apt-get update && apt-get install -y libpq5 \
    && addgroup --system appgroup \
    && adduser --system --group appuser \
    && rm -rf /var/lib/apt/lists/*

# Copiamos os pacotes compilados do estágio anterior e instalamos
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

# Copiamos o código da aplicação
COPY . .

# Ajustamos as permissões para o novo usuário
# Garantimos que staticfiles e media existam e sejam graváveis pelo appuser
RUN mkdir -p /app/staticfiles /app/media && \
    chmod +x /app/entrypoint.sh && \
    chown -R appuser:appgroup /app

# Mudamos para o usuário sem privilégios
USER appuser

EXPOSE 8000

# Script de inicialização (migrations + collectstatic + gunicorn)
ENTRYPOINT ["/app/entrypoint.sh"]