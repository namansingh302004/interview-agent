from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import secrets
import string

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL]):
    raise ValueError("Missing required environment variables")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "livekit_url": LIVEKIT_URL,
        "api_key_configured": bool(LIVEKIT_API_KEY),
        "api_secret_configured": bool(LIVEKIT_API_SECRET),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/generate-token")
async def generate_token(room: str, participant_name: str):
    try:
        # Create access token with extended expiration (6 hours)
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(participant_name)
        token.with_name(participant_name)
        
        # Set expiration to 6 hours from now
        token.with_ttl(timedelta(hours=6))
        
        # Grant permissions
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        ))
        
        jwt_token = token.to_jwt()
        
        return {
            "token": jwt_token,
            "room": room,
            "participant": participant_name,
            "url": LIVEKIT_URL,
            "expires_in": 21600  # 6 hours in seconds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")

@app.post("/create-room")
async def create_room():
    try:
        # Generate a unique room name
        room_id = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(12))
        room_name = f"interview-{room_id}"
        
        return {
            "room_name": room_name,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
