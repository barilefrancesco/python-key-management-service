from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
import secrets
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from app.models import Base, APIKey
from app.database import SessionLocal, engine
from app.schemas import APIKeyCreate, APIKeyResponse

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

# Utility function to verify API key
async def get_api_key(request: Request, db: Session = Depends(get_db)):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")

    sec_api_key = os.getenv("SEC_API_KEY")
    print(f"Provided API Key: {api_key}")
    print(f"Secure API Key: {sec_api_key}")

    if api_key == sec_api_key:
        return {"name": "Secure Key", "key": sec_api_key}

    key = db.query(APIKey).filter(APIKey.key == api_key).first()
    if not key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if key.expires_at and key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key has expired")

    return key

@app.post("/api/keys", response_model=APIKeyResponse, dependencies=[Depends(get_api_key)])
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

@app.get("/api/keys", response_model=List[APIKeyResponse], dependencies=[Depends(get_api_key)])
def list_api_keys(name: str = Query(None, description="Filter keys by name"), db: Session = Depends(get_db)):
    """List all API keys with optional name filter"""
    query = db.query(APIKey)
    if name:
        query = query.filter(APIKey.name == name)
    keys = query.all()
    return [key.to_dict() for key in keys]

@app.get("/api/keys/{key_id}", response_model=APIKeyResponse, dependencies=[Depends(get_api_key)])
def get_api_key(key_id: int, db: Session = Depends(get_db)):
    """Get a specific API key by ID"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key.to_dict()

@app.get("/api/keys/name/{name}", response_model=List[APIKeyResponse], dependencies=[Depends(get_api_key)])
def get_api_keys_by_name(name: str, db: Session = Depends(get_db)):
    """Get API keys by name"""
    keys = db.query(APIKey).filter(APIKey.name == name).all()
    if not keys:
        raise HTTPException(status_code=404, detail=f"No API keys found with name: {name}")
    return [key.to_dict() for key in keys]

@app.delete("/api/keys/{key_id}", dependencies=[Depends(get_api_key)])
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    db.commit()
    return {"message": "API key deleted"}

@app.get("/", dependencies=[Depends(get_api_key)])
def read_root():
    return {"status": "healthy", "message": "Key Management Service is running"}