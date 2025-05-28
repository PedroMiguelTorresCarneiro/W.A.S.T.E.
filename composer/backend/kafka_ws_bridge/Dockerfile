FROM python:3.10-slim

MAINTAINER Pedro Carneiro

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

EXPOSE 5006

CMD ["python", "kafka-ws-bridge.py"]
