from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer
import threading
import redis
import json
import logging
import re
import os
import signal


# ========================
# 🔧 Configurações Iniciais
# ========================
app = Flask(__name__)
swagger = Swagger(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

REDIS_HOST = "localhost"
REDIS_PORT = 6379
KAFKA_TOPIC = "iot_logs"
KAFKA_SERVER = "localhost:9092"
LOOKUP_FILE = "sensor_lookup.txt"

# ========================
# 📂 Redis
# ========================
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    print("✅ Redis conectado com sucesso.")
except redis.RedisError as e:
    print(f"❌ Erro ao conectar ao Redis: {e}")
    exit(1)

# ========================
# 🤖 Kafka ➞ WebSocket
# ========================
def safe_deserializer(msg):
    try:
        return json.loads(msg.decode('utf-8'))
    except Exception as e:
        print(f"❌ Erro ao decodificar mensagem Kafka: {e}")
        return {}

def kafka_router():
    print(f"📢 Subscrito no Kafka ({KAFKA_TOPIC})...")
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=safe_deserializer,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='iot-ws-router-group'
    )
    for msg in consumer:
        data = msg.value
        serial = data.get("serial")
        if not serial:
            print("⚠️ Mensagem sem serial ignorada.")
            continue
        topic = r.get(serial)
        if topic:
            socketio.emit(f"{topic}", data)
            print(f"📢 Emitido para tópico WebSocket '{topic}': {data}")
        else:
            print(f"⚠️ Sem topico para serial: {serial}")

# ========================
# 🚀 Start Thread
# ========================
kafka_thread = threading.Thread(target=kafka_router, daemon=True)
kafka_thread.start()

# ============================
# 🔐 AUTHENTICATION
# ============================

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response('Authentication required', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

# ==============================
# 🚀 SENSOR ROUTES (v2/sensors)
# ==============================

@app.route("/v2/sensors", methods=["POST"])
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
        examples:
          application/json:
            {"message": "Sensor temperature_sensor_1 added to topic temperature_readings"}
      400:
        description: Invalid input
        examples:
          application/json:
            {"error": "sensor_id and topic are required"}
      409:
        description: Sensor already exists
        examples:
          application/json:
            {"error": "Sensor temperature_sensor_1 already exists"}
      415:
        description: Unsupported media type
        examples:
          application/json:
            {"error": "Request must be JSON"}
      500:
        description: Server error
        examples:
          application/json:
            {"error": "Internal server error", "details": "Error details message"}
      503:
        description: Service unavailable
        examples:
          application/json:
            {"error": "Database error occurred"}
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
        
    data = request.json
    
    # Check for missing body
    if not data:
        return jsonify({"error": "Empty request body"}), 400
        
    sensor_id = data.get("sensor_id")
    topic = data.get("topic")

    # Validate required fields
    if not sensor_id or not topic:
        return jsonify({"error": "sensor_id and topic are required"}), 400
        
    # Validate format
    if not validate_sensor_id(sensor_id):
        return jsonify({"error": "Invalid sensor_id format. Use only alphanumeric characters, dots, underscores, and hyphens"}), 400
        
    if not validate_topic_name(topic):
        return jsonify({"error": "Invalid topic name. Use only alphanumeric characters, dots, underscores, and hyphens"}), 400

    try:
        # Check for duplicates
        if r.exists(sensor_id):
            return jsonify({"error": f"Sensor {sensor_id} already exists"}), 409
            
        r.set(sensor_id, topic)
        
        try:
            with open(LOOKUP_FILE, "a") as f:
                f.write(f"{sensor_id}:{topic}\n")
        except IOError as e:
            logger.error(f"Failed to write to lookup file: {str(e)}")
            # Continue even if file write fails

        logger.info(f"Sensor {sensor_id} added to topic {topic}")
        return jsonify({"message": f"Sensor {sensor_id} added to topic {topic}"}), 201
    except redis.RedisError as e:
        logger.error(f"Redis error during sensor creation: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 503

@app.route("/v2/sensors", methods=["GET"])
def api_list_sensors():
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
        examples:
          application/json:
            {
              "temperature_sensor_1": "temperature_readings",
              "humidity_sensor_2": "humidity_readings",
              "pressure_sensor_3": "pressure_readings"
            }
      404:
        description: Sensor not found
        examples:
          application/json:
            {"error": "Sensor not found"}
      500:
        description: Server error
        examples:
          application/json:
            {"error": "Internal server error", "details": "Error details message"}
      503:
        description: Service unavailable
        examples:
          application/json:
            {"error": "Database connection error"}
    """
    try:
        sensor_id = request.args.get("sensor_id")  # <--- buscar da query string, como ?sensor_id=xpto

        if sensor_id:
            topic = r.get(sensor_id)
            if topic:
                return jsonify({sensor_id: topic}), 200
            return jsonify({"error": "Sensor not found"}), 404

        keys = r.keys("*")
        sensors = {key: r.get(key) for key in keys}
        return jsonify(sensors), 200

    except redis.RedisError as e:
        logger.error(f"Redis error during sensor listing: {str(e)}")
        return jsonify({"error": "Database connection error"}), 503
    except Exception as e:
        logger.error(f"Unexpected error during sensor listing: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/v2/sensors", methods=["DELETE"])
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
          examples:
            multiple_sensors:
              value:
                {
                  "sensor_ids": ["temperature_sensor_1", "humidity_sensor_2"]
                }
            all_sensors:
              value:
                {
                  "all": true
                }
    responses:
      200:
        description: Sensors successfully removed
        examples:
          application/json:
            {
              "message": "Sensors removed: ['temperature_sensor_1', 'humidity_sensor_2']"
            }
      400:
        description: Invalid input
        examples:
          application/json:
            {"error": "Provide sensor_ids list or set 'all' to true"}
      404:
        description: One or more sensors not found
        examples:
          application/json:
            {
              "error": "None of the specified sensors found", 
              "not_found": ["unknown_sensor_1", "unknown_sensor_2"]
            }
      415:
        description: Unsupported media type
        examples:
          application/json:
            {"error": "Request must be JSON"}
      500:
        description: Server error
        examples:
          application/json:
            {"error": "Internal server error", "details": "Error details message"}
      503:
        description: Service unavailable
        examples:
          application/json:
            {"error": "Database error occurred"}
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
        
    data = request.json
    
    # Check for missing body
    if not data:
        return jsonify({"error": "Empty request body"}), 400

    try:
        if data.get("all", False):  # If "all" is true, delete all sensors
            try:
                all_sensors = [key for key in r.keys("*")]
                if not all_sensors:
                    return jsonify({"error": "No sensors found"}), 404

                for sensor_id in all_sensors:
                    r.delete(sensor_id)

                logger.info(f"All sensors removed (total: {len(all_sensors)})")
                return jsonify({"message": f"All sensors removed ({len(all_sensors)} total)"}), 200
            except redis.RedisError as e:
                logger.error(f"Redis error while removing all sensors: {str(e)}")
                return jsonify({"error": "Database error occurred"}), 503

        sensor_ids = data.get("sensor_ids", [])
        
        if not sensor_ids:
            return jsonify({"error": "Provide sensor_ids list or set 'all' to true"}), 400

        # Validate all sensor IDs
        invalid_ids = [sensor_id for sensor_id in sensor_ids if not validate_sensor_id(sensor_id)]
        if invalid_ids:
            return jsonify({"error": "Invalid sensor IDs", "invalid_ids": invalid_ids}), 400

        not_found = [sensor_id for sensor_id in sensor_ids if not r.exists(sensor_id)]
        
        if not_found and len(not_found) == len(sensor_ids):
            return jsonify({"error": "None of the specified sensors found", "not_found": not_found}), 404
        
        found_sensors = [s for s in sensor_ids if s not in not_found]
        for sensor_id in found_sensors:
            r.delete(sensor_id)

        result = {
            "message": f"Sensors removed: {found_sensors}"
        }
        
        if not_found:
            result["warning"] = "Some sensors were not found"
            result["not_found"] = not_found
            
        logger.info(f"Removed sensors: {found_sensors}")
        if not_found:
            logger.warning(f"Sensors not found: {not_found}")
            
        return jsonify(result), 200
    except redis.RedisError as e:
        logger.error(f"Redis error during sensor removal: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 503
    except Exception as e:
        logger.error(f"Unexpected error during sensor removal: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# ===========================
# 🔥 TOPIC ROUTES (v2/topic)
# ===========================

@app.route("/v2/topic", methods=["POST"])
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
          example:
            {
              "topic": "temperature_readings"
            }
    responses:
      201:
        description: Topic successfully created
        examples:
          application/json:
            {"message": "Topic temperature_readings created"}
      400:
        description: Invalid input
        examples:
          application/json:
            {"error": "topic name is required"}
      409:
        description: Topic already exists
        examples:
          application/json:
            {"error": "Topic temperature_readings already exists"}
      415:
        description: Unsupported media type
        examples:
          application/json:
            {"error": "Request must be JSON"}
      500:
        description: Server error
        examples:
          application/json:
            {
              "error": "Failed to create topic", 
              "details": "Error: not enough replicas available"
            }
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
        
    data = request.json
    
    # Check for missing body
    if not data:
        return jsonify({"error": "Empty request body"}), 400
        
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "topic name is required"}), 400
        
    if not validate_topic_name(topic):
        return jsonify({"error": "Invalid topic name. Use only alphanumeric characters, dots, underscores, and hyphens"}), 400

    try:
        # Check if topic already exists
        existing_topics = subprocess.check_output(
            f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
            shell=True, text=True
        ).split("\n")
        
        if topic in existing_topics:
            return jsonify({"error": f"Topic {topic} already exists"}), 409
            
        result = subprocess.run(
            f"{KAFKA_BIN} --create --topic {topic} --bootstrap-server {KAFKA_SERVER} --partitions 3 --replication-factor 1",
            shell=True, capture_output=True, text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to create topic {topic}: {result.stderr}")
            return jsonify({"error": f"Failed to create topic: {result.stderr.strip()}"}), 500
            
        logger.info(f"Topic {topic} created")
        return jsonify({"message": f"Topic {topic} created"}), 201
    except subprocess.SubprocessError as e:
        logger.error(f"Kafka command error: {str(e)}")
        return jsonify({"error": "Failed to communicate with Kafka", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error during topic creation: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/v2/topic", methods=["GET"])
def api_list_topics():
    """
    Get all existing Kafka topics.
    ---
    tags:
      - Topics
    responses:
      200:
        description: List of topics
        examples:
          application/json:
            {
              "topics": [
                "temperature_readings", 
                "humidity_readings", 
                "pressure_readings"
              ]
            }
      500:
        description: Server error
        examples:
          application/json:
            {
              "error": "Failed to communicate with Kafka",
              "details": "Error connecting to bootstrap servers"
            }
    """
    try:
        topics = subprocess.check_output(
            f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
            shell=True, text=True
        ).split("\n")
        
        return jsonify({"topics": [topic for topic in topics if topic]}), 200
    except subprocess.SubprocessError as e:
        logger.error(f"Kafka command error during topic listing: {str(e)}")
        return jsonify({"error": "Failed to communicate with Kafka", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error during topic listing: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/v2/topic", methods=["DELETE"])
#@requires_auth
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
          examples:
            multiple_topics:
              value:
                {
                  "topic_names": ["temperature_readings", "humidity_readings"]
                }
            all_topics:
              value:
                {
                  "all": true
                }
    responses:
      200:
        description: Topics successfully deleted
        examples:
          application/json:
            {
              "message": "Topics removed: ['temperature_readings', 'humidity_readings']"
            }
      207:
        description: Partial success (some topics deleted, some failed)
        examples:
          application/json:
            {
              "message": "Topics removed: ['temperature_readings']",
              "error": "Some topics could not be deleted",
              "failed_deletions": [
                {"topic": "humidity_readings", "error": "Topic is in use"}
              ]
            }
      400:
        description: Invalid input
        examples:
          application/json:
            {"error": "Provide topic_names list or set 'all' to true"}
      401:
        description: Authentication required
        examples:
          application/json:
            {"error": "Authentication required"}
      404:
        description: One or more topics not found
        examples:
          application/json:
            {
              "error": "None of the specified topics found", 
              "not_found": ["unknown_topic_1", "unknown_topic_2"]
            }
      415:
        description: Unsupported media type
        examples:
          application/json:
            {"error": "Request must be JSON"}
      500:
        description: Server error
        examples:
          application/json:
            {
              "error": "Failed to communicate with Kafka", 
              "details": "Connection refused"
            }
    """
    # Validate request format
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
        
    data = request.json
    
    # Check for missing body
    if not data:
        return jsonify({"error": "Empty request body"}), 400

    try:
        if data.get("all", False):  # If "all" is true, delete all topics
            try:
                all_topics = subprocess.check_output(
                    f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
                    shell=True, text=True
                ).split("\n")

                all_topics = [topic for topic in all_topics if topic and topic != "__consumer_offsets"]

                if not all_topics:
                    return jsonify({"error": "No topics found"}), 404

                successful_deletions = []
                failed_deletions = []
                
                for topic in all_topics:
                    try:
                        result = subprocess.run(
                            f"{KAFKA_BIN} --delete --topic {topic} --bootstrap-server {KAFKA_SERVER}",
                            shell=True, capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            successful_deletions.append(topic)
                        else:
                            failed_deletions.append({"topic": topic, "error": result.stderr.strip()})
                    except subprocess.SubprocessError as e:
                        failed_deletions.append({"topic": topic, "error": str(e)})

                response = {"message": f"Topics removed: {successful_deletions}"}
                
                if failed_deletions:
                    response["warning"] = "Some topics could not be deleted"
                    response["failed_deletions"] = failed_deletions
                    return jsonify(response), 207  # 207 Multi-Status
                
                logger.info(f"All topics removed (total: {len(successful_deletions)})")
                return jsonify(response), 200
            except subprocess.SubprocessError as e:
                logger.error(f"Kafka command error: {str(e)}")
                return jsonify({"error": "Failed to communicate with Kafka"}), 500

        topic_names = data.get("topic_names", [])
        
        if not topic_names:
            return jsonify({"error": "Provide topic_names list or set 'all' to true"}), 400

        # Validate all topic names
        invalid_topics = [topic for topic in topic_names if not validate_topic_name(topic)]
        if invalid_topics:
            return jsonify({"error": "Invalid topic names", "invalid_topics": invalid_topics}), 400

        # Get existing topics
        existing_topics = subprocess.check_output(
            f"{KAFKA_BIN} --list --bootstrap-server {KAFKA_SERVER}",
            shell=True, text=True
        ).split("\n")

        not_found = [topic for topic in topic_names if topic not in existing_topics]
        
        if not_found and len(not_found) == len(topic_names):
            return jsonify({"error": "None of the specified topics found", "not_found": not_found}), 404
        
        successful_deletions = []
        failed_deletions = []
        
        for topic in [t for t in topic_names if t not in not_found]:
            try:
                result = subprocess.run(
                    f"{KAFKA_BIN} --delete --topic {topic} --bootstrap-server {KAFKA_SERVER}",
                    shell=True, capture_output=True, text=True
                )
                if result.returncode == 0:
                    successful_deletions.append(topic)
                else:
                    failed_deletions.append({"topic": topic, "error": result.stderr.strip()})
            except subprocess.SubprocessError as e:
                failed_deletions.append({"topic": topic, "error": str(e)})

        response = {"message": f"Topics removed: {successful_deletions}"}
        
        if not_found:
            response["warning"] = "Some topics were not found"
            response["not_found"] = not_found
            
        if failed_deletions:
            response["error"] = "Some topics could not be deleted"
            response["failed_deletions"] = failed_deletions
            return jsonify(response), 207  # 207 Multi-Status
            
        logger.info(f"Topics removed: {successful_deletions}")
        if not_found:
            logger.warning(f"Topics not found: {not_found}")
            
        return jsonify(response), 200
    except subprocess.SubprocessError as e:
        logger.error(f"Kafka command error during topic deletion: {str(e)}")
        return jsonify({"error": "Failed to communicate with Kafka", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error during topic deletion: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


# =========================
# 🔒 ERROR HANDLERS
# =========================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found", "message": str(error)}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed", "message": str(error)}), 405

@app.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({"error": "Unsupported media type", "message": "Request must be valid JSON"}), 415

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({"error": "Rate limit exceeded", "message": str(error)}), 429

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "Internal server error", "details": str(e)}), 500

# ============================
# 📴 SIGNAL HANDLER
# ============================

def signal_handler(sig, frame):
    logger.info("Shutdown signal received, closing connections...")
    try:
        r.close()
    except:
        pass
    logger.info("All connections closed. Shutting down.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ========================
# 🚀 Run App
# ========================
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5004, debug=True)
