import requests
import traceback
import datetime
import os

from flask import Flask, jsonify, request
from flasgger import Swagger
import json
from datetime import datetime
import service_core as sc
import osrm_api as osrm
from flask_cors import CORS
from config import FLASK_PORT, FLASK_DEBUG, FLASK_HOST, OSRM_BASE_URL

def calculate_routing_driving(start, waypoints, end):
    """
    Calculates an optimized driving route using OSRM, considering a start point, waypoints, and an endpoint.
    """
    if not start or not end:
        return {"error": "Invalid start or end"}, 400

    # OSRM base URL
    base_url = f"{OSRM_BASE_URL}/trip/v1/driving/"

    # Merge coordinates into one sequence: Start -> Waypoints -> End
    all_coordinates = [start] + waypoints + [end]
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in all_coordinates])
    url = f"{base_url}{coords_str}?source=first&destination=last&overview=full&geometries=geojson"

    print(f"[DEBUG] OSRM Request URL: {url}")

    try:
        response = requests.get(url, timeout=5)
        response_text = response.text
        print(f"[DEBUG] OSRM status code: {response.status_code}")
    except Exception as e:
        print("[EXCEPTION] Falha ao fazer request para OSRM")
        print(f"[EXCEPTION] URL: {url}")
        print(f"[EXCEPTION] Tipo: {type(e).__name__}")
        print(f"[EXCEPTION] Erro: {str(e)}")
        traceback.print_exc()
        return {"error": "Falha ao comunicar com o serviço OSRM (exceção)"}, 500

    if response.status_code != 200:
        print(f"[ERROR] OSRM response status: {response.status_code}")
        print(f"[ERROR] OSRM response text: {response_text}")
        return {"error": f"Falha ao comunicar com o serviço OSRM. Código: {response.status_code}"}, 503

    try:
        data = response.json()
    except Exception as e:
        print("[ERROR] OSRM returned non-JSON response")
        print(f"[RAW RESPONSE] {response_text}")
        print(f"[EXCEPTION] {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return {"error": "Invalid JSON from OSRM"}, 500

    if "trips" not in data or not data["trips"]:
        print("[ERROR] OSRM response has no 'trips'")
        print(data)
        return {"error": "No route found"}, 404

    trip_info = data["trips"][0]
    if "geometry" not in trip_info or not trip_info["geometry"]:
        print("[ERROR] 'geometry' missing in trip_info")
        print(trip_info)
        return {"error": "Invalid geometry data from OSRM"}, 500

    route_coordinates = [(lat, lon) for lon, lat in trip_info["geometry"]["coordinates"]]

    return {
        "distance_km": trip_info["distance"] / 1000,
        "duration_min": trip_info["duration"] / 60,
        "route_coordinates": route_coordinates
    }, 200

def calculate_routing_walking(start, end):
    """
    Calculates a walking route between a start and an endpoint using OSRM.
    
    Parameters:
        start (tuple): The starting point as (latitude, longitude).
        end (tuple): The endpoint as (latitude, longitude).
    
    Returns:
        dict: A dictionary containing the distance (km), duration (min), and route coordinates.
        int: HTTP status code (200 for success, 400/500 for errors).
    """
    if not start or not end:
        return {"error": "Invalid start or end"}, 400
    
    # OSRM base URL
    base_url = f"{OSRM_BASE_URL}/route/v1/foot/"
    
    coords_str = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    url = f"{base_url}{coords_str}?overview=full&geometries=geojson"
    
    # Debug: Print the request URL
    #print(f"OSRM Request URL: {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": f"Failed to get route from OSRM. Status Code: {response.status_code}"}, 500
    
    data = response.json()
    if "routes" not in data or not data["routes"]:
        return {"error": "No route found"}, 404
    
    route_info = data["routes"][0]
    route_coordinates = [(lat, lon) for lon, lat in route_info["geometry"]["coordinates"]]  # Convert to (lat, lon) format
    
    return {
        "distance_km": route_info["distance"] / 1000,
        "duration_min": route_info["duration"] / 60,
        "route_coordinates": route_coordinates
    }, 200

def generate_gpx(coordinates):
    """
    Generates a GPX file from a list of coordinates to be used in GPS applications.
    
    Parameters:
        coordinates (list of tuples): List of (latitude, longitude) points defining the route.
    
    Returns:
        dict: A dictionary containing the message, filename, and file path.
    """
    gpx_template = """
    <gpx version="1.1" creator="RoutesService">
        <trk>
            <name>OSRM Route</name>
            <trkseg>
                {points}
            </trkseg>
        </trk>
    </gpx>
    """
    
    points = "\n".join([f'<trkpt lat="{lat}" lon="{lon}" />' for lat, lon in coordinates])
    gpx_content = gpx_template.replace("{points}", points)
    
    filename = f"osrm_route_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.gpx"
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, "w") as gpx_file:
        gpx_file.write(gpx_content)
    
    return {"message": "GPX file generated", "filename": filename, "path": filepath}, 200

def print_route_info(route_result):
    """
    Prints the route information in a structured format.
    
    Parameters:
        route_result (dict): Dictionary containing distance, duration, and route coordinates.
    """
    print("\nRoute Information:")
    print(f"Distance (km):\t{route_result['distance_km']:.4f}")
    print(f"Duration (min):\t{route_result['duration_min']:.2f}")
    print("Route Coordinates:")
    print(", ".join([f"({lat}, {lon})" for lat, lon in route_result["route_coordinates"]]))

app = Flask(__name__)

swagger = Swagger(app, config={
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/v2/routes/apidocs/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/v2/routes/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/v2/routes/apidocs/"
})



CORS(app)  # Enable CORS for all routes

@app.route("/v2/routes", methods=["POST"])
def create_route():
    """
    Cria uma nova rota com base nas coordenadas, modo de transporte e opcionalmente um ID de caminhão.
    ---
    tags:
      - routes
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - coordinates
            - mode
          properties:
            coordinates:
              type: array
              description: Array de pares de coordenadas [latitude, longitude]. Mínimo de 2 pontos (origem e destino).
              items:
                type: array
                items:
                  type: number
                  format: float
                minItems: 2
                maxItems: 2
              example: [[40.6221, -8.6280], [40.6331, -8.6587], [40.6221, -8.6280]]
              minItems: 2
            mode:
              type: string
              enum: ["car", "walking"]
              description: Modo de transporte da rota
              example: "car"
            truck_id:
              type: string
              description: "ID do caminhão (obrigatório apenas se mode for 'car')"
              example: "T123"
    responses:
      201:
        description: Rota criada com sucesso
        schema:
          type: object
          properties:
            route_id:
              type: string
              description: ID único da rota
              example: "r1647852963"
            mode:
              type: string
              description: Modo de transporte utilizado
              example: "car"
            distance_km:
              type: number
              format: float
              description: Distância total da rota (km)
              example: 3.5
            duration_min:
              type: number
              format: float
              description: Duração estimada da rota (min)
              example: 30
            route_coordinates:
              type: array
              description: Coordenadas completas da rota
              example: [[40.6221, -8.6280], [40.6331, -8.6587], [40.6221, -8.6280]]
            created_at:
              type: string
              format: date
              description: Data de criação da rota
              example: "2024-12-01"
      400:
        description: Entrada inválida
        schema:
          type: object
          properties:
            error:
              type: string
              description: Descrição do erro
          examples:
            missing_fields:
              error: "Campos obrigatórios ausentes: coordinates e mode são necessários"
            invalid_coordinates:
              error: "Formato inválido de coordenadas. Cada coordenada deve ser um par [latitude, longitude]"
            insufficient_coordinates:
              error: "São necessárias no mínimo duas coordenadas para criar uma rota"
            invalid_mode:
              error: "Modo inválido. Valores aceitos: 'car', 'walking'"
            missing_truck_id:
              error: "ID do caminhão (truck_id) obrigatório para o modo 'car'"
      404:
        description: Rota não encontrada
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Nenhuma rota encontrada entre os pontos fornecidos. Verifique as coordenadas"
      503:
        description: Serviço indisponível
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Falha ao comunicar com o serviço OSRM. Tente novamente mais tarde"
      500:
        description: Erro interno do servidor
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Rota calculada, mas não pôde ser salva"
    """
    data = request.json

    if not data:
        return jsonify({"error": "Corpo da requisição vazio ou formato JSON inválido"}), 400
        
    if "coordinates" not in data or "mode" not in data:
        return jsonify({"error": "Campos obrigatórios ausentes: coordinates e mode são necessários"}), 400
    
    # Validação de formato das coordenadas
    try:
        if not all(len(coord) == 2 and all(isinstance(val, (int, float)) for val in coord) for coord in data["coordinates"]):
            return jsonify({"error": "Formato inválido de coordenadas. Cada coordenada deve ser um par [latitude, longitude]"}), 400
            
        if len(data["coordinates"]) < 2:
            return jsonify({"error": "São necessárias no mínimo duas coordenadas para criar uma rota"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Formato inválido de coordenadas. Verifique a estrutura JSON"}), 400
    
    if data["mode"] not in ["car", "walking"]:
        return jsonify({"error": "Modo inválido. Valores aceitos: 'car', 'walking'"}), 400

    start, *waypoints, end = data["coordinates"]

    if data["mode"] == "car":
        if "truck_id" not in data:
            return jsonify({"error": "ID do caminhão (truck_id) obrigatório para o modo 'car'"}), 400
        route_result, status = calculate_routing_driving(start, waypoints, end)
        print(f"[DEBUG] OSRM status: {status}")
        print(f"[DEBUG] OSRM result: {route_result}")
    else:
        route_result, status = calculate_routing_walking(start, end)
        print(f"[DEBUG] OSRM status: {status}")
        print(f"[DEBUG] OSRM result: {route_result}") 

    if status != 200:
        if status == 500:
            return jsonify({"error": "Falha ao comunicar com o serviço OSRM. Tente novamente mais tarde"}), 503
        elif status == 404:
            return jsonify({"error": "Nenhuma rota encontrada entre os pontos fornecidos. Verifique as coordenadas"}), 404
        else:
            return jsonify(route_result), status

    route_result["route_id"] = f"r{int(datetime.now().timestamp())}"
    route_result["mode"] = data["mode"]
    route_result["created_at"] = str(datetime.today().date())

    if data["mode"] == "car":
      db_result = sc.create_route(
          route_result["route_id"],
          route_result["route_coordinates"],
          truck_id=data["truck_id"],
          distance_km=route_result.get("distance_km"),
          duration_min=route_result.get("duration_min")
      )
      if "error" in db_result:
          return jsonify({"error": f"Rota calculada, mas não pôde ser salva: {db_result['error']}"}), 500

    return jsonify(route_result), 201

@app.route("/v2/routes", methods=["GET"])
def get_routes():
    """
    Recupera todas as rotas ou filtra por ID, data ou ID do caminhão.
    ---
    tags:
      - routes
    parameters:
      - name: id
        in: query
        type: string
        required: false
        description: ID único da rota
      - name: day
        in: query
        type: integer
        required: false
        description: Dia da criação da rota (1-31)
        minimum: 1
        maximum: 31
      - name: month
        in: query
        type: integer
        required: false
        description: Mês da criação da rota (1-12)
        minimum: 1
        maximum: 12
      - name: year
        in: query
        type: integer
        required: false
        description: Ano da criação da rota
        minimum: 2000
      - name: truck_id
        in: query
        type: string
        required: false
        description: ID do caminhão para filtrar rotas
    responses:
      200:
        description: Rota(s) encontrada(s)
        schema:
          type: array
          items:
            type: object
            properties:
              route_id:
                type: string
              coordinates:
                type: array
                items:
                  type: array
                  items:
                    type: number
              day:
                type: integer
              month:
                type: integer
              year:
                type: integer
              truck_id:
                type: string
              distance_km:
                type: number
                format: float
                example: 3.5
              duration_min:
                type: number
                format: float
                example: 25.2
      400:
        description: Parâmetros de consulta inválidos
        schema:
          type: object
          properties:
            error:
              type: string
          examples:
            invalid_day:
              error: "Dia inválido. Deve estar entre 1 e 31"
            invalid_month:
              error: "Mês inválido. Deve estar entre 1 e 12"
            invalid_year:
              error: "Ano inválido. Deve estar entre 2000 e 2025"
      404:
        description: Nenhuma rota encontrada
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Nenhuma rota encontrada com os critérios: dia=1 e mês=12 e ano=2024"
      503:
        description: Serviço indisponível
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Falha na conexão com o banco de dados. Tente novamente mais tarde"
    """
    route_id = request.args.get("id")
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")
    truck_id = request.args.get("truck_id")
    
    # Validar formatos de data se fornecidos
    if day:
        try:
            day = int(day)
            if day < 1 or day > 31:
                return jsonify({"error": "Dia inválido. Deve estar entre 1 e 31"}), 400
        except ValueError:
            return jsonify({"error": "Formato de dia inválido. Deve ser um número inteiro"}), 400
            
    if month:
        try:
            month = int(month)
            if month < 1 or month > 12:
                return jsonify({"error": "Mês inválido. Deve estar entre 1 e 12"}), 400
        except ValueError:
            return jsonify({"error": "Formato de mês inválido. Deve ser um número inteiro"}), 400
            
    if year:
        try:
            year = int(year)
            current_year = datetime.now().year
            if year < 2000 or year > current_year:
                return jsonify({"error": f"Ano inválido. Deve estar entre 2000 e {current_year}"}), 400
        except ValueError:
            return jsonify({"error": "Formato de ano inválido. Deve ser um número inteiro"}), 400

    if route_id:
        route = sc.get_route(route_id)
        if "error" in route:
            if route["error"] == "Route not found":
                return jsonify({"error": f"Rota com ID '{route_id}' não encontrada"}), 404
            elif route["error"] == "Database connection failed":
                return jsonify({"error": "Falha na conexão com o banco de dados. Tente novamente mais tarde"}), 503
            else:
                return jsonify(route), 500
        return jsonify(route)

    routes = sc.get_routes_history(day, month, year, truck_id)
    if "error" in routes:
        if routes["error"] == "No routes found":
            filter_desc = []
            if day: filter_desc.append(f"dia={day}")
            if month: filter_desc.append(f"mês={month}")
            if year: filter_desc.append(f"ano={year}")
            if truck_id: filter_desc.append(f"truck_id={truck_id}")
            
            filter_text = " e ".join(filter_desc) if filter_desc else "sem filtros"
            return jsonify({"error": f"Nenhuma rota encontrada com os critérios: {filter_text}"}), 404
        elif routes["error"] == "Database connection failed":
            return jsonify({"error": "Falha na conexão com o banco de dados. Tente novamente mais tarde"}), 503
        else:
            return jsonify(routes), 500
    return jsonify(routes)

@app.route("/v2/routes", methods=["DELETE"])
def delete_route():
    """
    Exclui uma rota salva com base no ID fornecido.
    ---
    tags:
      - routes
    parameters:
      - name: id
        in: query
        type: string
        required: true
        description: ID da rota a ser excluída
    responses:
      200:
        description: Rota excluída com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Rota 'r1647852963' excluída com sucesso"
      400:
        description: ID da rota ausente
        schema:
          type: object
          properties:
            error:
              type: string
              example: "ID da rota é obrigatório"
      404:
        description: Rota não encontrada
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Rota com ID 'r1647852963' não encontrada"
      503:
        description: Serviço indisponível
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Falha na conexão com o banco de dados. Tente novamente mais tarde"
      500:
        description: Erro interno do servidor
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Falha ao excluir a rota: erro no banco de dados"
    """
    route_id = request.args.get("id")
    if not route_id:
        return jsonify({"error": "ID da rota é obrigatório"}), 400

    result = sc.delete_route(route_id)
    if "error" in result:
        if result["error"] == "Route not found":
            return jsonify({"error": f"Rota com ID '{route_id}' não encontrada"}), 404
        elif result["error"] == "Database connection failed":
            return jsonify({"error": "Falha na conexão com o banco de dados. Tente novamente mais tarde"}), 503
        else:
            return jsonify({"error": f"Falha ao excluir a rota: {result['error']}"}), 500
    return jsonify({"message": f"Rota '{route_id}' excluída com sucesso"})

if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)