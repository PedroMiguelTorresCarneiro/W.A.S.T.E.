# KAFKA

Funciona com :
- **Produtores :** serviços que enviam eventos para um **tópico** kafka
- **Tópicos :** São "canais" onde os eventos são organizados e armazenados
- **Brokers :** são servidores kafka que armazenam e distribuem os eventos
- **Consumidores:** são serviços que "escutam" os tópicos e processam os eventos


## **MacOS Setup**
```bash
### 1. Install Kafka & Zookeeper
brew install kafka
brew install zookeeper

### 2. Start Kafka & Zookeeper
brew services start zookeeper
brew services start kafka

### 3. Check Running Services
brew services list

### 4. Stop Kafka & Zookeeper
brew services stop kafka
brew services stop zookeeper

### 5. Create a Kafka Topic
/usr/local/opt/kafka/bin/kafka-topics --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

### 6. Start a Kafka Producer
/usr/local/opt/kafka/bin/kafka-console-producer --broker-list localhost:9092 --topic test-topic

### 7. Start a Kafka Consumer
/usr/local/opt/kafka/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic test-topic --from-beginning
```

---

## **Linux Setup**
```bash
### 1. Install Kafka & Zookeeper
sudo apt update
sudo apt install kafka zookeeper

# Extract Kafka package (if installed manually)
tar -xvzf kafka_2.13-3.9.0.tgz
cd kafka_2.13-3.9.0

### 2. Start Kafka & Zookeeper
sudo systemctl start zookeeper
sudo systemctl start kafka

### 3. Check Running Services
sudo systemctl status kafka
sudo systemctl status zookeeper

### 4. Stop Kafka & Zookeeper
sudo systemctl stop kafka
sudo systemctl stop zookeeper

### 5. Create a Kafka Topic
/opt/kafka/bin/kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

### 6. Start a Kafka Producer
/opt/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test-topic

### 7. Start a Kafka Consumer
/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --from-beginning
```

---
<br>
<br>
<br>

# WASTE

<br>

## 1. Create Kafka Topics for each service : 
- `nfc-auth` 
- `bin-monitoring`

	- `linux` 
		```bash
		# Create Kafka topics
		## nfc-auth
		/opt/kafka/bin/kafka-topics.sh --create --topic nfc-auth --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
		## bin-monitoring
		/opt/kafka/bin/kafka-topics.sh --create --topic bin-monitoring --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

		# List topics
		/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

		# Describe a topic
		/opt/kafka/bin/kafka-topics.sh --describe --topic <topic-name> --bootstrap-server localhost:9092

		# Delete a topic
		/opt/kafka/bin/kafka-topics.sh --delete --topic <topic-name> --bootstrap-server localhost:9092
		```
	- `macOS` 
		```bash

		# Create Kafka topics
		## nfc-auth
		/usr/local/opt/kafka/bin/kafka-topics --create --topic nfc-auth --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
		## bin-monitoring
		/usr/local/opt/kafka/bin/kafka-topics --create --topic bin-monitoring --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

		# List topics
		/usr/local/opt/kafka/bin/kafka-topics --list --bootstrap-server localhost:9092

		# Describe a topic
		/usr/local/opt/kafka/bin/kafka-topics --describe --topic <topic-name> --bootstrap-server localhost:9092

		# Delete a topic
		/usr/local/opt/kafka/bin/kafka-topics --delete --topic <topic-name> --bootstrap-server localhost:9092
		```

## 2. PRODUCERS 
The `NFC Auth` and `Bin Monitoring` services will act as **producers**, sending events to the respective topics.

- **EXAMPLE for a producer for `NFC AUTH`**
	```python
	ffrom kafka import KafkaProducer
	import json
	import time

	producer = KafkaProducer(
		bootstrap_servers="localhost:9092",
		value_serializer=lambda v: json.dumps(v).encode("utf-8")
	)

	def enviar_evento_nfc(user_id):
		evento = {
			"tipo": "NFC",
			"user_id": user_id,
			"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
		}
		producer.send("nfc-auth", evento)
		print(f"Enviado evento NFC: {evento}")
		producer.flush()

	# Simulação de um evento NFC
	enviar_evento_nfc("12345")
	```

- **EXEMPLO para um produtor para `BIN MONITORING`**
	```python
	from kafka import KafkaProducer
	import json
	import time
	import random

	producer = KafkaProducer(
		bootstrap_servers="localhost:9092",
		value_serializer=lambda v: json.dumps(v).encode("utf-8")
	)

	def enviar_evento_bin(sensor_id, nivel_enchimento):
		evento = {
			"tipo": "BIN",
			"sensor_id": sensor_id,
			"nivel_enchimento": nivel_enchimento,
			"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
		}
		producer.send("bin-monitoring", evento)
		print(f"Enviado evento Bin Monitoring: {evento}")
		producer.flush()

	# Simulação de um evento de sensor de lixo
	enviar_evento_bin("bin_01", random.randint(0, 100))
	```


---
<br>
<br>

## 2. Consumidores
- `nfc-auth` 
- `bin-monitoring`

	- `linux` 
		```bash
		# Consumer for NFC Authentication
		/opt/kafka/bin/kafka-console-consumer.sh --topic nfc-auth --from-beginning --bootstrap-server localhost:9092

		# Consumer for Bin Monitoring
		/opt/kafka/bin/kafka-console-consumer.sh --topic bin-monitoring --from-beginning --bootstrap-server localhost:9092
		```
	- `macOS` 
		```bash
		# Consumer for NFC Authentication
		/usr/local/opt/kafka/bin/kafka-console-consumer --topic nfc-auth --from-beginning --bootstrap-server localhost:9092

		# Consumer for Bin Monitoring
		/usr/local/opt/kafka/bin/kafka-console-consumer --topic bin-monitoring --from-beginning --bootstrap-server localhost:9092
		```


### No nosso caso o `COMPOSER` vai ser um consumidor *kafka* direto
Pequeno exemplo de como poderia ser implementado:
```python
from kafka import KafkaConsumer
import json

# O COMPOSER escuta diretamente o Kafka
consumer = KafkaConsumer(
    "nfc-auth",
    "bin-monitoring",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("O COMPOSER está à escuta do Kafka...")

for message in consumer:
    print(f"Recebido no tópico {message.topic}: {message.value}")
```

Podendo depois tratar a informação, armazena-la etc onde quisermos e da forma que quisermos!



