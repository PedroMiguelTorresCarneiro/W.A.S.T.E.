# import random
# import time
# import json
# from kafka import KafkaProducer
# from config import KAFKA_TOPIC, KAFKA_SERVER


# # Lista dos caixotes (serials)
# BINS = [f"BIN-AVE-{str(i).zfill(3)}" for i in range(1, 31)]

# # Inicializa produtor Kafka
# producer = KafkaProducer(
#     bootstrap_servers=KAFKA_SERVER,
#     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# )

# print("🚀 Simulador de bins iniciado. A publicar em loop no tópico iot_logs...\n")

# try:
#     while True:
#         # Escolher bin aleatório
#         serial = random.choice(BINS)

#         # Simular valor de enchimento entre 10% e 100%
#         fill_level = random.randint(10, 100)

#         # Criar mensagem
#         message = {
#             "serial": serial,
#             "fill_level": fill_level
#         }

#         # Publicar
#         producer.send(KAFKA_TOPIC, value=message)
#         print(f"📤 Enviado: {message}")

#         # Esperar entre 6 e 15 segundos
#         time.sleep(random.uniform(6.0, 15.0))

# except KeyboardInterrupt:
#     print("\n🛑 Simulador interrompido pelo utilizador.")
#     producer.close()


import random
import time
import requests

# URL da API FastAPI para publicar dados dos sensores
POSTING_API_URL = "http://grupo2-egs-deti.ua.pt/v1/posting/sensors"

# Lista dos caixotes (serials)
BINS = [f"BIN-AVE-{str(i).zfill(3)}" for i in range(1, 31)]

print("🚀 Simulador de bins (HTTP) iniciado. A publicar em loop na API Posting...\n")

try:
    while True:
        # Escolher bin aleatório
        serial = random.choice(BINS)

        # Simular valor de enchimento entre 10% e 100%
        fill_level = random.randint(10, 100)

        # Criar payload
        payload = {
            "serial": serial,
            "fill_level": fill_level
        }

        # Enviar para a API via POST
        response = requests.post(POSTING_API_URL, json=payload)

        if response.status_code == 200:
            print(f"📤 Enviado: {payload}")
        else:
            print(f"⚠️ Erro ao enviar: {response.status_code} → {response.text}")

        # Esperar entre 6 e 15 segundos
        time.sleep(random.uniform(6.0, 15.0))

except KeyboardInterrupt:
    print("\n🛑 Simulador interrompido pelo utilizador.")



# comandos para testar o Kafka no pod:

# /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bin_monitoring --from-beginning

# /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic iot_logs --from-beginning
