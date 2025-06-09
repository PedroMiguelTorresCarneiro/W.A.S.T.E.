# FROM python:3.8-alpine

# MAINTAINER Pedro Carneiro

# WORKDIR /app

# RUN apk add --no-cache \
#     gcc \
#     musl-dev \
#     python3-dev \
#     mariadb-dev

# COPY requirements.txt .
# COPY app/ /app/

# RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 5002

# CMD ["python", "routesAPI_v2.py"]

FROM python:3.8-alpine

MAINTAINER Pedro Carneiro

WORKDIR /app

# Instalar dependências do sistema (para compilação e drivers MariaDB)
RUN apk add --no-cache \
    build-base \
    mariadb-dev \
    libffi-dev

# Copiar ficheiros
COPY requirements.txt .
COPY app/ /app/

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta usada pelo Uvicorn
EXPOSE 5002

# Comando para correr o servidor FastAPI com Uvicorn
CMD ["uvicorn", "routesAPI_v2:app", "--host", "0.0.0.0", "--port", "5002"]
