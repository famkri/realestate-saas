from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(30), nullable=False, index=True)  # kleinanzeigen, immowelt, etc.
    title = Column(String(500))
    price = Column(Float, index=True)
    location = Column(String(200))
    url = Column(String(500), unique=True, nullable=False)
    description = Column(Text)
    property_type = Column(String(50))  # apartment, house, etc.
    rooms = Column(Float)
    area_sqm = Column(Float)
    raw_data = Column(Text)  # JSON string for flexibility
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'title': self.title,
            'price': self.price,
            'location': self.location,
            'url': self.url,
            'description': self.description,
            'property_type': self.property_type,
            'rooms': self.rooms,
            'area_sqm': self.area_sqm,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
