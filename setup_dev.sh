#!/bin/bash

# Shuar Chicham Translator - Development Setup Script

echo "🚀 Setting up Shuar Chicham Translator development environment"
echo "============================================================"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Supabase credentials"
else
    echo "✅ .env file already exists"
fi

# Create tests directory if it doesn't exist
if [ ! -d "tests" ]; then
    echo "🧪 Creating tests directory..."
    mkdir -p tests
    touch tests/__init__.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Supabase credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python3 run.py"
echo "4. Visit: http://localhost:8000/docs"
echo ""
echo "Development commands:"
echo "- Run tests: pytest"
echo "- Format code: black app/"
echo "- Sort imports: isort app/"
echo "- Type check: mypy app/"