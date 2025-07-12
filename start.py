#!/usr/bin/env python3
"""
Smart Warehouse Simulator - Startup Script
The Ultimate Hackathon Winner Application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = [
        "backend/models",
        "backend/services", 
        "backend/database",
        "backend/utils",
        "frontend/static/css",
        "frontend/static/js",
        "frontend/templates",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting Smart Warehouse Simulator...")
    print("🎯 This application is designed to WIN FIRST PLACE in hackathons!")
    print()
    
    # Change to backend directory
    os.chdir("backend")
    
    # Start the application
    try:
        print("🌟 Starting AI-Powered Warehouse Management System...")
        print("🔗 WebSocket server: ws://localhost:8000/ws/warehouse")
        print("📊 API Documentation: http://localhost:8000/api/docs")
        print("🎮 Main Application: http://localhost:8000")
        print()
        print("⏳ Starting server...")
        
        # Start the FastAPI application
        subprocess.run([sys.executable, "main.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🏆 Smart Warehouse Simulator - Hackathon Winner")
    print("=" * 50)
    print("🤖 AI-Powered Warehouse Management System")
    print("🎮 Real-time 3D Visualization")
    print("📊 Advanced Analytics Dashboard")
    print("🚀 Designed to WIN FIRST PLACE!")
    print("=" * 50)
    print()
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies if requirements.txt exists
    if Path("requirements.txt").exists():
        install_dependencies()
    else:
        print("⚠️  requirements.txt not found, skipping dependency installation")
    
    print()
    print("🎯 Features that will impress judges:")
    print("   • AI/ML-powered demand forecasting")
    print("   • Real-time 3D warehouse visualization")
    print("   • Intelligent route optimization")
    print("   • Predictive analytics and insights")
    print("   • Live robot fleet management")
    print("   • Professional-grade UI/UX")
    print("   • Real-time WebSocket communication")
    print("   • Comprehensive analytics dashboard")
    print()
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main() 