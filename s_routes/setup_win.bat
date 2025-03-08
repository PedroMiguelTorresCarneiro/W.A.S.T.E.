@echo off
echo 🚀 Verificando ambiente virtual no Windows...

:: 1️⃣ Criar e ativar ambiente virtual
if exist venv (
    echo ✅ Ambiente virtual já existe.
    echo 🔄 Ativando o ambiente virtual...
    call venv\Scripts\activate
) else (
    echo 🛠 Criando novo ambiente virtual...
    python -m venv venv
    call venv\Scripts\activate
    echo ✅ Ambiente virtual criado e ativado!
)

:: 2️⃣ Instalar dependências
if exist requirements.txt (
    echo 📦 Instalando dependências do requirements.txt...
    pip install -r requirements.txt
) else (
    echo ⚠️ Arquivo requirements.txt não encontrado. Instalando dependências básicas...
    pip install flask flask-swagger-ui mariadb
)

:: 3️⃣ Verificar se MariaDB está instalado
echo 🔍 Verificando instalação do MariaDB...
where mariadb >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ MariaDB não está instalado. Por favor, instale manualmente do site oficial:
    echo https://mariadb.org/download/
    exit /b
)

:: 4️⃣ Iniciar MariaDB e configurar base de dados
echo 🔄 Iniciando serviço do MariaDB...
net start MariaDB

echo ✅ Configurando MariaDB...
mariadb -u root -e "CREATE DATABASE IF NOT EXISTS routes_service;
CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON routes_service.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;"

echo ✅ Configuração concluída! Agora pode rodar o servidor com:
echo    python server.py
