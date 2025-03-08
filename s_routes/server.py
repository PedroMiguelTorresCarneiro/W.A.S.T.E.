from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import json
from datetime import datetime
import service_core as sc
import osrm_api as osrm

app = Flask(__name__)

# Configurar Swagger UI
SWAGGER_URL = "/routes-service"
API_URL = "/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Routes Service API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Endpoint para servir o ficheiro swagger.json
@app.route("/static/swagger.json")
def swagger_json():
    with open("swagger.json", "r") as file:
        return jsonify(json.load(file))

# Calcula uma nova rota
@app.route("/v1/routes/calculate", methods=["POST"])
def calculate_route():
    data = request.json

    if not data or "coordinates" not in data or "mode" not in data:
        return jsonify({"error": "Missing required fields: coordinates and mode"}), 400
    
    if data["mode"] not in ["car", "walking"]:
        return jsonify({"error": "Invalid mode. Accepted values: 'car', 'walking'"}), 400

    start, *waypoints, end = data["coordinates"]
    
    if data["mode"] == "car":
        route_result, status = osrm.calculate_routing_driving(start, waypoints, end)
    else:
        route_result, status = osrm.calculate_routing_walking(start, end)

    if status != 200:
        return jsonify(route_result), status

    route_result["route_id"] = f"r{int(datetime.now().timestamp())}"  # Generate unique route ID
    route_result["mode"] = data["mode"]
    route_result["created_at"] = str(datetime.today().date())

    # Apenas armazena no banco de dados se o modo for "car"
    if data["mode"] == "car":
        sc.create_route(route_result["route_id"], route_result["route_coordinates"], truck_id=data.get("truck_id"))

    return jsonify(route_result), 201

# Obtém detalhes de uma rota específica
@app.route("/v1/routes", methods=["GET"])
def get_route_details():
    route_id = request.args.get("id")

    if not route_id:
        return jsonify({"error": "Missing route ID"}), 400
    
    route = sc.get_route(route_id)
    
    if "error" in route:
        return jsonify(route), 404

    return jsonify(route), 200

# Lista todas as rotas com filtros opcionais
@app.route("/v1/routes/history", methods=["GET"])
def get_route_history():
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")
    truck_id = request.args.get("truck_id")

    routes = sc.get_routes_history(day, month, year, truck_id)

    if "error" in routes:
        return jsonify(routes), 404

    return jsonify(routes), 200

# Remove uma rota guardada
@app.route("/v1/routes", methods=["DELETE"])
def delete_route_endpoint():
    route_id = request.args.get("id")

    if not route_id:
        return jsonify({"error": "Missing route ID"}), 400

    result = sc.delete_route(route_id)
    
    if "error" in result:
        return jsonify(result), 404

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
