# FROM python:3.10-slim

# MAINTAINER Pedro Carneiro

# WORKDIR /app

# COPY app/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY app/ /app/

# EXPOSE 5006

# CMD ["python", "kafka-ws-bridge.py"]

FROM python:3.10-slim

LABEL maintainer="Pedro Carneiro"

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

EXPOSE 5006

CMD ["uvicorn", "kafka_ws_bridge:app", "--host", "0.0.0.0", "--port", "5006"]
