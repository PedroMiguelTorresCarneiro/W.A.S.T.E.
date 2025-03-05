#!/bin/bash

echo "Verificando ambiente virtual no macOS..."

# Verificar se a pasta venv já existe
if [ -d "venv" ]; then
    echo "Ambiente virtual já existe."
    echo "Ativando o ambiente virtual..."
    source venv/bin/activate
    echo "-> Ambiente virtual ativado!"
else
    echo "Criando novo ambiente virtual..."
    python3 -m venv venv
    echo "-> Ambiente virtual criado com sucesso!"

    # Ativar ambiente virtual
    source venv/bin/activate
    echo "-> Ambiente virtual ativado!"

    # Instalar dependências
    if [ -f requirements.txt ]; then
        echo "📦 Instalando dependências do requirements.txt..."
        pip install -r requirements.txt
    else
        echo "⚠️ Arquivo requirements.txt não encontrado. Instalando Flask apenas."
        pip install flask flask-swagger-ui
    fi
fi

echo "Configuração concluída!!! "
