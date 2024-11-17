from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "key": self.key,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }