BIN MONITORING:


- main topic to receive raw data:
	`iot_raw_data`
- re-route the sensor msg to the specific topics based on previous configuration

# Architecture

## `Python Wrapper` for management
- store **sensor-to-topic mappings** in Redis
- Provide REST API endpoints do **manage sensors and topics**
- `Producers`
    - send all sensor data to a single topic `iot-raw-data`
- `Kafka Processor (Streams)`
    - reads, analyse and routes messages
- `Consumers`
    - only need to listen on the topic they want
---

### API ENDPOINTS:

| endpoint | method | purpose|
|----------|--------|--------|
| */sensor/add* | `POST` | register a new sensor and assign it to a topic |
| */sensor/remove/{serial}* | `DELETE`| Remove a sensor from the system |
| */sensor/list* | `GET` | Get all registeres sensors and their topics |
| */sensor/get-topic/{serial}* | `GET` | Get the topic assigned to a sensor |
| *topic/create* | `POST` | Create a new Kafka Topic |
| */topic/delete/{topic}* | `DELETE`| Delete an existing Kafka topic |
| */topic/list* | `GET` | Get all existing topics | 


<br>
<br>
<br>

## 1. `Redis`
Simpler to implement and sensors only need a simple lookup : `serialNumber → topic`

```bash
 # Install Redis (Mac)
brew install redis
brew services start redis

# Install Redis (Linux)
sudo apt update
sudo apt install redis
sudo systemctl start redis

# Install Redis Python Library
pip install redis
```

- Instead of creating a separate topic for each sensor, you create a single topic where all events are sent.

    ```bash
    /usr/local/opt/kafka/bin/kafka-topics --create --topic iot-raw-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
    ```


## 2. kafka_wrapper - `binAPI`

- Each sensor sends its type and serial number to `iot-raw-data`

    - *python example*
    ```python
    # Kafka Configuration
    KAFKA_BROKER = "localhost:9092"
    RAW_TOPIC = "iot-raw-data"

    # Redis Setup
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    LOOKUP_FILE = "sensor_lookup.txt"
    KAFKA_BIN = "/usr/local/opt/kafka/bin/kafka-topics"  # Update if using Linux

    # Connect to Redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    # restore lookup
    def restore_sensors():
    """Load previous configurations into Redis and ensure topics exist in Kafka."""
        if not os.path.exists(LOOKUP_FILE):
            print("🔍 No previous configurations found. Starting fresh.")
            return

        print("Restoring previous configurations...")

        with open(LOOKUP_FILE, "r") as f:
            for line in f:
                sensor_id, topic = line.strip().split(":")
                r.set(sensor_id, topic)

                # Check if topic exists in Kafka
                topic_list_cmd = f"{KAFKA_BIN} --list --bootstrap-server localhost:9092"
                existing_topics = subprocess.check_output(topic_list_cmd, shell=True).decode()

                if topic not in existing_topics:
                    print(f"📌 Creating missing topic: {topic}")
                    create_topic_cmd = (
                        f"{KAFKA_BIN} --create --topic {topic} --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1"
                    )
                    subprocess.run(create_topic_cmd, shell=True)
        
        print("Restore complete. Sensors and topics are ready.")


    # Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    # Kafka Admin
    admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER)


    ### -------------|SENSOR MANAGEMENT ###

    @app.route("/sensor/add", methods=["POST"])
    def add_sensor():
        # add sensor to redis
        # write this connection on a lookup file

    @app.route("/sensor/remove/<serial>", methods=["DELETE"])
    def remove_sensor(serial):
        # remove sensor on redis
        # UPDATE lookup file


    @app.route("/sensor/list", methods=["GET"])
    def list_sensors():

    @app.route("/sensor/get-topic/<serial>", methods=["GET"])
    def get_sensor_topic(serial):

    ### -------------|TOPIC MANAGEMENT ###

    @app.route("/topic/create", methods=["POST"])
    def create_topic():

    @app.route("/topic/delete/<topic>", methods=["DELETE"])
    def delete_topic(topic):

    @app.route("/topic/list", methods=["GET"])
    def list_topics():




    ### MESSAGE ROUTING SERVICE ###
    def kafka_router():
        consumer = KafkaConsumer(
            RAW_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )

        print("🔄 Kafka Router Running...")

        for msg in consumer:
            event = msg.value
            serial_number = event.get("serialNumber")

            if not serial_number:
                print("⚠️ Invalid event:", event)
                continue

            target_topic = redis_client.get(serial_number)  # Get topic from Redis

            if target_topic:
                print(f"🔀 Routing {serial_number} to {target_topic}")
                producer.send(target_topic, event)
            else:
                print(f"⚠️ Sensor {serial_number} not registered. Dropping event.")


    # Start Kafka Router in a separate thread
    threading.Thread(target=kafka_router, daemon=True).start()
    ```


- Each sensor sends:
    - **serialNumber:** Uniquely identifies the sensor
    - **value:** The measurement/event from the sensor
    - **...** the params the sensor sends

---

## How to Run

1. Start `Redis`
```bash
redis-server
```

2. Start `kafka+zookeper``
```bash
# macOs
brew services start zookeeper
brew services start kafka
```

3. Run `binAPI`
```bash
python kafka_wrapper.py
```

## How to use API

```bash
## -----------| SENSOR MANAGMENT ##

# Add a sensor
curl -X POST "http://localhost:5000/sensor/add" -H "Content-Type: application/json" -d '{"sensor_id": "sensor_001", "topic": "temperature_readings"}'

# Remove a sensor
curl -X DELETE "http://localhost:5000/sensor/remove/sensor_001"

# List all sensors
curl -X GET "http://localhost:5000/sensor/list"

# Ger a topic for a sensor
curl -X GET "http://localhost:5000/sensor/get-topic/sensor_001"




## -----------| TOPIC MANAGMENT ##

# Create a topic
curl -X POST "http://localhost:5000/topic/create" -H "Content-Type: application/json" -d '{"topic": "humidity_readings"}'

# Delete a topic
curl -X DELETE "http://localhost:5000/topic/delete/humidity_readings"

# List all kafka topics
curl -X GET "http://localhost:5000/topic/list"

```

