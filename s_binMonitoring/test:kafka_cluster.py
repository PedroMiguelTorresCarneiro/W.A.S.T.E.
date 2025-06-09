from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='193.136.82.35:30092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

test_message = {
    "serial": "sensor_nfc_001",
    "timestamp": "2025-06-04T16:00:00Z",
    "uid": "0xAB12CD34",
    "event": "nfc_tag_read"
}

producer.send("nfc_logs", value=test_message)
producer.flush()

print("✅ Mensagem enviada para 'nfc_logs'")
