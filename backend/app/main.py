from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from app.db.database import engine, get_db
from app.models import user as user_models
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.crud.user import create_user, get_user_by_email, authenticate_user
from app.auth.auth import create_access_token, get_current_user
from app.dependencies import get_db

# Create database tables
user_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate Scraper API", version="1.0.0")

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

security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "Real Estate Scraper API"}

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        db_user = create_user(db=db, user=user)
        return UserResponse(
            id=db_user.id,
            email=db_user.email,
            is_active=db_user.is_active
        )
    except Exception as e:
        print(f"Register error: {e}")  # This will show up in Render logs
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
  
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: user_models.User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active
    )

@app.get("/protected")
async def protected_route(current_user: user_models.User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}, this is a protected route!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
