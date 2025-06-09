
docker build -t registry.deti/waste-app/api:v3 .

docker push registry.deti/waste-app/api:v3


kubectl apply -f k8s/ -n waste-app 