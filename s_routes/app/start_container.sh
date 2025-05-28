#!/bin/bash

docker compose down         # NÃO usa -v (mantém a base de dados!)

echo "A construir as imagens..."
docker compose build

echo "A iniciar os serviços..."
docker compose up -d

echo "Serviços UP!!!"
echo "Documentação -> http://localhost:5002/apidocs"
