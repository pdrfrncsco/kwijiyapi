# --- Estágio 1: Builder (Compilação) ---
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala ferramentas de compilação necessárias 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Gera os wheels das dependências para evitar recompilar na imagem final [cite: 2]
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# --- Estágio 2: Final (Produção) ---
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Instala apenas a biblioteca de runtime do Postgres e cria o usuário 'deploy'
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && addgroup --system deploygroup \
    && adduser --system --group deploy \
    && rm -rf /var/lib/apt/lists/*

# 2. Instala as dependências a partir dos wheels do builder [cite: 2]
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# 3. Copia o código da aplicação e o entrypoint 
COPY . .

# 4. Corrige finais de linha (Windows/Linux), dá permissão de execução e ajusta o dono da pasta 
RUN sed -i 's/\r$//' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    chown -R deploy:deploygroup /app

RUN mkdir -p /app/staticfiles /app/media && \
    chown -R deploy:deploygroup /app/staticfiles /app/media
# Muda para o usuário sem privilégios antes de iniciar
USER deploy

# O ENTRYPOINT garante que as migrações e o collectstatic rodem sempre 
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000

# Se você tiver o arquivo gunicorn_config.py, use este CMD 
CMD ["gunicorn", "--config", "gunicorn_config.py", "config.wsgi:application"]