FROM python:3.11-slim

# Instala dependências de sistema necessárias para o OpenCV e processamento de imagens
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação e artefatos necessários
COPY app.py .
COPY index.html .
COPY visao_computacional.py .
COPY models/ ./models/
COPY images/ ./images/
COPY docs/ ./docs/

# Expõe a porta padrão da aplicação
EXPOSE 8000

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
