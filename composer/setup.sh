#!/bin/bash

# Iniciar o container Docker
echo "A iniciar o container waste-mariadb..."
docker start waste-mariadb

# Verificar se o container foi iniciado com sucesso
if [ $? -eq 0 ]; then
    echo "Container iniciado com sucesso."
else
    echo "Erro ao iniciar o container."
    exit 1
fi

# Esperar alguns segundos para garantir que o serviço está pronto
sleep 5

# Iniciar o servidor FastAPI com uvicorn
echo "A iniciar o servidor FastAPI..."
uvicorn main:app --reload