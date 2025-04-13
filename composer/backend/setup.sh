#!/bin/bash

echo "🚀 A iniciar o backend FastAPI (usando .env)..."

# 1️⃣ Ativar ou criar o ambiente virtual
if [ -d "venv" ]; then
    echo "✅ Ambiente virtual já existe. A ativar..."
    source venv/bin/activate
else
    echo "🛠 A criar ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual criado e ativado!"
fi

# 2️⃣ Instalar dependências
if [ -f requirements.txt ]; then
    echo "📦 A instalar dependências..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt não encontrado. A instalar pacotes mínimos..."
    pip install fastapi uvicorn pymysql python-dotenv
fi

# 3️⃣ Iniciar MariaDB via Docker
echo "🐬 A iniciar o container 'waste-mariadb'..."
docker start waste-mariadb
if [ $? -eq 0 ]; then
    echo "✅ MariaDB iniciado!"
else
    echo "❌ Erro ao iniciar o MariaDB!"
    exit 1
fi

# 4️⃣ Esperar para garantir que a BD está pronta
sleep 5

# 🔚 Instruções para iniciar a bridge
echo ""
echo "🌉 Para iniciar a Kafka WebSocket Bridge, corre os seguintes comandos num novo terminal:"
echo "   source venv/bin/activate"
echo "   python3 kafka-ws-bridge_v2.py"
echo ""


# 5️⃣ Extrair host/port do config.py dinamicamente
echo "📦 A carregar configurações do config.py..."
HOST=$(python3 -c "import config; print(config.UVICORN_HOST)")
PORT=$(python3 -c "import config; print(config.UVICORN_PORT)")

# 6️⃣ Iniciar Uvicorn com os valores carregados
echo "⚡ A iniciar FastAPI em $HOST:$PORT..."
uvicorn main:app --host "$HOST" --port "$PORT" --reload
if [ $? -eq 0 ]; then
    echo "✅ FastAPI iniciado com sucesso!"
else
    echo "❌ Erro ao iniciar o FastAPI!"
    exit 1
fi

