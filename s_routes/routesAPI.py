from flask import Flask, jsonify, request
from flasgger import Swagger
import json
from datetime import datetime
import service_core as sc
import osrm_api as osrm

app = Flask(__name__)
Swagger(app)

@app.route("/v1/routes", methods=["POST"])
def create_route():
    """
    Creates a new route based on provided coordinates, mode, and optionally a truck ID.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            coordinates:
              type: array
              items:
                type: array
                items:
                  type: number
              example: [[40.6221, -8.6280], [40.6331, -8.6587], [40.6221, -8.6280]]
            mode:
              type: string
              enum: ["car", "walking"]
              example: "car"
            truck_id:
              type: string
              description: "Required only if mode is 'car'"
              example: "T123"
    responses:
      201:
        description: Route successfully created
      400:
        description: Invalid input
    """
    data = request.json

    if not data or "coordinates" not in data or "mode" not in data:
        return jsonify({"error": "Missing required fields: coordinates and mode"}), 400
    
    if data["mode"] not in ["car", "walking"]:
        return jsonify({"error": "Invalid mode. Accepted values: 'car', 'walking'"}), 400

    start, *waypoints, end = data["coordinates"]

    if data["mode"] == "car":
        if "truck_id" not in data:
            return jsonify({"error": "Missing truck_id for mode 'car'"}), 400
        route_result, status = osrm.calculate_routing_driving(start, waypoints, end)
    else:
        route_result, status = osrm.calculate_routing_walking(start, end)

    if status != 200:
        return jsonify(route_result), status

    route_result["route_id"] = f"r{int(datetime.now().timestamp())}"
    route_result["mode"] = data["mode"]
    route_result["created_at"] = str(datetime.today().date())

    if data["mode"] == "car":
        sc.create_route(route_result["route_id"], route_result["route_coordinates"], truck_id=data["truck_id"])

    return jsonify(route_result), 201

@app.route("/v1/routes", methods=["GET"])
def get_routes():
    """
    Retrieve all routes or filter by ID, date, or truck ID.
    ---
    parameters:
      - name: id
        in: query
        type: string
        required: false
      - name: day
        in: query
        type: string
        required: false
      - name: month
        in: query
        type: string
        required: false
      - name: year
        in: query
        type: string
        required: false
      - name: truck_id
        in: query
        type: string
        required: false
    responses:
      200:
        description: Route(s) found
      400:
        description: Invalid request
      404:
        description: No routes found
    """
    route_id = request.args.get("id")
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")
    truck_id = request.args.get("truck_id")

    if route_id:
        route = sc.get_route(route_id)
        return jsonify(route) if "error" not in route else (jsonify(route), 404)

    routes = sc.get_routes_history(day, month, year, truck_id)
    return jsonify(routes) if "error" not in routes else (jsonify(routes), 404)

@app.route("/v1/routes", methods=["DELETE"])
def delete_route():
    """
    Deletes a saved route based on the given ID.
    ---
    parameters:
      - name: id
        in: query
        type: string
        required: true
    responses:
      200:
        description: Route successfully deleted
      400:
        description: Missing route ID
      404:
        description: Route not found
    """
    route_id = request.args.get("id")
    if not route_id:
        return jsonify({"error": "Missing route ID"}), 400

    result = sc.delete_route(route_id)
    return jsonify(result) if "error" not in result else (jsonify(result), 404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
