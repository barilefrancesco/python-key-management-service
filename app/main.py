from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
import secrets
from dotenv import load_dotenv
import logging

load_dotenv()  # Load environment variables from .env file

from app.models import Base, APIKey
from app.database import SessionLocal, engine
from app.schemas import APIKeyCreate, APIKeyResponse

# Configure logging
logging.basicConfig(filename='/kms/data/app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Key Management Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware to log each request
@app.middleware("http")
async def log_requests(request: Request, call_next):

    print(f"logging request: {request.url}")


    api_key = request.headers.get("X-API-Key")
    endpoint = request.url.path
    method = request.method
    ip_address = request.client.host
    timestamp = datetime.utcnow().isoformat()

    response = await call_next(request)

    log_message = f"API Key: {api_key}, Endpoint: {endpoint}, Method: {method}, IP Address: {ip_address}, Timestamp: {timestamp}"
    logging.info(log_message)

    return response

# Utility function to verify API key for creating keys
async def check_create_auth(request: Request, db: Session = Depends(get_db)):
    api_key = request.headers.get("X-API-Key")
    print(f"Received API Key: {api_key}")  # Debug statement
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")

    sec_api_key = os.getenv("CREATE_API_KEY")
    print(f"Create API Key: {sec_api_key}")  # Debug statement

    if api_key != sec_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return {"name": "Create Key", "key": sec_api_key}

# Utility function to verify API key for getting keys
async def check_get_auth(request: Request, db: Session = Depends(get_db)):
    api_key = request.headers.get("X-API-Key")
    print(f"Received API Key: {api_key}")  # Debug statement
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")

    sec_api_key = os.getenv("GET_API_KEY")
    print(f"Get API Key: {sec_api_key}")  # Debug statement

    if api_key != sec_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return {"name": "Get Key", "key": sec_api_key}

# Utility function to verify API key for deleting keys
async def check_delete_auth(request: Request, db: Session = Depends(get_db)):
    api_key = request.headers.get("X-API-Key")
    print(f"Received API Key: {api_key}")  # Debug statement
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")

    sec_api_key = os.getenv("DELETE_API_KEY")
    print(f"Delete API Key: {sec_api_key}")  # Debug statement

    if api_key != sec_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return {"name": "Delete Key", "key": sec_api_key}

@app.post("/api/keys/create", response_model=APIKeyResponse, dependencies=[Depends(check_create_auth)])
def create_api_key(key_data: APIKeyCreate, db: Session = Depends(get_db)):
    """Create a new API key"""
    api_key = APIKey(
        name=key_data.name,
        key=secrets.token_urlsafe(32),
        created_at=datetime.utcnow(),
        expires_at=key_data.expires_at
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key.to_dict()

@app.get("/api/keys", response_model=List[APIKeyResponse], dependencies=[Depends(check_get_auth)])
def get_api_key(name: str = Query(None, description="Filter keys by name"), db: Session = Depends(get_db)):
    """List all API keys with optional name filter"""    
    if name:
        return [key.to_dict() for key in db.query(APIKey).filter(APIKey.name == name).all()]
    else:
        raise HTTPException(status_code=401, detail="You need to provide a name to filter the keys")

@app.get("/api/keys/by-id/{key_id}", response_model=APIKeyResponse, dependencies=[Depends(check_get_auth)])
def get_by_id_api_key(key_id: int, db: Session = Depends(get_db)):
    """Get a specific API key by ID"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key.to_dict()

@app.delete("/api/keys/delete/{key_id}", dependencies=[Depends(check_delete_auth)])
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    db.commit()
    return {"message": "API key deleted"}

@app.get("/", dependencies=[Depends(check_get_auth)])
def read_root():
    return {"status": "healthy", "message": "Key Management Service is running"}
