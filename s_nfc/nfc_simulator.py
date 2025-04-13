import random
import time
import json
from kafka import KafkaProducer

# Configurações Kafka
KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "nfc_logs"

# IMEIs simulados
IMEIS = [
    "123456789012345",  # do admin
    "987654321098765"   # do user
]

# Serial dos caixotes (simulação)
BINS = [f"BIN-AVE-{str(i).zfill(3)}" for i in range(1, 31)]

# Inicializa produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("🚀 Simulador de interações NFC iniciado. A publicar em loop no tópico nfc_logs...\n")

try:
    while True:
        # Escolhe aleatoriamente um bin e um IMEI
        imei = random.choice(IMEIS)
        serial = random.choice(BINS)

        # Cria a mensagem de uso
        message = {
            "imei": imei,
            "serial": serial,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Publica no tópico nfc_logs
        producer.send(KAFKA_TOPIC, value=message)
        print(f"📤 Enviado para {KAFKA_TOPIC}: {message}")

        # Espera entre 3 a 7 segundos
        time.sleep(random.uniform(3.0, 7.0))

except KeyboardInterrupt:
    print("\n🛑 Simulador interrompido pelo utilizador.")
    producer.close()
