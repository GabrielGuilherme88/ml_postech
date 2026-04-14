# Dockerfile para Ana - Auditora de Saúde
# Este arquivo deve ser construído a partir da raiz do projeto:
# docker build -t ana-api -f src/serving/Dockerfile .

FROM python:3.10-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/models_cache

WORKDIR /app

# Instala dependências de sistema necessárias para compilação e segurança
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de definição de dependências
COPY pyproject.toml .
# Caso exista um requirements.txt, copie-o também para garantir
COPY requirements.txt* .

# Instala as dependências (incluindo o próprio pacote em modo editável ou não)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

# Cria simlink para compatibilidade com dvc.yaml que usa caminhos locais do host
RUN mkdir -p /app/ambi/bin && ln -s $(which python) /app/ambi/bin/python

# Copia o restante do código fonte
COPY . .

# Expõe a porta que a API FastAPI utiliza
EXPOSE 8000

# Comando para iniciar a aplicação
# Nota: app/app.py já contém a lógica de inicialização com uvicorn
CMD ["python", "app/app.py"]
