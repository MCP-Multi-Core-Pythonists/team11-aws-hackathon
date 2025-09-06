#!/usr/bin/env python3
"""
Setup instructions for Sync Hub local development environment
"""

def main():
    print("🔄 Sync Hub - Local Development Environment Setup")
    print("=" * 60)
    
    print("\n📋 Prerequisites:")
    print("- Python 3.12+")
    print("- uv package manager (https://github.com/astral-sh/uv)")
    
    print("\n🚀 Quick Setup:")
    print("1. Create virtual environment:")
    print("   uv venv")
    
    print("\n2. Install dependencies:")
    print("   uv pip install fastapi uvicorn[standard] pydantic requests httpx python-dotenv boto3 python-multipart jinja2 ruff mypy pytest pytest-asyncio anyio types-requests")
    
    print("\n3. Configure environment:")
    print("   cp .env.example .env")
    
    print("\n4. Start development server:")
    print("   source .venv/bin/activate")
    print("   uvicorn services.webauth.main:app --reload --port 3001")
    
    print("\n5. Open browser:")
    print("   http://localhost:3001")
    
    print("\n🔧 Available Commands:")
    print("- Start dev server: uvicorn services.webauth.main:app --reload --port 3001")
    print("- Run smoke test: python tools/smoke_local.py")
    print("- Lint code: ruff check .")
    print("- Format code: ruff format .")
    print("- Type check: mypy services")
    
    print("\n🌐 Authentication Flow:")
    print("1. Visit http://localhost:3001")
    print("2. Click 'Login with Google'")
    print("3. Complete OAuth flow → redirected to /callback")
    print("4. Access protected endpoints: /me, /settings/public")
    
    print("\n📁 Project Structure:")
    print("sync-hub/")
    print("├── pyproject.toml          # Project config & dependencies")
    print("├── .env.example            # Environment template")
    print("├── services/")
    print("│   └── webauth/")
    print("│       └── main.py         # FastAPI web auth service")
    print("└── tools/")
    print("    └── smoke_local.py      # Smoke tests")
    
    print("\n🔗 Endpoints:")
    print("- GET /                     # Main page with auth status")
    print("- GET /login-start          # Start OAuth flow (PKCE)")
    print("- GET /callback             # OAuth callback handler")
    print("- GET /me                   # User profile (requires auth)")
    print("- GET /settings/public      # Public settings proxy")
    print("- GET /logout               # Logout and clear cookies")
    print("- GET /health               # Health check")
    
    print("\n⚙️  Configuration (.env):")
    print("COGNITO_DOMAIN=https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com")
    print("COGNITO_CLIENT_ID=7n568rmtbtp2tt8m0av2hl0f2n")
    print("REDIRECT_URI=http://localhost:3001/callback")
    print("LOGOUT_URI=http://localhost:3001/")
    print("API_BASE=https://l7ycatge3j.execute-api.us-east-1.amazonaws.com")
    
    print("\n✅ Ready to develop!")

if __name__ == "__main__":
    main()
