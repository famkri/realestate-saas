cat > app/routers/__init__.py <<'EOF'
from fastapi import APIRouter
from .auth import router as auth_router
from .listings import router as listings_router

api_router = APIRouter()

# Include routers with prefixes
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(listings_router, tags=["listings"])
EOF
