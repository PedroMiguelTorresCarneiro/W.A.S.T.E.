FROM python:3.8-alpine

MAINTAINER Inês Águia

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "binAPI_v2.py"]
