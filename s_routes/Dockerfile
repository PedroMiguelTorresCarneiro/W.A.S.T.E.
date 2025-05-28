FROM python:3.8-alpine

MAINTAINER Pedro Carneiro

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    mariadb-dev

COPY requirements.txt .
COPY app/ /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5002

CMD ["python", "routesAPI_v2.py"]
