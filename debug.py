#!/usr/bin/env python3
"""
LiveKit Connection Debugger
"""
import os
import asyncio
import jwt
import aiohttp
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Get environment variables
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

def test_env_variables():
    """Test if environment variables are set"""
    print("🔍 Checking Environment Variables:")
    print("-" * 40)
    
    if LIVEKIT_API_KEY:
        print(f"✅ LIVEKIT_API_KEY: {LIVEKIT_API_KEY[:8]}...{LIVEKIT_API_KEY[-4:] if len(LIVEKIT_API_KEY) > 12 else LIVEKIT_API_KEY}")
    else:
        print("❌ LIVEKIT_API_KEY: Not set")
    
    if LIVEKIT_API_SECRET:
        print(f"✅ LIVEKIT_API_SECRET: {LIVEKIT_API_SECRET[:8]}...{LIVEKIT_API_SECRET[-4:] if len(LIVEKIT_API_SECRET) > 12 else LIVEKIT_API_SECRET}")
    else:
        print("❌ LIVEKIT_API_SECRET: Not set")
    
    if LIVEKIT_URL:
        print(f"✅ LIVEKIT_URL: {LIVEKIT_URL}")
    else:
        print("❌ LIVEKIT_URL: Not set")
    
    print()
    return all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL])

def create_test_token():
    """Create a test JWT token"""
    print("🔑 Creating Test JWT Token:")
    print("-" * 40)
    
    try:
        now = datetime.utcnow()
        payload = {
            "iss": LIVEKIT_API_KEY,
            "sub": "test_user",
            "nbf": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=3600)).timestamp()),
            "video": {
                "room_join": True,
                "room": "test_room",
                "can_publish": True,
                "can_subscribe": True
            }
        }
        
        token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
        print(f"✅ JWT Token created: {token[:50]}...")
        print(f"✅ Token payload: {json.dumps(payload, indent=2)}")
        print()
        return token
    except Exception as e:
        print(f"❌ JWT Token creation failed: {e}")
        print()
        return None

async def test_livekit_connectivity():
    """Test connectivity to LiveKit server"""
    print("🌐 Testing LiveKit Server Connectivity:")
    print("-" * 40)
    
    if not LIVEKIT_URL:
        print("❌ No LiveKit URL configured")
        return False
    
    # Extract HTTP URL from WebSocket URL
    http_url = LIVEKIT_URL.replace("wss://", "https://").replace("ws://", "http://")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test basic connectivity
            async with session.get(f"{http_url}/", timeout=10) as response:
                print(f"✅ Server reachable: {response.status}")
                
            # Test with token
            token = create_test_token()
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{http_url}/", headers=headers, timeout=10) as response:
                    print(f"✅ Token accepted: {response.status}")
                    
        return True
    except asyncio.TimeoutError:
        print("❌ Connection timeout - server might be unreachable")
        return False
    except aiohttp.ClientConnectorError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def validate_livekit_url():
    """Validate LiveKit URL format"""
    print("🔗 Validating LiveKit URL Format:")
    print("-" * 40)
    
    if not LIVEKIT_URL:
        print("❌ No URL provided")
        return False
    
    valid_prefixes = ["wss://", "ws://"]
    if not any(LIVEKIT_URL.startswith(prefix) for prefix in valid_prefixes):
        print(f"❌ URL should start with wss:// or ws://, got: {LIVEKIT_URL}")
        return False
    
    if ".livekit.cloud" in LIVEKIT_URL:
        print("✅ Using LiveKit Cloud")
    else:
        print("✅ Using self-hosted LiveKit")
    
    print(f"✅ URL format valid: {LIVEKIT_URL}")
    print()
    return True

async def test_room_creation():
    """Test room creation via API"""
    print("🏠 Testing Room Creation:")
    print("-" * 40)
    
    try:
        import requests
        
        response = requests.post("http://localhost:8000/create-room", json={
            "room": "test_room_debug",
            "participant_name": "debug_user"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Room creation successful")
            print(f"✅ Room: {data.get('room')}")
            print(f"✅ Token: {data.get('token', '')[:50]}...")
            print(f"✅ URL: {data.get('url')}")
            return True
        else:
            print(f"❌ Room creation failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server (http://localhost:8000)")
        print("   Make sure your API server is running!")
        return False
    except Exception as e:
        print(f"❌ Room creation error: {e}")
        return False

def print_troubleshooting_guide():
    """Print troubleshooting guide"""
    print("🔧 Troubleshooting Guide:")
    print("-" * 40)
    print("1. Check your .env file exists and has correct values")
    print("2. For LiveKit Cloud:")
    print("   - Go to https://cloud.livekit.io/")
    print("   - Create a project if you haven't")
    print("   - Copy API Key, API Secret, and WebSocket URL")
    print("   - URL should look like: wss://your-project.livekit.cloud")
    print()
    print("3. For self-hosted LiveKit:")
    print("   - Make sure your LiveKit server is running")
    print("   - Check firewall settings")
    print("   - Verify WebSocket URL is accessible")
    print()
    print("4. Test your API server:")
    print("   - Run: python main_api_server.py")
    print("   - Visit: http://localhost:8000/health")
    print()

async def main():
    """Run all diagnostic tests"""
    print("🚀 LiveKit Connection Diagnostic Tool")
    print("=" * 50)
    print()
    
    # Test 1: Environment variables
    env_ok = test_env_variables()
    if not env_ok:
        print("❌ Environment setup incomplete")
        print_troubleshooting_guide()
        return
    
    # Test 2: URL format
    url_ok = validate_livekit_url()
    if not url_ok:
        print("❌ URL format invalid")
        return
    
    # Test 3: JWT token creation
    token_ok = create_test_token() is not None
    if not token_ok:
        print("❌ Cannot create JWT tokens")
        return
    
    # Test 4: Server connectivity
    connectivity_ok = await test_livekit_connectivity()
    if not connectivity_ok:
        print("❌ LiveKit server unreachable")
        print_troubleshooting_guide()
        return
    
    # Test 5: API server
    api_ok = await test_room_creation()
    if not api_ok:
        print("❌ API server issues")
        return
    
    print("🎉 All tests passed! Your LiveKit setup should be working.")
    print()
    print("Next steps:")
    print("1. Start your API server: python main_api_server.py")
    print("2. Start your agent: python agent.py start")
    print("3. Start your React app: npm start")

if __name__ == "__main__":
    asyncio.run(main())