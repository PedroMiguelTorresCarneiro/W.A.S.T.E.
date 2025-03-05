from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import json
from datetime import datetime

app = Flask(__name__)

# Simulação de base de dados de rotas
routes_db = {
    "r123": {
        "route_id": "r123",
        "distance_km": 15.2,
        "fuel_liters": 2.5,
        "created_at": "2025-03-05",
        "mode": "car",
        "coordinates": [[40.7128, -74.0060], [34.0522, -118.2437]]
    }
}

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

    route_id = f"r{len(routes_db) + 1}"
    new_route = {
        "route_id": route_id,
        "distance_km": 10.5,  # Simulação
        "fuel_liters": 3.2 if data["mode"] == "car" else 0,
        "created_at": str(datetime.today().date()),
        "mode": data["mode"],
        "coordinates": data["coordinates"]
    }

    routes_db[route_id] = new_route

    return jsonify(new_route), 201

# Obtém detalhes de uma rota específica
@app.route("/v1/routes", methods=["GET"])
def get_route():
    route_id = request.args.get("id")

    if not route_id:
        return jsonify({"error": "Missing route ID"}), 400
    
    route = routes_db.get(route_id)
    
    if not route:
        return jsonify({"error": "Route not found"}), 404

    return jsonify(route), 200

# Lista todas as rotas com filtros opcionais
@app.route("/v1/routes/history", methods=["GET"])
def get_route_history():
    day = request.args.get("day")
    month = request.args.get("month")
    truck_id = request.args.get("truck_id")

    filtered_routes = list(routes_db.values())

    if day:
        filtered_routes = [r for r in filtered_routes if r["created_at"].split("-")[2] == day]

    if month:
        filtered_routes = [r for r in filtered_routes if r["created_at"].split("-")[1] == month]

    if truck_id:
        # Simulação: Nenhuma lógica de truck_id implementada
        filtered_routes = [r for r in filtered_routes if r.get("truck_id") == truck_id]

    if not filtered_routes:
        return jsonify({"error": "No routes found for the given filters"}), 404

    return jsonify(filtered_routes), 200

# Remove uma rota guardada
@app.route("/v1/routes", methods=["DELETE"])
def delete_route():
    route_id = request.args.get("id")

    if not route_id:
        return jsonify({"error": "Missing route ID"}), 400

    if route_id in routes_db:
        del routes_db[route_id]
        return jsonify({"message": "Route deleted successfully"}), 200

    return jsonify({"error": "Route not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
