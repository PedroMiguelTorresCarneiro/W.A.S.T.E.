from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import json

app = Flask(__name__)

# Configurar Swagger UI
SWAGGER_URL = "/firebase-auth"
API_URL = "/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Firebase-auth API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Endpoint para servir o ficheiro swagger.json
@app.route("/static/swagger.json")
def swagger_json():
    with open("swagger.json", "r") as file:
        return jsonify(json.load(file))

# Endpoint para registar um utilizador
@app.route("/v1/auth/register", methods=["POST"])
def register():
    data = request.json
    
    # Validação de dados
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    if "email" in data and "password" in data:
        return jsonify({
            "message": "User registered successfully",
            "user_id": "uid123",
            "email": data["email"],
            "role": "admin" if data.get("role_code") == "ADMIN123" else "user"
        }), 201
    
    elif "oauth_provider" in data and "token" in data:
        return jsonify({
            "message": "User registered with OAuth",
            "user_id": "uid123",
            "provider": data["oauth_provider"]
        }), 201
    
    return jsonify({"error": "Invalid request data"}), 400

# Endpoint para login
@app.route("/v1/auth/login", methods=["POST"])
def login():
    data = request.json
    
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    if "email" in data and "password" in data:
        return jsonify({
            "message": "Login successful",
            "user_id": "uid123",
            "email": data["email"],
            "role": "user"
        }), 200

    elif "oauth_provider" in data and "token" in data:
        return jsonify({
            "message": "Login successful via OAuth",
            "user_id": "uid123",
            "provider": data["oauth_provider"]
        }), 200

    return jsonify({"error": "Invalid request data"}), 400

# Endpoint para obter informações de um utilizador
@app.route("/v1/auth/user/<user_id>", methods=["GET"])
def get_user(user_id):
    if user_id == "uid123":
        return jsonify({
            "user_id": user_id,
            "email": "user@example.com",
            "role": "admin"
        }), 200
    return jsonify({"error": "User not found"}), 404

# Endpoint para verificar um token JWT (simulação)
@app.route("/v1/auth/verify-token", methods=["GET"])
def verify_token():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing Authorization header"}), 401

    if token == "Bearer valid_token":
        return jsonify({
            "message": "Token is valid",
            "user_id": "uid123",
            "role": "user"
        }), 200

    return jsonify({"error": "Invalid or expired token"}), 401


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
