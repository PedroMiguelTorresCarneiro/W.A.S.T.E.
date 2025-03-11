#!/bin/bash

echo "Setting up Kafka Wrapper Service on macOS..."

# 1️⃣ Create and Activate Virtual Environment
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    echo "Activating the virtual environment..."
    source venv/bin/activate
else
    echo "🛠 Creating a new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated!"
fi

# 2️⃣ Install Dependencies
if [ -f requirements.txt ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Installing required packages manually..."
    pip install flask flasgger redis subprocess
fi

# 3️⃣ Check and Install Redis
echo "Checking if Redis is installed..."
if ! command -v redis-server &> /dev/null
then
    echo "Redis is not installed. Installing now..."
    brew install redis
    echo "Redis installed successfully!"
fi

# 4️⃣ Start Redis Service
echo "Starting Redis service..."
brew services start redis

# 5️⃣ Check and Install Kafka & Zookeeper
echo "Checking if Kafka is installed..."
if ! command -v kafka-server-start &> /dev/null
then
    echo "Kafka is not installed. Installing now..."
    brew install kafka
    echo "Kafka installed successfully!"
fi

echo "Checking if Zookeeper is installed..."
if ! command -v zookeeper-server-start &> /dev/null
then
    echo "Zookeeper is not installed. Installing now..."
    brew install zookeeper
    echo "Zookeeper installed successfully!"
fi

# 6️⃣ Start Kafka & Zookeeper Services
echo "Starting Zookeeper..."
brew services start zookeeper
sleep 5  # Allow Zookeeper some time to start

echo "Starting Kafka..."
brew services start kafka

# 7️⃣ Display Final Instructions
echo "Setup complete!"
echo "To run the Kafka Wrapper service, use:"
echo "   source venv/bin/activate && python3 binAPI.py"
echo "To see the API documentation, visit http://localhost:5004/apidocs/"
