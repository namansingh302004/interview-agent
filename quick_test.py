#!/usr/bin/env python3
"""
Quick test to verify LiveKit setup
"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def main():
    print("🔍 Quick LiveKit Setup Test")
    print("=" * 30)
    
    # Check environment variables
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    livekit_url = os.getenv("LIVEKIT_URL")
    
    print(f"API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"API Secret: {'✅ Set' if api_secret else '❌ Missing'}")
    print(f"LiveKit URL: {'✅ Set' if livekit_url else '❌ Missing'}")
    
    if livekit_url:
        print(f"URL: {livekit_url}")
    
    # Test API server
    print("\n🔍 Testing API Server...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running")
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"LiveKit URL: {data.get('livekit_url')}")
        else:
            print(f"❌ API Server returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API Server not running")
        print("   Start it with: python main_api_server.py")
    except Exception as e:
        print(f"❌ API Server error: {e}")

if __name__ == "__main__":
    main()