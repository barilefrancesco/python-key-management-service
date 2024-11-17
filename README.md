# Installation
```
docker build -t key-management-service .
docker run -p 8000:8000 key-management-service
```

# Create key
```
curl -X POST \
 http://localhost:8000/api/keys \
 -H "Content-Type: application/json" \
 -d '{"name": "test-key-1"}' | json_pp
```

# Keys list
```
curl http://localhost:8000/api/keys | json_pp
```
