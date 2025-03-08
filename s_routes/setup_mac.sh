#!/bin/bash

echo "🚀 Verificando ambiente virtual no macOS..."

# 1️⃣ Criar e ativar ambiente virtual
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

# 2️⃣ Instalar dependências
if [ -f requirements.txt ]; then
    echo "📦 Instalando dependências do requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Arquivo requirements.txt não encontrado. Instalando dependências básicas..."
    pip install flask flask-swagger-ui mariadb
fi

# 3️⃣ Verificar se MariaDB está instalado
echo "🔍 Verificando instalação do MariaDB..."
if ! command -v mariadb &> /dev/null
then
    echo "❌ MariaDB não está instalado. Instalando agora..."
    brew install mariadb
    echo "✅ MariaDB instalado com sucesso!"
fi

# 4️⃣ Iniciar MariaDB e configurar base de dados
echo "🔄 Iniciando serviço do MariaDB..."
brew services start mariadb

echo "✅ Configurando MariaDB..."
sudo mariadb -u root <<EOF
CREATE DATABASE IF NOT EXISTS routes_service;
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON routes_service.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "✅ Configuração concluída! Agora pode rodar o servidor com:"
echo "   python3 server.py"
