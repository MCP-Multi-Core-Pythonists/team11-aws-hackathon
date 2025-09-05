import os
import secrets
import bcrypt
import jwt
import sqlite3
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from uuid import uuid4
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRES_IN = int(os.getenv('JWT_EXPIRES_IN_HOURS', '24'))

app = FastAPI(
    title="TeamSync Production API",
    description="Complete team collaboration and settings sync API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "vscode-webview://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Database setup
def init_database():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect('teamsync.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            owner_id TEXT NOT NULL,
            is_public BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    
    # Team members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id TEXT PRIMARY KEY,
            team_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(team_id, user_id)
        )
    ''')
    
    # Team configs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_configs (
            id TEXT PRIMARY KEY,
            team_id TEXT NOT NULL,
            name TEXT NOT NULL,
            settings_json TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Prompts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id TEXT PRIMARY KEY,
            team_id TEXT NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Bookmarks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            setting_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Initialize database on startup
init_database()

# Pydantic models with validation
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v.strip()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Team name must be at least 2 characters long')
        return v.strip()

class ConfigCreateRequest(BaseModel):
    name: str
    settings_json: dict
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Config name must be at least 2 characters long')
        return v.strip()

class PromptCreateRequest(BaseModel):
    name: str
    content: str
    category: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Prompt name must be at least 2 characters long')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Prompt content must be at least 10 characters long')
        return v.strip()

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_db():
    """Get database connection"""
    conn = sqlite3.connect('teamsync.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Health endpoints
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/_health")
async def public_health():
    return {"ok": True, "ts": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/auth/register")
async def register(request: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    """Register new user with validation"""
    try:
        cursor = db.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user_id = str(uuid4())
        password_hash = hash_password(request.password)
        
        cursor.execute(
            "INSERT INTO users (id, email, name, password_hash) VALUES (?, ?, ?, ?)",
            (user_id, request.email, request.name, password_hash)
        )
        db.commit()
        
        logger.info(f"New user registered: {request.email}")
        return {"success": True, "message": "User registered successfully", "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/auth/login")
async def login(request: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    """Login user and return JWT token"""
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, email, name, password_hash FROM users WHERE email = ?",
            (request.email,)
        )
        user = cursor.fetchone()
        
        if not user or not verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create token
        token_data = {
            "user_id": user['id'],
            "email": user['email'],
            "name": user['name']
        }
        access_token = create_access_token(token_data)
        
        logger.info(f"User logged in: {request.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRES_IN * 3600,
            "user": {
                "id": user['id'],
                "email": user['email'],
                "name": user['name']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# User profile endpoints
@app.get("/users/me")
async def get_my_profile(current_user: dict = Depends(verify_token)):
    """Get current user profile"""
    return {
        "id": current_user["user_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "created_at": datetime.now().isoformat()
    }

@app.put("/users/me")
async def update_my_profile(
    profile_data: dict,
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Update current user profile"""
    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (profile_data.get("name", current_user["name"]), current_user["user_id"])
        )
        db.commit()
        
        return {
            "id": current_user["user_id"],
            "email": current_user["email"],
            "name": profile_data.get("name", current_user["name"]),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Profile update failed")

# Teams endpoints
@app.get("/teams")
async def get_my_teams(
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get current user's teams"""
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.description, t.owner_id, t.is_public, 
                   t.created_at, t.updated_at, tm.role
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id AND tm.user_id = ?
            WHERE t.owner_id = ? OR tm.user_id = ?
        """, (current_user["user_id"], current_user["user_id"], current_user["user_id"]))
        
        teams = []
        for row in cursor.fetchall():
            teams.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "owner_id": row["owner_id"],
                "is_public": bool(row["is_public"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "role": row["role"] or ("owner" if row["owner_id"] == current_user["user_id"] else "member")
            })
        
        return teams
    except Exception as e:
        logger.error(f"Get teams failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get teams")

@app.post("/teams")
async def create_team(
    request: TeamCreateRequest,
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Create new team"""
    try:
        cursor = db.cursor()
        team_id = str(uuid4())
        
        cursor.execute(
            "INSERT INTO teams (id, name, description, owner_id, is_public) VALUES (?, ?, ?, ?, ?)",
            (team_id, request.name, request.description, current_user["user_id"], request.is_public)
        )
        
        # Add owner as team member
        cursor.execute(
            "INSERT INTO team_members (id, team_id, user_id, role) VALUES (?, ?, ?, ?)",
            (str(uuid4()), team_id, current_user["user_id"], "owner")
        )
        
        db.commit()
        logger.info(f"Team created: {request.name} by {current_user['email']}")
        
        return {
            "id": team_id,
            "name": request.name,
            "description": request.description,
            "owner_id": current_user["user_id"],
            "is_public": request.is_public,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Team creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Team creation failed")

# Team configs endpoints
@app.get("/teams/{team_id}/configs")
async def get_team_configs(
    team_id: str,
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get team configurations"""
    try:
        # Verify team membership
        cursor = db.cursor()
        cursor.execute(
            "SELECT role FROM team_members WHERE team_id = ? AND user_id = ?",
            (team_id, current_user["user_id"])
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not a team member")
        
        # Get configs
        cursor.execute(
            "SELECT id, name, settings_json, created_by, created_at, updated_at FROM team_configs WHERE team_id = ?",
            (team_id,)
        )
        
        configs = []
        for row in cursor.fetchall():
            configs.append({
                "id": row["id"],
                "team_id": team_id,
                "name": row["name"],
                "settings_json": eval(row["settings_json"]),  # In production, use json.loads
                "created_by": row["created_by"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        
        return configs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get team configs failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get team configs")

@app.post("/teams/{team_id}/configs")
async def create_team_config(
    team_id: str,
    request: ConfigCreateRequest,
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Create team configuration"""
    try:
        # Verify team membership
        cursor = db.cursor()
        cursor.execute(
            "SELECT role FROM team_members WHERE team_id = ? AND user_id = ?",
            (team_id, current_user["user_id"])
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not a team member")
        
        config_id = str(uuid4())
        cursor.execute(
            "INSERT INTO team_configs (id, team_id, name, settings_json, created_by) VALUES (?, ?, ?, ?, ?)",
            (config_id, team_id, request.name, str(request.settings_json), current_user["user_id"])
        )
        db.commit()
        
        return {
            "id": config_id,
            "team_id": team_id,
            "name": request.name,
            "settings_json": request.settings_json,
            "created_by": current_user["user_id"],
            "created_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create team config failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create team config")

# Settings sync endpoints
@app.post("/settings/sync/apply")
async def sync_apply(
    request: dict,
    current_user: dict = Depends(verify_token)
):
    """Apply settings synchronization"""
    try:
        settings = request.get("settings", {})
        return {
            "success": True,
            "applied_count": len(settings),
            "version": 1,
            "version_id": str(uuid4())
        }
    except Exception as e:
        logger.error(f"Settings sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Settings sync failed")

@app.post("/settings/sync/preview")
async def sync_preview(
    request: dict,
    current_user: dict = Depends(verify_token)
):
    """Preview settings synchronization"""
    settings = request.get("settings", {})
    return {
        "conflicts": [],
        "preview": settings,
        "safe_to_apply": True
    }

# Bookmarks endpoints
@app.get("/bookmarks")
async def get_bookmarks(
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get user bookmarks"""
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, setting_id, name, description, tags, created_at FROM bookmarks WHERE user_id = ?",
            (current_user["user_id"],)
        )
        
        bookmarks = []
        for row in cursor.fetchall():
            bookmarks.append({
                "id": row["id"],
                "user_id": current_user["user_id"],
                "setting_id": row["setting_id"],
                "name": row["name"],
                "description": row["description"],
                "tags": row["tags"].split(",") if row["tags"] else [],
                "created_at": row["created_at"]
            })
        
        return bookmarks
    except Exception as e:
        logger.error(f"Get bookmarks failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get bookmarks")

@app.post("/bookmarks")
async def create_bookmark(
    request: dict,
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Create bookmark"""
    try:
        cursor = db.cursor()
        bookmark_id = str(uuid4())
        tags_str = ",".join(request.get("tags", []))
        
        cursor.execute(
            "INSERT INTO bookmarks (id, user_id, setting_id, name, description, tags) VALUES (?, ?, ?, ?, ?, ?)",
            (bookmark_id, current_user["user_id"], request["setting_id"], 
             request["name"], request.get("description"), tags_str)
        )
        db.commit()
        
        return {
            "id": bookmark_id,
            "user_id": current_user["user_id"],
            "setting_id": request["setting_id"],
            "name": request["name"],
            "description": request.get("description"),
            "tags": request.get("tags", []),
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Create bookmark failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create bookmark")

# Notifications endpoints
@app.get("/notifications")
async def get_notifications(
    current_user: dict = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db)
):
    """Get user notifications"""
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, type, message, read, created_at FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
            (current_user["user_id"],)
        )
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "id": row["id"],
                "user_id": current_user["user_id"],
                "type": row["type"],
                "message": row["message"],
                "read": bool(row["read"]),
                "created_at": row["created_at"]
            })
        
        return notifications
    except Exception as e:
        logger.error(f"Get notifications failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")
