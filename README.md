# Test di creazione key

curl -X POST \
 http://localhost:8000/api/keys \
 -H "Content-Type: application/json" \
 -d '{"name": "test-key-1"}' | json_pp

# Lista delle key

curl http://localhost:8000/api/keys | json_pp
