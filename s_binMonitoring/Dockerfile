# Dockerfile (na raiz do projeto bin_monitoring/)
FROM python:3.10-slim

MAINTAINER Inês Águia

WORKDIR /app

# Copia requirements e instala
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os ficheiros da app
COPY app/ /app/


EXPOSE 5004

# Arranca a aplicação
CMD ["python", "binAPI_v2.py"]
