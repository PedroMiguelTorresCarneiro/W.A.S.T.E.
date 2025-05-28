import datetime
import requests
import json
from dotenv import load_dotenv
import os
from config import OSRM_BASE_URL
import traceback


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

# def calculate_routing_driving(start, waypoints, end):
#     """
#     Calculates an optimized driving route using OSRM, considering a start point, waypoints, and an endpoint.
    
#     Parameters:
#         start (tuple): The starting point as (latitude, longitude).
#         waypoints (list of tuples): Intermediate waypoints [(lat1, lon1), (lat2, lon2), ...].
#         end (tuple): The endpoint as (latitude, longitude).
    
#     Returns:
#         dict: A dictionary containing the distance (km), duration (min), and route coordinates.
#         int: HTTP status code (200 for success, 400/500 for errors).
#     """
#     if not start or not end:
#         return {"error": "Invalid start or end"}, 400
    
#     # OSRM base URL
#     base_url = f"{OSRM_BASE_URL}/trip/v1/driving/"
#     #base_url = f"{OSRM_BASE_URL}/route/v1/driving/"

#     # Merge coordinates into one sequence: Start -> Waypoints -> End
#     all_coordinates = [start] + waypoints + [end]
#     coords_str = ";".join([f"{lon},{lat}" for lat, lon in all_coordinates])
#     url = f"{base_url}{coords_str}?source=first&destination=last&overview=full&geometries=geojson"
#     # Debug: Print the request URL
#     print(f"OSRM Request URL: {url}")
    
#     try:
#         response = requests.get(url, timeout=5)
#         print(f"[DEBUG] OSRM status code: {response.status_code}")
#         print(f"[DEBUG] OSRM response text: {response.text}")
#     except Exception as e:
#         print("[EXCEPTION] Falha ao fazer request para OSRM")
#         print(f"[EXCEPTION] URL: {url}")
#         print(f"[EXCEPTION] Tipo: {type(e).__name__}")
#         print(f"[EXCEPTION] Erro: {str(e)}")
#         traceback.print_exc()
#         return {"error": "Falha ao comunicar com o serviço OSRM (exceção)"}, 500


#     try:
#         data = response.json()
#     except Exception as e:
#         print("[ERROR] OSRM returned non-JSON response")
#         print(response.text)
#         return {"error": "Invalid JSON from OSRM"}, 500

#     if "trips" not in data or not data["trips"]:
#         return {"error": "No route found"}, 404
    
#     trip_info = data["trips"][0]
#     route_coordinates = [(lat, lon) for lon, lat in trip_info["geometry"]["coordinates"]]  # Convert to (lat, lon) format
    
#     return {
#         "distance_km": trip_info["distance"] / 1000,
#         "duration_min": trip_info["duration"] / 60,
#         "route_coordinates": route_coordinates
#     }, 200

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

if __name__ == "__main__":
    start = (40.622177907562765, -8.628062888853071)
    waypoints = [(40.633100434754446, -8.658784977324297)]
    end = (40.622177907562765, -8.628062888853071)
    test_mode = "car"
    
    # Run route calculation for driving
    result, status_code = calculate_routing_driving(start, waypoints, end)
    #print(f"Status Code: {status_code}")
    
    if status_code == 200:
        print_route_info(result)
        print("\n")
        gpx_result, _ = generate_gpx(result["route_coordinates"])
        print(f"📂 GPX file generated: {gpx_result['path']}\n")
    
    # Run route calculation for walking
    walking_result, walking_status_code = calculate_routing_walking(start, waypoints[0])
    #print(f"\nWalking Route Status Code: {walking_status_code}")
    
    if walking_status_code == 200:
        print_route_info(walking_result)
        print("\n")
        gpx_result, _ = generate_gpx(walking_result["route_coordinates"])
        print(f"📂 GPX file generated for walking: {gpx_result['path']}\n")
