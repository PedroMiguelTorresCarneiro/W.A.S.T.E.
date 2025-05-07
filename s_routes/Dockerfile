FROM python:3.8-alpine

MAINTAINER Pedro Carneiro

# Instala só MariaDB Connector e headers Python
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    mariadb-dev

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "routesAPI_v2.py"]
