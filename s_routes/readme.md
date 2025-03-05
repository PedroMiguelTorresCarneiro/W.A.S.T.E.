# Route Service

This service allows calculating routes based on coordinates, storing them, and retrieving them.

## 📌 Environment Setup

1. **Create and activate the virtual environment**:
   - **macOS/Linux**:
     ```bash
     chmod +x setup_mac.sh  # Only the first time
     ./setup_mac.sh
     ```
   - **Linux**:
     ```bash
     chmod +x setup_linux.sh  # Only the first time
     ./setup_linux.sh
     ```

2. **Install dependencies** (if the script does not do so automatically):
   ```bash
   pip install -r requirements.txt
   ```

---
<br>
<br>
<br>

## 📌 How to Run the Server

To start the Flask server, simply run:
```bash
python server.py
```

---
<br>
<br>
<br>

## 📌 Access the API Documentation

After starting the server, the Swagger UI documentation will be available at:
```
http://localhost:5002/routes-service/
```

Here you can test the endpoints interactively.