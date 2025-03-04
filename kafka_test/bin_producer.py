from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Lista de caixotes do lixo com IDs e coordenadas GPS
bins = [
    {"sensor_id": "bin_01", "latitude": 40.6413, "longitude": -8.6535},
    {"sensor_id": "bin_02", "latitude": 40.6421, "longitude": -8.6512},
    {"sensor_id": "bin_03", "latitude": 40.6435, "longitude": -8.6550},
    {"sensor_id": "bin_04", "latitude": 40.6402, "longitude": -8.6528}
]

def enviar_evento_bin(sensor_id, nivel_enchimento, latitude, longitude):
    evento = {
        "tipo": "BIN",
        "sensor_id": sensor_id,
        "nivel_enchimento": nivel_enchimento,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    producer.send("bin-monitoring", evento)
    print(f"Enviado evento Bin Monitoring: {evento}")
    producer.flush()

# Simulação de eventos durante 1 minuto
start_time = time.time()
while time.time() - start_time < 60:
    bin_data = random.choice(bins)  # Escolher um dos 4 sensores
    nivel_enchimento = random.randint(0, 100)  # Nível de enchimento aleatório
    enviar_evento_bin(bin_data["sensor_id"], nivel_enchimento, bin_data["latitude"], bin_data["longitude"])
    time.sleep(random.uniform(1, 5))  # Simular um intervalo realista entre eventos
