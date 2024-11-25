
# Key Management Service

A FastAPI application for managing API keys.

## Installation

1. Create `.env` file with `SEC_API_KEY` variable. Generate key with this terminal command:
```bash
openssl rand -hex 32
```

2. To build and run the service using Docker, follow these steps:
```bash
docker build -t key-management-service .
docker run -p 8000:8000 key-management-service
```
or with docker-compose:
```bash
docker compose up --build -d
```

The service will be available at `http://localhost:8000`

## Endpoints and Usage

### Create a Key
Use the following command to create a new API key:
```bash
curl -X POST \
  http://localhost:8000/api/keys \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secure-api-key" \
  -d '{"name": "test-key-1", "expires_at": "2024-12-31T23:59:59Z"}' | json_pp
```

### Get a Key by Name
Retrieve a list of all API keys using the command below:
```bash
curl -X GET \
  http://localhost:8000/api/keys?name=test-key-1 \
  -H "X-API-Key: your-secure-api-key" | json_pp
```
**Optional Query Parameter:**

-   `name`: Filter keys by name.


### Delete a Key

To delete a specific API key by its ID:
```bash
curl -X DELETE \
  http://localhost:8000/api/keys/1 \
  -H "X-API-Key: your-secure-api-key" | json_pp
```

## Development

### Environment Variables

-   `DATABASE_URL`: Database connection URL (e.g., `sqlite:///./test.db`).

### Dependencies

-   **FastAPI:** The main framework.
-   **SQLAlchemy:** ORM for database management.
-   **Uvicorn:** ASGI server to run the application.

To modify or extend the service, edit the files in the `app/` directory.

## License

This project is licensed under the MIT License.
