FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/models_cache

WORKDIR /app

# 1. Instala dependências de sistema (Quase nunca muda, fica em cache)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Copia APENAS os arquivos de dependências
COPY pyproject.toml .
COPY requirements.txt* .

# 3. Instala as bibliotecas (Se o pyproject.toml não mudou, o Docker pula isso)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]" && \
    python -m spacy download en_core_web_lg

# 4. Cria o simlink
RUN mkdir -p /app/ambi/bin && ln -s $(which python) /app/ambi/bin/python

# 5. SÓ AGORA copia o código fonte
# Como o código muda sempre, esta camada raramente usa cache.
# Mas como o 'pip install' está acima, ele não é afetado por mudanças aqui!
COPY . .

EXPOSE 8000

CMD ["python", "app/app.py"]