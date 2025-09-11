import asyncio
import websockets
import json
import sys

async def test_basic_websocket():
    """Test basic WebSocket connection"""
    base_url = "https://comprende-comms.preview.emergentagent.com"
    ws_url = base_url.replace("https://", "wss://")
    user_id = "test_user_simple"
    ws_endpoint = f"{ws_url}/ws/{user_id}"
    
    print(f"Testing WebSocket connection to: {ws_endpoint}")
    
    try:
        websocket = await websockets.connect(ws_endpoint)
        print("✅ WebSocket connection established successfully")
        
        # Test sending a message
        test_message = {
            "type": "test_connection",
            "message": "Hello WebSocket"
        }
        
        await websocket.send(json.dumps(test_message))
        print("✅ Message sent successfully")
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Close connection
        await websocket.close()
        print("✅ WebSocket connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def main():
    success = await test_basic_websocket()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))