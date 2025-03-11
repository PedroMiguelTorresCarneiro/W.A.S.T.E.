import os
import json
import redis
import subprocess
from flask import Flask, request, jsonify
from flasgger import Swagger
import shutil

# Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
LOOKUP_FILE = "sensor_lookup.txt"

def find_kafka_bin():
    """Dynamically find Kafka binaries based on the system."""
    # Try finding kafka-topics in the system PATH
    kafka_bin = shutil.which("kafka-topics")
    
    # If not found, try common installation paths
    if not kafka_bin:
        common_paths = [
            "/usr/local/opt/kafka/bin/kafka-topics",  # macOS (Homebrew)
            "/opt/kafka/bin/kafka-topics",  # Linux (APT/YUM manual install)
            "/usr/bin/kafka-topics",  # Linux (common bin)
            "/usr/local/bin/kafka-topics"  # Alternative macOS/Linux
        ]
        for path in common_paths:
            if os.path.exists(path):
                kafka_bin = path
                break

    # If still not found, raise an error
    if not kafka_bin:
        raise FileNotFoundError("Kafka binary not found! Make sure Kafka is installed and available in the system PATH.")

    return kafka_bin
KAFKA_BIN = find_kafka_bin()
print(f"Kafka binary found at: {KAFKA_BIN}")

KAFKA_SERVER = "localhost:9092"

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Flask
app = Flask(__name__)
swagger = Swagger(app)  # Auto-generate Swagger docs

def find_kafka_bin():
    """Dynamically find Kafka binaries based on the system."""
    # Try finding kafka-topics in the system PATH
    kafka_bin = shutil.which("kafka-topics")
    
    # If not found, try common installation paths
    if not kafka_bin:
        common_paths = [
            "/usr/local/opt/kafka/bin/kafka-topics",  # macOS (Homebrew)
            "/opt/kafka/bin/kafka-topics",  # Linux (APT/YUM manual install)
            "/usr/bin/kafka-topics",  # Linux (common bin)
            "/usr/local/bin/kafka-topics"  # Alternative macOS/Linux
        ]
        for path in common_paths:
            if os.path.exists(path):
                kafka_bin = path
                break

    # If still not found, raise an error
    if not kafka_bin:
        raise FileNotFoundError("Kafka binary not found! Make sure Kafka is installed and available in the system PATH.")

    return kafka_bin


def config_lookup():
    """Restores Redis and Kafka topics from the lookup file at startup."""
    if not os.path.exists(LOOKUP_FILE):
        print("🔍 No previous configurations found. Starting fresh.")
        return

    print("🔄 Restoring previous configurations...")

    with open(LOOKUP_FILE, "r") as f:
        for line in f:
            sensor_id, topic = line.strip().split(":")
            r.set(sensor_id, topic)

            existing_topics = subprocess.check_output(
                f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
                shell=True
            ).decode()

            if topic not in existing_topics:
                print(f"📌 Creating missing topic: {topic}")
                subprocess.run(
                    f"{KAFKA_BIN} --create --topic {topic} --bootstrap-server {KAFKA_SERVER} --partitions 3 --replication-factor 1",
                    shell=True
                )
    
    print("✅ Restore complete. Sensors and topics are ready.")

@app.route("/sensor/add", methods=["POST"])
def api_add_sensor():
    """
    Register a new sensor and assign it to a topic.
    ---
    tags:
      - Sensors
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - sensor_id
            - topic
          properties:
            sensor_id:
              type: string
              description: The unique ID of the sensor
            topic:
              type: string
              description: The Kafka topic to assign the sensor
    responses:
      201:
        description: Sensor successfully added
      400:
        description: Invalid input
    """
    data = request.json
    sensor_id = data.get("sensor_id")
    topic = data.get("topic")

    if not sensor_id or not topic:
        return jsonify({"error": "sensor_id and topic are required"}), 400

    r.set(sensor_id, topic)
    with open(LOOKUP_FILE, "a") as f:
        f.write(f"{sensor_id}:{topic}\n")

    return jsonify({"message": f"Sensor {sensor_id} added to topic {topic}"}), 201

@app.route("/sensor/remove/<sensor_id>", methods=["DELETE"])
def api_remove_sensor(sensor_id):
    """
    Remove a sensor from the system.
    ---
    tags:
      - Sensors
    parameters:
      - name: sensor_id
        in: path
        required: true
        type: string
        description: The unique ID of the sensor
    responses:
      200:
        description: Sensor successfully removed
      404:
        description: Sensor not found
    """
    if not r.exists(sensor_id):
        return jsonify({"error": "Sensor not found"}), 404

    r.delete(sensor_id)
    return jsonify({"message": f"Sensor {sensor_id} removed"}), 200

@app.route("/sensor/list", methods=["GET"])
def api_list_sensors():
    """
    Get all registered sensors and their topics.
    ---
    tags:
      - Sensors
    responses:
      200:
        description: A list of registered sensors
    """
    sensors = {key: value for key, value in r.scan_iter()}
    return jsonify(sensors), 200

@app.route("/sensor/get-topic/<sensor_id>", methods=["GET"])
def api_get_sensor_topic(sensor_id):
    """
    Get the topic assigned to a sensor.
    ---
    tags:
      - Sensors
    parameters:
      - name: sensor_id
        in: path
        required: true
        type: string
        description: The unique ID of the sensor
    responses:
      200:
        description: Sensor topic found
      404:
        description: Sensor not found
    """
    topic = r.get(sensor_id)
    if topic:
        return jsonify({"sensor_id": sensor_id, "topic": topic}), 200
    return jsonify({"error": "Sensor not found"}), 404

@app.route("/topic/create", methods=["POST"])
def api_create_topic():
    """
    Create a new Kafka topic.
    ---
    tags:
      - Topics
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - topic
          properties:
            topic:
              type: string
              description: The name of the Kafka topic
    responses:
      201:
        description: Topic successfully created
      400:
        description: Invalid input
    """
    data = request.json
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "topic name is required"}), 400

    subprocess.run(
        f"{KAFKA_BIN} --create --topic {topic} --bootstrap-server {KAFKA_SERVER} --partitions 3 --replication-factor 1",
        shell=True
    )
    return jsonify({"message": f"Topic {topic} created"}), 201

@app.route("/topic/delete/<topic>", methods=["DELETE"])
def api_delete_topic(topic):
    """
    Delete an existing Kafka topic.
    ---
    tags:
      - Topics
    parameters:
      - name: topic
        in: path
        required: true
        type: string
        description: The name of the Kafka topic to delete
    responses:
      200:
        description: Topic successfully deleted
    """
    subprocess.run(
        f"{KAFKA_BIN} --delete --topic {topic} --bootstrap-server {KAFKA_SERVER}",
        shell=True
    )
    return jsonify({"message": f"Topic {topic} deleted"}), 200

@app.route("/topic/list", methods=["GET"])
def api_list_topics():
    """
    Get all existing Kafka topics.
    ---
    tags:
      - Topics
    responses:
      200:
        description: List of topics
    """
    topics = subprocess.check_output(
        f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
        shell=True
    ).decode().split("\n")
    
    return jsonify({"topics": [topic for topic in topics if topic]}), 200

if __name__ == "__main__":
    config_lookup()  # Restore previous configurations
    app.run(host="0.0.0.0", port=5004, debug=True)
