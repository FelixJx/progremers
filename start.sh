#!/bin/bash

echo "🚀 AI Agent Team - Quick Start"
echo "=============================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your API keys."
    echo ""
fi

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install it first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Start databases
echo ""
echo "🗄️  Starting databases..."
docker-compose up -d postgres redis

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 5

# Initialize database
echo ""
echo "🔧 Initializing database..."
poetry run python scripts/setup_database.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Available commands:"
echo "  poetry run python -m src.cli status          # Check system status"
echo "  poetry run python -m src.cli list-projects   # List all projects"
echo "  poetry run python -m src.cli list-agents     # List all agents"
echo "  poetry run python -m src.cli create-project  # Create a new project"
echo "  poetry run python -m src.cli start-sprint    # Start a new sprint"
echo "  poetry run python -m src.cli run             # Start the API server"
echo ""
echo "Or use the shortcut:"
echo "  poetry run python -m src.main                # Start the API server directly"