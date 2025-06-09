
1. BUILD
```bash
docker build -t registry.deti/waste-app/posting-service:v2 .
```

2. PUSH
```bash
docker push registry.deti/waste-app/posting-service:v2
```

3. APPLY DEPLOYMENT
```bash
# ADD
kubectl apply -f k8s/ -n waste-app 

# DELETE
kubectl delete -f k8s/ -n waste-app 
```