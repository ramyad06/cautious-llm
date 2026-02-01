#!/bin/bash

# Installation script for Code Intelligence Agent

echo "🚀 Installing Code Intelligence Agent..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
REPO_PATH=./test-project
DB_PATH=./chroma_db
BATCH_SIZE=50
EOF
    echo "⚠️  Please edit .env and add your GROQ_API_KEY"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GROQ_API_KEY"
echo "2. Activate virtual environment: source .venv/bin/activate"
echo "3. Initialize database: python3 cli.py init"
echo "4. Start using: python3 cli.py --help"
echo ""
echo "Or run the API server: python3 api.py"