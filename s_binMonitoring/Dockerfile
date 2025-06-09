FROM python:3.8-alpine

WORKDIR /

# Copia requirements e instala
COPY app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os ficheiros da app
COPY app/. .


EXPOSE 5004

# Arranca a aplicação
#CMD ["python", "binAPI_v2.py"]
CMD ["uvicorn", "binAPI_v2:app", "--host", "0.0.0.0", "--port", "5004"]
