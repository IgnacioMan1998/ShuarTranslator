#!/usr/bin/env python3
"""
Startup script for Shuar Chicham Translator
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_virtual_env():
    """Check if running in virtual environment."""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Consider running: python3 -m venv venv && source venv/bin/activate")
    else:
        print("✅ Virtual environment active")

def install_dependencies():
    """Install dependencies if needed."""
    try:
        import fastapi
        import supabase
        print("✅ Dependencies installed")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def check_env_file():
    """Check if .env file exists."""
    if not Path(".env").exists():
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and configure your settings")
        return False
    print("✅ Environment file found")
    return True

def main():
    """Main startup function."""
    print("🚀 Starting Shuar Chicham Translator")
    print("=" * 50)
    
    check_python_version()
    check_virtual_env()
    install_dependencies()
    
    if not check_env_file():
        print("\n❌ Setup incomplete. Please configure .env file first.")
        sys.exit(1)
    
    print("\n🌟 Starting application...")
    
    # Import and run the app
    try:
        from main import app
        import uvicorn
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()