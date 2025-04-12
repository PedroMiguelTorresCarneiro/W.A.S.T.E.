#!/bin/bash

echo "🚀 Setup do serviço s_binMonitoring no macOS..."

# 1️⃣ Carregar variáveis do .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Variáveis do .env carregadas com sucesso."
else
    echo "⚠️ Ficheiro .env não encontrado. Algumas variáveis podem não estar definidas!"
fi

# 2️⃣ Criar e ativar ambiente virtual
if [ -d "venv" ]; then
    echo "✅ Ambiente virtual já existe."
    echo "🔄 Ativando o ambiente virtual..."
    source venv/bin/activate
else
    echo "🛠 Criando novo ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Ambiente virtual criado e ativado!"
fi

# 3️⃣ Instalar dependências
if [ -f requirements.txt ]; then
    echo "📦 Instalando dependências do requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Arquivo requirements.txt não encontrado. Instalando dependências mínimas..."
    pip install flask flasgger redis kafka-python python-dotenv flask-cors
fi

# 4️⃣ Verificar instalação do Redis
echo "🔍 Verificando Redis..."
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis não encontrado. Instalando via brew..."
    brew install redis
    echo "✅ Redis instalado!"
fi

# 5️⃣ Iniciar Redis
echo "🔄 Iniciando Redis..."
brew services start redis

# 6️⃣ Verificar Kafka
echo "🔍 Verificando Kafka..."
if ! command -v kafka-server-start &> /dev/null; then
    echo "❌ Kafka não encontrado. Instalando via brew..."
    brew install kafka
    echo "✅ Kafka instalado!"
fi

# 7️⃣ Verificar Zookeeper
echo "🔍 Verificando Zookeeper..."
if ! command -v zookeeper-server-start &> /dev/null; then
    echo "❌ Zookeeper não encontrado. Instalando via brew..."
    brew install zookeeper
    echo "✅ Zookeeper instalado!"
fi

# 8️⃣ Iniciar serviços Kafka e Zookeeper
echo "🔄 Iniciando Zookeeper..."
brew services start zookeeper
sleep 5

echo "🔄 Iniciando Kafka..."
brew services start kafka

# 9️⃣ Mensagem final
echo "✅ Setup concluído com sucesso!"
echo ""
echo "▶️ Para correr o serviço:"
echo "   source venv/bin/activate && python3 binAPI.py"
echo ""