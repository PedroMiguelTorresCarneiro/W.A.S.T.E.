
docker build -t registry.deti/waste-app/kafka-ws-bridge:v5 .

docker push registry.deti/waste-app/kafka-ws-bridge:v5

kubectl apply -f k8s/ -n waste-app 