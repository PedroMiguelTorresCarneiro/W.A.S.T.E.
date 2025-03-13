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
KAFKA_SERVER = "localhost:9092"

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Flask
app = Flask(__name__)
swagger = Swagger(app)  # Auto-generate Swagger docs

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

# ==============================
# 🚀 SENSOR ROUTES (v1/sensors)
# ==============================

@app.route("/v1/sensors", methods=["POST"])
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

@app.route("/v1/sensors", methods=["GET"])
def api_list_sensors(sensor_id=None):
    """
    Get all registered sensors and their topics. If a sensor ID is provided, return only that sensor.
    ---
    tags:
      - Sensors
    parameters:
      - name: sensor_id
        in: path
        required: false
        type: string
        description: The unique ID of the sensor (optional)
    responses:
      200:
        description: A list of registered sensors or a single sensor if an ID is provided
    """
    if sensor_id:
        topic = r.get(sensor_id)
        if topic:
            return jsonify({"sensor_id": sensor_id, "topic": topic}), 200
        return jsonify({"error": "Sensor not found"}), 404

    sensors = {key: value for key, value in r.scan_iter()}
    return jsonify(sensors), 200

@app.route("/v1/sensors", methods=["DELETE"])
def api_remove_sensors():
    """
    Remove one or multiple sensors from the system.
    ---
    tags:
      - Sensors
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            sensor_ids:
              type: array
              items:
                type: string
              description: A list of sensor IDs to remove
            all:
              type: boolean
              description: Set to true to remove all sensors
    responses:
      200:
        description: Sensors successfully removed
      400:
        description: Invalid input
      404:
        description: One or more sensors not found
    """
    data = request.json

    if data.get("all", False):  # If "all" is true, delete all sensors
        all_sensors = [key.decode() for key in r.keys("*")]
        if not all_sensors:
            return jsonify({"error": "No sensors found"}), 404

        for sensor_id in all_sensors:
            r.delete(sensor_id)

        return jsonify({"message": "All sensors removed"}), 200

    sensor_ids = data.get("sensor_ids", [])
    
    if not sensor_ids:
        return jsonify({"error": "Provide sensor_ids list or set 'all' to true"}), 400

    not_found = [sensor_id for sensor_id in sensor_ids if not r.exists(sensor_id)]
    
    if not_found:
        return jsonify({"error": "Some sensors not found", "not_found": not_found}), 404

    for sensor_id in sensor_ids:
        r.delete(sensor_id)

    return jsonify({"message": f"Sensors {sensor_ids} removed"}), 200

# ===========================
# 🔥 TOPIC ROUTES (v1/topic)
# ===========================

@app.route("/v1/topic", methods=["POST"])
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

@app.route("/v1/topic", methods=["GET"])
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

@app.route("/v1/topic", methods=["DELETE"])
def api_delete_topics():
    """
    Delete one or multiple Kafka topics.
    ---
    tags:
      - Topics
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            topic_names:
              type: array
              items:
                type: string
              description: A list of topics to remove
            all:
              type: boolean
              description: Set to true to remove all topics
    responses:
      200:
        description: Topics successfully deleted
      400:
        description: Invalid input
      404:
        description: One or more topics not found
    """
    data = request.json

    if data.get("all", False):  # If "all" is true, delete all topics
        all_topics = subprocess.check_output(
            f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
            shell=True
        ).decode().split("\n")

        all_topics = [topic for topic in all_topics if topic and topic != "__consumer_offsets"]

        if not all_topics:
            return jsonify({"error": "No topics found"}), 404

        for topic in all_topics:
            subprocess.run(
                f"{KAFKA_BIN} --delete --topic {topic} --bootstrap-server {KAFKA_SERVER}",
                shell=True
            )

        return jsonify({"message": "All topics removed"}), 200

    topic_names = data.get("topic_names", [])
    
    if not topic_names:
        return jsonify({"error": "Provide topic_names list or set 'all' to true"}), 400

    existing_topics = subprocess.check_output(
        f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
        shell=True
    ).decode().split("\n")

    not_found = [topic for topic in topic_names if topic not in existing_topics]
    
    if not_found:
        return jsonify({"error": "Some topics not found", "not_found": not_found}), 404

    for topic in topic_names:
        subprocess.run(
            f"{KAFKA_BIN} --delete --topic {topic} --bootstrap-server {KAFKA_SERVER}",
            shell=True
        )

    return jsonify({"message": f"Topics {topic_names} removed"}), 200

# =========================
# 🚀 APP STARTUP
# =========================
if __name__ == "__main__":
    config_lookup()  # Restore previous configurations
    app.run(host="0.0.0.0", port=5004, debug=True)
