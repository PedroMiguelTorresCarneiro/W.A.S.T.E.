FROM python:3.11-slim

# Instala dependências do sistema (incluindo MariaDB C Connector)
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas o ficheiro de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte
COPY . .

# Define o comando de arranque
CMD ["python", "routesAPI_v2.py"]
