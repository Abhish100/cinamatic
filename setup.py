#!/usr/bin/env python3
"""
Setup script for Cinematic Movie Recommendation App
This script helps configure the environment with API keys.
"""

import os
import shutil

def setup_environment():
    """Set up the environment configuration"""
    print("🎬 Cinematic Movie Recommendation App Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Copy config.env to .env if it exists
    if os.path.exists('config.env'):
        shutil.copy('config.env', '.env')
        print("✅ API keys configured from config.env")
        print("✅ Environment setup complete!")
    else:
        print("❌ config.env file not found!")
        print("Please create a .env file with your API keys:")
        print("TRAKT_CLIENT_ID=your_trakt_client_id")
        print("TRAKT_CLIENT_SECRET=your_trakt_client_secret")
        print("NEWS_API_KEY=your_newsapi_key")
        print("WATCHMODE_API_KEY=your_watchmode_api_key")
    
    print("\n🚀 You can now run the app with: python app.py")
    print("🌐 Visit http://localhost:5000 to start using Cinematic!")

if __name__ == "__main__":
    setup_environment() 