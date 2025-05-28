#!/bin/bash

echo "🚀 Verificando ambiente virtual no macOS..."

# 1️⃣ Criar e ativar ambiente virtual
if [ -d "venv" ]; then
    echo "✅ Ambiente virtual já existe."
else
    echo "🛠 Criando novo ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado!"
fi

echo "🔄 Ativando o ambiente virtual..."
source venv/bin/activate

# 2️⃣ Instalar dependências
if [ -f requirements.txt ]; then
    echo "📦 Instalando dependências do requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Arquivo requirements.txt não encontrado. Instalando dependências básicas..."
    pip install flask flasgger flask-cors flask-swagger-ui python-dotenv mariadb
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

echo "🔐 Lendo variáveis do ficheiro .env..."
export $(grep -v '^#' .env | xargs)

echo "✅ Configurando MariaDB com variáveis do .env..."
sudo mariadb -u root <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'$DB_HOST' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'$DB_HOST';
FLUSH PRIVILEGES;
EOF

echo ""
echo "✅ Configuração concluída!"
echo "💡 Servidor preparado para correr com:"
echo "   python3 routesAPI_v2.py"
echo ""