from kafka import KafkaConsumer
import json

KAFKA_SERVER = 'localhost:9092'
TOPIC = 'bin_monitoring'

def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='latest',  # ou 'earliest' se quiseres ver tudo desde o início
        enable_auto_commit=True,
        group_id='test-bin-monitor',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print(f"👂 A ouvir o tópico '{TOPIC}'...")
    for msg in consumer:
        print(f"📩 Mensagem recebida: {msg.value}")

if __name__ == "__main__":
    main()
