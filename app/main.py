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
async def check_auth(request: Request):
    api_key = request.headers.get("X-API-Key")
    print(f"Received API Key: {api_key}")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")

    sec_api_key = os.getenv("SEC_API_KEY")
    # print(f"Secure API Key: {sec_api_key}")

    if api_key == sec_api_key:
        return {"name": "Secure Key", "key": sec_api_key}
    else: 
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/api/keys/create", response_model=APIKeyResponse, dependencies=[Depends(check_auth)])
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

@app.get("/api/keys", response_model=List[APIKeyResponse], dependencies=[Depends(check_auth)])
def list_api_keys(name: str = Query(None, description="Filter keys by name"), db: Session = Depends(get_db)):
    """List all API keys with optional name filter"""    
    if name:
        return [key.to_dict() for key in db.query(APIKey).filter(APIKey.name == name).all()]
    else:
        raise HTTPException(status_code=401, detail="You need to provide a name to filter the keys")

@app.get("/api/keys/by-id/{key_id}", response_model=APIKeyResponse, dependencies=[Depends(check_auth)])
def check_auth(key_id: int, db: Session = Depends(get_db)):
    """Get a specific API key by ID"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key.to_dict()

@app.delete("/api/keys/delete/{key_id}", dependencies=[Depends(check_auth)])
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an API key"""
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    db.commit()
    return {"message": "API key deleted"}

@app.get("/", dependencies=[Depends(check_auth)])
def read_root():
    return {"status": "healthy", "message": "Key Management Service is running"}