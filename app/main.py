from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
import secrets

from app.models import Base, APIKey
from app.database import SessionLocal, engine
from app.schemas import APIKeyCreate, APIKeyResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Key Management Service")
api_key_header = APIKeyHeader(name="X-API-Key")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/keys", response_model=APIKeyResponse)
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

@app.get("/api/keys", response_model=List[APIKeyResponse])
def list_api_keys(name: str = Query(None, description="Filter keys by name"), db: Session = Depends(get_db)):
    """List all API keys with optional name filter"""
    query = db.query(APIKey)
    if name:
        query = query.filter(APIKey.name == name)
    keys = query.all()
    return [key.to_dict() for key in keys]

@app.get("/api/keys/{key_id}", response_model=APIKeyResponse)
def get_api_key(key_id: int, db: Session = Depends(get_db)):
    """Get a specific API key by ID"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key.to_dict()

@app.get("/api/keys/name/{name}", response_model=List[APIKeyResponse])
def get_api_keys_by_name(name: str, db: Session = Depends(get_db)):
    """Get API keys by name"""
    keys = db.query(APIKey).filter(APIKey.name == name).all()
    if not keys:
        raise HTTPException(status_code=404, detail=f"No API keys found with name: {name}")
    return [key.to_dict() for key in keys]

@app.delete("/api/keys/{key_id}")
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    db.commit()
    return {"message": "API key deleted"}

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Key Management Service is running"}