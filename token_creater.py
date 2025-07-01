import jwt
import time

def create_barebones_livekit_token(api_key, api_secret, room_name, participant_identity):
    """
    Create a minimal LiveKit token with no extra metadata.
    
    Args:
        api_key: Your LiveKit API key
        api_secret: Your LiveKit API secret  
        room_name: Name of the room to join
        participant_identity: Unique identifier for the participant
    
    Returns:
        JWT token string
    """
    
    # Create the minimal token payload
    payload = {
        "iss": api_key,
        "sub": participant_identity,
        "exp": int(time.time()) + 3600,  # 1 hour expiration
        "video": {
            "roomJoin": True,
            "room": room_name
        }
    }
    
    # Generate the JWT token
    token = jwt.encode(payload, api_secret, algorithm="HS256")
    return token

# Example usage
if __name__ == "__main__":
    # Replace with your actual LiveKit credentials
    API_KEY = "APID4ukNNTGzQX4"
    API_SECRET = "f5xs1eZXKXMe7q9m9BPxf7yLyrFP12SdvbJJfJkdxFaD"
    
    # Room and participant details
    room_name = "65eff450-5d86-46f1-8b00-3f975c6e88d6"
    participant_id = "user123"
    
    # Generate minimal token
    token = create_barebones_livekit_token(API_KEY, API_SECRET, room_name, participant_id)
    
    print("LiveKit Token:")
    print(token)
