#!/bin/bash

echo "🚀 TeamSync Pro Development Setup"

# Backend setup
echo "📦 Setting up Backend..."
cd src/backend
npm install
echo "✅ Backend dependencies installed"

# Frontend setup
echo "📦 Setting up Frontend..."
cd ../frontend
npm install
echo "✅ Frontend dependencies installed"

# VS Code Extension setup
echo "📦 Setting up VS Code Extension..."
cd ../extension
npm install
echo "✅ Extension dependencies installed"

cd ../../

echo "🎉 Setup complete!"
echo ""
echo "To start development:"
echo "1. Backend: cd src/backend && npm run dev"
echo "2. Frontend: cd src/frontend && npm run dev"
echo "3. Extension: Open in VS Code and press F5"
echo ""
echo "Make sure to:"
echo "- Install PostgreSQL and Redis"
echo "- Copy .env.example to .env and configure"
echo "- Create database 'teamsync'"
