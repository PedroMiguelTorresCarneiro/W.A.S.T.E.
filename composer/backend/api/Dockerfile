FROM python:3.10-slim

MAINTAINER Pedro Carneiro

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

EXPOSE 5008

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5008"]
