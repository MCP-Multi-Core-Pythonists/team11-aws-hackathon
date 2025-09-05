import os
import secrets
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

# Security configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRES_IN = int(os.getenv('JWT_EXPIRES_IN_HOURS', '24'))

app = FastAPI(title="TeamSync Secure API")
security = HTTPBearer()

# In-memory user store (use database in production)
users_db = {}

def create_access_token(user_data: dict) -> str:
    """Create JWT token with expiration"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRES_IN)
    to_encode = {
        **user_data,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models remain the same...
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    created_at: str

class Team(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_public: bool = False

class SyncRequest(BaseModel):
    settings: dict

class Bookmark(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    tags: List[str] = []

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/_health")
async def public_health():
    return {"ok": True, "ts": datetime.now().isoformat()}

# Authentication
@app.post("/auth/register")
async def register(request: RegisterRequest):
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password in production
    user_id = str(uuid4())
    users_db[request.email] = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "password": request.password,  # Hash this in production!
        "created_at": datetime.now().isoformat()
    }
    
    return {"success": True, "message": "User registered successfully"}

@app.post("/auth/login")
async def login(request: LoginRequest):
    user = users_db.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_data = {
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"]
    }
    
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRES_IN * 3600,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    }

# Protected endpoints
@app.get("/users/me")
async def get_profile(current_user: dict = Depends(verify_token)):
    return {
        "id": current_user["user_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "created_at": datetime.now().isoformat()
    }

@app.get("/teams")
async def get_teams(current_user: dict = Depends(verify_token)):
    return [
        Team(
            id=str(uuid4()),
            name="Development Team",
            description="Main development team",
            is_public=False
        ),
        Team(
            id=str(uuid4()),
            name="Frontend Team", 
            description="Frontend specialists",
            is_public=True
        )
    ]

# Settings sync
@app.post("/settings/sync/apply")
async def sync_apply(request: SyncRequest):
    return {
        "success": True,
        "applied_count": len(request.settings),
        "version": 1,
        "version_id": str(uuid4())
    }

@app.post("/settings/sync/preview")
async def sync_preview(request: SyncRequest):
    return {
        "conflicts": [],
        "preview": request.settings,
        "safe_to_apply": True
    }

# Bookmarks
@app.get("/bookmarks")
async def get_bookmarks():
    return [
        Bookmark(
            id=str(uuid4()),
            name="My React Setup",
            description="Personal React configuration",
            tags=["react", "personal"]
        ),
        Bookmark(
            id=str(uuid4()),
            name="Python Backend Config",
            description="Backend development setup",
            tags=["python", "backend"]
        )
    ]

@app.post("/bookmarks")
async def create_bookmark(bookmark: dict):
    return Bookmark(
        id=str(uuid4()),
        name=bookmark["name"],
        description=bookmark.get("description"),
        tags=bookmark.get("tags", [])
    )

@app.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: str):
    return {"success": True, "deleted": bookmark_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
