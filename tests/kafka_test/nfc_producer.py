from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Serialização correta para JSON
)

def enviar_evento_nfc(user_id):
    evento = {
        "tipo": "NFC",
        "user_id": user_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    producer.send("nfc-auth", key=str(user_id).encode(), value=evento)  # A chave precisa de bytes
    print(f"✅ Enviado evento NFC: {evento}")
    producer.flush()

# Simulação de um evento NFC
enviar_evento_nfc("12345")
enviar_evento_nfc("54321")
enviar_evento_nfc("12345")
enviar_evento_nfc("54321")