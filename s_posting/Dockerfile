# Base com Python 3.11 slim
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema para kafka-python
RUN apt-get update && apt-get install -y gcc libsnappy-dev && apt-get clean

# Copiar requirements.txt da raiz e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da API que está em app/
COPY app/ .

# Porta usada pelo serviço
EXPOSE 5010

# Comando para arrancar o servidor FastAPI com Uvicorn
CMD ["uvicorn", "postingAPI:app", "--host", "0.0.0.0", "--port", "5010"]
