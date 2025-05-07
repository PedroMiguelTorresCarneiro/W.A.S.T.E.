import random
import time
import json
from kafka import KafkaProducer
from config import KAFKA_TOPIC, KAFKA_SERVER


# Lista dos caixotes (serials)
BINS = [f"BIN-AVE-{str(i).zfill(3)}" for i in range(1, 31)]

# Inicializa produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("🚀 Simulador de bins iniciado. A publicar em loop no tópico iot_logs...\n")

try:
    while True:
        # Escolher bin aleatório
        serial = random.choice(BINS)

        # Simular valor de enchimento entre 10% e 100%
        fill_level = random.randint(10, 100)

        # Criar mensagem
        message = {
            "serial": serial,
            "fill_level": fill_level
        }

        # Publicar
        producer.send(KAFKA_TOPIC, value=message)
        print(f"📤 Enviado: {message}")

        # Esperar entre 6 e 15 segundos
        time.sleep(random.uniform(6.0, 15.0))

except KeyboardInterrupt:
    print("\n🛑 Simulador interrompido pelo utilizador.")
    producer.close()
