import os
import secrets
import hashlib
import base64
from urllib.parse import urlencode, quote
from typing import Optional

import httpx
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Sync Hub Local Dev", version="1.0.0")

# Configuration
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
LOGOUT_URI = os.getenv("LOGOUT_URI")
API_BASE = os.getenv("API_BASE")

class TokenResponse(BaseModel):
    access_token: str
    id_token: str
    token_type: str
    expires_in: int

class UserInfo(BaseModel):
    sub: str
    email: str
    email_verified: bool
    given_name: Optional[str] = None
    family_name: Optional[str] = None

def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

def get_access_token(request: Request) -> Optional[str]:
    """Extract access token from cookies"""
    return request.cookies.get("access_token")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page showing authentication status"""
    access_token = get_access_token(request)
    
    if access_token:
        status_html = f"""
        <div style="color: green;">
            <h3>✅ Authenticated</h3>
            <p>Access token: {access_token[:20]}...</p>
            <p><a href="/me">View Profile</a> | <a href="/settings/public">Public Settings</a> | <a href="/logout">Logout</a></p>
        </div>
        """
    else:
        status_html = """
        <div style="color: red;">
            <h3>❌ Not Authenticated</h3>
            <p><a href="/login-start">Login with Google</a></p>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sync Hub Local Dev</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .container {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
            a {{ color: #007bff; text-decoration: none; margin-right: 10px; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔄 Sync Hub Local Development</h1>
            {status_html}
            
            <h3>Available Endpoints:</h3>
            <ul>
                <li><a href="/login-start">GET /login-start</a> - Start OAuth flow</li>
                <li><a href="/me">GET /me</a> - User profile (requires auth)</li>
                <li><a href="/settings/public">GET /settings/public</a> - Public settings</li>
                <li><a href="/logout">GET /logout</a> - Logout</li>
            </ul>
            
            <h3>Configuration:</h3>
            <ul>
                <li>Cognito Domain: {COGNITO_DOMAIN}</li>
                <li>Client ID: {COGNITO_CLIENT_ID}</li>
                <li>API Base: {API_BASE}</li>
                <li>Redirect URI: {REDIRECT_URI}</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/login-start")
async def login_start(response: Response):
    """Generate PKCE parameters and redirect to Cognito"""
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Store code verifier in cookie for callback
    response.set_cookie(
        "code_verifier", 
        code_verifier, 
        max_age=600,  # 10 minutes
        httponly=True,
        secure=False  # Set to True in production
    )
    
    # Build authorization URL
    params = {
        "client_id": COGNITO_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "identity_provider": "Google"
    }
    
    auth_url = f"{COGNITO_DOMAIN}/oauth2/authorize?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(request: Request, response: Response, code: str):
    """Handle OAuth callback and exchange code for tokens"""
    code_verifier = request.cookies.get("code_verifier")
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Missing code verifier")
    
    # Exchange authorization code for tokens
    token_data = {
        "grant_type": "authorization_code",
        "client_id": COGNITO_CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            f"{COGNITO_DOMAIN}/oauth2/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=400, 
            detail=f"Token exchange failed: {token_response.text}"
        )
    
    tokens = token_response.json()
    
    # Set tokens in cookies
    response.set_cookie(
        "access_token",
        tokens["access_token"],
        max_age=tokens.get("expires_in", 3600),
        httponly=True,
        secure=False  # Set to True in production
    )
    
    response.set_cookie(
        "id_token",
        tokens["id_token"],
        max_age=tokens.get("expires_in", 3600),
        httponly=True,
        secure=False
    )
    
    # Clear code verifier
    response.delete_cookie("code_verifier")
    
    return RedirectResponse(url="/", status_code=302)

@app.get("/me")
async def get_user_info(request: Request):
    """Get user information from Cognito"""
    access_token = get_access_token(request)
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{COGNITO_DOMAIN}/oauth2/userInfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    
    if user_response.status_code != 200:
        raise HTTPException(
            status_code=401, 
            detail="Failed to get user info"
        )
    
    return user_response.json()

@app.get("/settings/public")
async def get_public_settings(request: Request):
    """Proxy to API Gateway /settings/public endpoint"""
    access_token = get_access_token(request)
    
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    async with httpx.AsyncClient() as client:
        api_response = await client.get(
            f"{API_BASE}/settings/public",
            headers=headers
        )
    
    if api_response.status_code != 200:
        raise HTTPException(
            status_code=api_response.status_code,
            detail=f"API request failed: {api_response.text}"
        )
    
    return api_response.json()

@app.get("/logout")
async def logout(response: Response):
    """Logout user and clear cookies"""
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("id_token")
    response.delete_cookie("code_verifier")
    
    # Build Cognito logout URL
    logout_params = {
        "client_id": COGNITO_CLIENT_ID,
        "logout_uri": LOGOUT_URI
    }
    
    logout_url = f"{COGNITO_DOMAIN}/logout?{urlencode(logout_params)}"
    return RedirectResponse(url=logout_url)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "sync-hub-local-dev"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
