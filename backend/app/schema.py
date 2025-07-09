from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ListingResponse(BaseModel):
    id: int
    title: str
    price: Optional[str]
    location: Optional[str]
    url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
