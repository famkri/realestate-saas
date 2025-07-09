from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import os

from app.database import get_db, init_db
from app.models import User, Listing
from app.schemas import UserCreate, UserResponse, Token, LoginRequest, ListingResponse
from app.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Real Estate SaaS API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://realestate-saas-chi.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        print("✅ Database initialized successfully")
        
        # Create a default user if none exists
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            existing_user = db.query(User).first()
            if not existing_user:
                default_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin123")
                )
                db.add(default_user)
                db.commit()
                print("✅ Default user created: admin/admin123")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")

@app.get("/")
async def root():
    return {"message": "Real Estate SaaS API is running!"}

@app.post("/api/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/listings", response_model=list[ListingResponse])
async def get_listings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listings = db.query(Listing).limit(100).all()
    return listings

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
