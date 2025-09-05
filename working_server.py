import os
import secrets
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRES_IN = 24

app = FastAPI(title="TeamSync Working API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# In-memory storage
users_db = {}
teams_db = {}
bookmarks_db = {}

# Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

# Utility functions
def create_access_token(user_data: dict) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRES_IN)
    to_encode = {**user_data, "exp": expire, "iat": datetime.utcnow()}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health endpoints
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/_health")
async def public_health():
    return {"ok": True, "ts": datetime.now().isoformat()}

# Auth endpoints
@app.post("/auth/register")
async def register(request: RegisterRequest):
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = str(uuid4())
    users_db[request.email] = {
        "id": user_id,
        "email": request.email,
        "name": request.name,
        "password": request.password,
        "created_at": datetime.now().isoformat()
    }
    
    return {"success": True, "message": "User registered successfully", "user_id": user_id}

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
    user_teams = []
    for team_id, team in teams_db.items():
        if team["owner_id"] == current_user["user_id"]:
            user_teams.append(team)
    return user_teams

@app.post("/teams")
async def create_team(request: TeamCreateRequest, current_user: dict = Depends(verify_token)):
    team_id = str(uuid4())
    team = {
        "id": team_id,
        "name": request.name,
        "description": request.description,
        "owner_id": current_user["user_id"],
        "is_public": request.is_public,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    teams_db[team_id] = team
    return team

@app.post("/settings/sync/apply")
async def sync_apply(request: dict, current_user: dict = Depends(verify_token)):
    settings = request.get("settings", {})
    return {
        "success": True,
        "applied_count": len(settings),
        "version": 1,
        "version_id": str(uuid4())
    }

@app.get("/bookmarks")
async def get_bookmarks(current_user: dict = Depends(verify_token)):
    user_bookmarks = []
    for bookmark_id, bookmark in bookmarks_db.items():
        if bookmark["user_id"] == current_user["user_id"]:
            user_bookmarks.append(bookmark)
    return user_bookmarks

@app.post("/bookmarks")
async def create_bookmark(request: dict, current_user: dict = Depends(verify_token)):
    bookmark_id = str(uuid4())
    bookmark = {
        "id": bookmark_id,
        "user_id": current_user["user_id"],
        "setting_id": request["setting_id"],
        "name": request["name"],
        "description": request.get("description"),
        "tags": request.get("tags", []),
        "created_at": datetime.now().isoformat()
    }
    bookmarks_db[bookmark_id] = bookmark
    return bookmark

@app.get("/notifications")
async def get_notifications(current_user: dict = Depends(verify_token)):
    return [
        {
            "id": str(uuid4()),
            "user_id": current_user["user_id"],
            "type": "team_invite",
            "message": "You've been invited to join Development Team",
            "read": False,
            "created_at": datetime.now().isoformat()
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
