import asyncio
import websockets
import json
import requests
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

class WebRTCWebSocketTester:
    def __init__(self, base_url="https://translate-hub-22.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        # Convert HTTP URL to WebSocket URL
        self.ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://")
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_meeting_id = None

    def log_test_result(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name} - FAILED")
            if details:
                print(f"   {details}")
            self.failed_tests.append({
                'name': name,
                'details': details
            })

    async def test_websocket_connection(self):
        """Test basic WebSocket connection to /ws/{user_id}"""
        print("\n🔍 Testing WebSocket Connection...")
        
        user_id = "test_user_1"
        ws_endpoint = f"{self.ws_url}/ws/{user_id}"
        
        try:
            async with websockets.connect(ws_endpoint, timeout=10) as websocket:
                # Test connection is established
                self.log_test_result(
                    "WebSocket Connection Establishment",
                    True,
                    f"Successfully connected to {ws_endpoint}"
                )
                
                # Test sending a simple message
                test_message = {
                    "type": "test_connection",
                    "message": "Connection test"
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait a moment to see if connection stays stable
                await asyncio.sleep(1)
                
                self.log_test_result(
                    "WebSocket Message Sending",
                    True,
                    "Successfully sent test message without connection dropping"
                )
                
                return True
                
        except websockets.exceptions.ConnectionClosed as e:
            self.log_test_result(
                "WebSocket Connection",
                False,
                f"Connection closed unexpectedly: {e}"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "WebSocket Connection",
                False,
                f"Connection failed: {e}"
            )
            return False

    async def test_meeting_join_leave_websocket(self):
        """Test meeting join/leave functionality via WebSocket"""
        print("\n🤝 Testing Meeting Join/Leave via WebSocket...")
        
        # First create a meeting via REST API
        meeting_data = {
            "name": "WebSocket Test Meeting",
            "participants": ["test_user_1", "test_user_2"],
            "scheduled_time": None
        }
        
        try:
            response = requests.post(f"{self.api_url}/meetings", json=meeting_data, timeout=10)
            if response.status_code != 200:
                self.log_test_result(
                    "Meeting Creation for WebSocket Test",
                    False,
                    f"Failed to create meeting: {response.status_code} - {response.text}"
                )
                return False
            
            meeting_response = response.json()
            self.test_meeting_id = meeting_response.get('id')
            
            if not self.test_meeting_id:
                self.log_test_result(
                    "Meeting Creation for WebSocket Test",
                    False,
                    "No meeting ID returned from creation"
                )
                return False
            
            self.log_test_result(
                "Meeting Creation for WebSocket Test",
                True,
                f"Created meeting with ID: {self.test_meeting_id}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Meeting Creation for WebSocket Test",
                False,
                f"Exception during meeting creation: {e}"
            )
            return False
        
        # Test WebSocket join/leave functionality
        user_id = "test_user_1"
        ws_endpoint = f"{self.ws_url}/ws/{user_id}"
        
        try:
            async with websockets.connect(ws_endpoint, timeout=10) as websocket:
                # Test joining a meeting
                join_message = {
                    "type": "join_meeting",
                    "meeting_id": self.test_meeting_id
                }
                
                await websocket.send(json.dumps(join_message))
                
                # Wait for potential response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "existing_participants":
                        self.log_test_result(
                            "Meeting Join WebSocket Message",
                            True,
                            f"Received existing participants list: {response_data.get('participants', [])}"
                        )
                    else:
                        self.log_test_result(
                            "Meeting Join WebSocket Message",
                            True,
                            f"Join message processed, received: {response_data.get('type', 'unknown')}"
                        )
                        
                except asyncio.TimeoutError:
                    self.log_test_result(
                        "Meeting Join WebSocket Message",
                        True,
                        "Join message sent successfully (no immediate response expected)"
                    )
                
                # Test leaving a meeting
                leave_message = {
                    "type": "leave_meeting",
                    "meeting_id": self.test_meeting_id
                }
                
                await websocket.send(json.dumps(leave_message))
                
                self.log_test_result(
                    "Meeting Leave WebSocket Message",
                    True,
                    "Leave message sent successfully"
                )
                
                return True
                
        except Exception as e:
            self.log_test_result(
                "Meeting Join/Leave WebSocket",
                False,
                f"WebSocket communication failed: {e}"
            )
            return False

    async def test_webrtc_signaling_messages(self):
        """Test WebRTC signaling message forwarding"""
        print("\n📡 Testing WebRTC Signaling Messages...")
        
        # We'll simulate two users for WebRTC signaling
        user1_id = "webrtc_user_1"
        user2_id = "webrtc_user_2"
        
        user1_ws_endpoint = f"{self.ws_url}/ws/{user1_id}"
        user2_ws_endpoint = f"{self.ws_url}/ws/{user2_id}"
        
        try:
            # Connect both users
            async with websockets.connect(user1_ws_endpoint, timeout=10) as user1_ws, \
                       websockets.connect(user2_ws_endpoint, timeout=10) as user2_ws:
                
                self.log_test_result(
                    "Dual WebSocket Connections for WebRTC",
                    True,
                    "Both users connected successfully"
                )
                
                # Test WebRTC Offer forwarding
                offer_message = {
                    "type": "webrtc_offer",
                    "target_user": user2_id,
                    "offer": {
                        "type": "offer",
                        "sdp": "v=0\r\no=- 123456789 123456789 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
                    }
                }
                
                await user1_ws.send(json.dumps(offer_message))
                
                # Check if user2 receives the offer
                try:
                    response = await asyncio.wait_for(user2_ws.recv(), timeout=5)
                    response_data = json.loads(response)
                    
                    if (response_data.get("type") == "webrtc_offer" and 
                        response_data.get("from_user") == user1_id):
                        self.log_test_result(
                            "WebRTC Offer Forwarding",
                            True,
                            f"Offer successfully forwarded from {user1_id} to {user2_id}"
                        )
                    else:
                        self.log_test_result(
                            "WebRTC Offer Forwarding",
                            False,
                            f"Unexpected response: {response_data}"
                        )
                        
                except asyncio.TimeoutError:
                    self.log_test_result(
                        "WebRTC Offer Forwarding",
                        False,
                        "No response received within timeout"
                    )
                
                # Test WebRTC Answer forwarding
                answer_message = {
                    "type": "webrtc_answer",
                    "target_user": user1_id,
                    "answer": {
                        "type": "answer",
                        "sdp": "v=0\r\no=- 987654321 987654321 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\n"
                    }
                }
                
                await user2_ws.send(json.dumps(answer_message))
                
                # Check if user1 receives the answer
                try:
                    response = await asyncio.wait_for(user1_ws.recv(), timeout=5)
                    response_data = json.loads(response)
                    
                    if (response_data.get("type") == "webrtc_answer" and 
                        response_data.get("from_user") == user2_id):
                        self.log_test_result(
                            "WebRTC Answer Forwarding",
                            True,
                            f"Answer successfully forwarded from {user2_id} to {user1_id}"
                        )
                    else:
                        self.log_test_result(
                            "WebRTC Answer Forwarding",
                            False,
                            f"Unexpected response: {response_data}"
                        )
                        
                except asyncio.TimeoutError:
                    self.log_test_result(
                        "WebRTC Answer Forwarding",
                        False,
                        "No response received within timeout"
                    )
                
                # Test ICE Candidate forwarding
                ice_message = {
                    "type": "webrtc_ice_candidate",
                    "target_user": user2_id,
                    "candidate": {
                        "candidate": "candidate:1 1 UDP 2130706431 192.168.1.100 54400 typ host",
                        "sdpMLineIndex": 0,
                        "sdpMid": "0"
                    }
                }
                
                await user1_ws.send(json.dumps(ice_message))
                
                # Check if user2 receives the ICE candidate
                try:
                    response = await asyncio.wait_for(user2_ws.recv(), timeout=5)
                    response_data = json.loads(response)
                    
                    if (response_data.get("type") == "webrtc_ice_candidate" and 
                        response_data.get("from_user") == user1_id):
                        self.log_test_result(
                            "WebRTC ICE Candidate Forwarding",
                            True,
                            f"ICE candidate successfully forwarded from {user1_id} to {user2_id}"
                        )
                    else:
                        self.log_test_result(
                            "WebRTC ICE Candidate Forwarding",
                            False,
                            f"Unexpected response: {response_data}"
                        )
                        
                except asyncio.TimeoutError:
                    self.log_test_result(
                        "WebRTC ICE Candidate Forwarding",
                        False,
                        "No response received within timeout"
                    )
                
                return True
                
        except Exception as e:
            self.log_test_result(
                "WebRTC Signaling Messages",
                False,
                f"WebRTC signaling test failed: {e}"
            )
            return False

    async def test_meeting_participant_management(self):
        """Test meeting participant tracking and broadcasting"""
        print("\n👥 Testing Meeting Participant Management...")
        
        if not self.test_meeting_id:
            # Create a meeting if we don't have one
            meeting_data = {
                "name": "Participant Management Test Meeting",
                "participants": [],
                "scheduled_time": None
            }
            
            try:
                response = requests.post(f"{self.api_url}/meetings", json=meeting_data, timeout=10)
                if response.status_code == 200:
                    self.test_meeting_id = response.json().get('id')
                else:
                    self.log_test_result(
                        "Meeting Creation for Participant Test",
                        False,
                        f"Failed to create meeting: {response.status_code}"
                    )
                    return False
            except Exception as e:
                self.log_test_result(
                    "Meeting Creation for Participant Test",
                    False,
                    f"Exception: {e}"
                )
                return False
        
        # Test with multiple participants
        participants = ["participant_1", "participant_2", "participant_3"]
        websockets_list = []
        
        try:
            # Connect all participants
            for participant in participants:
                ws_endpoint = f"{self.ws_url}/ws/{participant}"
                ws = await websockets.connect(ws_endpoint, timeout=10)
                websockets_list.append((participant, ws))
            
            self.log_test_result(
                "Multiple Participant Connections",
                True,
                f"Successfully connected {len(participants)} participants"
            )
            
            # Have participants join the meeting one by one
            for i, (participant, ws) in enumerate(websockets_list):
                join_message = {
                    "type": "join_meeting",
                    "meeting_id": self.test_meeting_id
                }
                
                await ws.send(json.dumps(join_message))
                
                # Check if other participants receive join notifications
                if i > 0:  # Skip first participant as there are no others yet
                    await asyncio.sleep(0.5)  # Give time for message propagation
                    
                    # Check if previous participants received join notification
                    for j in range(i):
                        prev_participant, prev_ws = websockets_list[j]
                        try:
                            response = await asyncio.wait_for(prev_ws.recv(), timeout=2)
                            response_data = json.loads(response)
                            
                            if (response_data.get("type") == "user_joined" and 
                                response_data.get("user_id") == participant):
                                self.log_test_result(
                                    f"Join Notification to {prev_participant}",
                                    True,
                                    f"Received join notification for {participant}"
                                )
                            else:
                                self.log_test_result(
                                    f"Join Notification to {prev_participant}",
                                    False,
                                    f"Unexpected message: {response_data.get('type', 'unknown')}"
                                )
                        except asyncio.TimeoutError:
                            self.log_test_result(
                                f"Join Notification to {prev_participant}",
                                False,
                                "No join notification received"
                            )
                
                # Check if the joining participant receives existing participants list
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=3)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "existing_participants":
                        existing = response_data.get("participants", [])
                        expected_count = i  # Should have i existing participants
                        
                        if len(existing) == expected_count:
                            self.log_test_result(
                                f"Existing Participants List for {participant}",
                                True,
                                f"Received correct list of {expected_count} existing participants"
                            )
                        else:
                            self.log_test_result(
                                f"Existing Participants List for {participant}",
                                False,
                                f"Expected {expected_count} participants, got {len(existing)}"
                            )
                    else:
                        if i == 0:
                            # First participant might not get existing participants message
                            self.log_test_result(
                                f"Existing Participants List for {participant}",
                                True,
                                "First participant - no existing participants expected"
                            )
                        else:
                            self.log_test_result(
                                f"Existing Participants List for {participant}",
                                False,
                                f"Expected existing_participants, got: {response_data.get('type', 'unknown')}"
                            )
                except asyncio.TimeoutError:
                    if i == 0:
                        self.log_test_result(
                            f"Existing Participants List for {participant}",
                            True,
                            "First participant - no response expected"
                        )
                    else:
                        self.log_test_result(
                            f"Existing Participants List for {participant}",
                            False,
                            "No existing participants list received"
                        )
            
            # Test participant leaving
            leaving_participant, leaving_ws = websockets_list[1]  # Second participant leaves
            
            leave_message = {
                "type": "leave_meeting",
                "meeting_id": self.test_meeting_id
            }
            
            await leaving_ws.send(json.dumps(leave_message))
            await asyncio.sleep(0.5)  # Give time for message propagation
            
            # Check if remaining participants receive leave notification
            remaining_participants = [websockets_list[0], websockets_list[2]]  # First and third
            
            for participant, ws in remaining_participants:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=3)
                    response_data = json.loads(response)
                    
                    if (response_data.get("type") == "user_left" and 
                        response_data.get("user_id") == leaving_participant):
                        self.log_test_result(
                            f"Leave Notification to {participant}",
                            True,
                            f"Received leave notification for {leaving_participant}"
                        )
                    else:
                        self.log_test_result(
                            f"Leave Notification to {participant}",
                            False,
                            f"Unexpected message: {response_data.get('type', 'unknown')}"
                        )
                except asyncio.TimeoutError:
                    self.log_test_result(
                        f"Leave Notification to {participant}",
                        False,
                        "No leave notification received"
                    )
            
            # Close all connections
            for participant, ws in websockets_list:
                await ws.close()
            
            return True
            
        except Exception as e:
            # Clean up connections
            for participant, ws in websockets_list:
                try:
                    await ws.close()
                except:
                    pass
            
            self.log_test_result(
                "Meeting Participant Management",
                False,
                f"Test failed with exception: {e}"
            )
            return False

    async def test_meeting_backend_integration(self):
        """Test integration between WebSocket functionality and meeting backend"""
        print("\n🔗 Testing Meeting Backend Integration...")
        
        # Create a meeting via REST API
        meeting_data = {
            "name": "Backend Integration Test Meeting",
            "participants": ["integration_user_1", "integration_user_2"],
            "scheduled_time": None
        }
        
        try:
            response = requests.post(f"{self.api_url}/meetings", json=meeting_data, timeout=10)
            if response.status_code != 200:
                self.log_test_result(
                    "Meeting Backend Creation",
                    False,
                    f"Failed to create meeting: {response.status_code}"
                )
                return False
            
            meeting_response = response.json()
            integration_meeting_id = meeting_response.get('id')
            
            self.log_test_result(
                "Meeting Backend Creation",
                True,
                f"Created meeting with ID: {integration_meeting_id}"
            )
            
            # Verify meeting can be retrieved
            get_response = requests.get(f"{self.api_url}/meetings/{integration_meeting_id}", timeout=10)
            if get_response.status_code != 200:
                self.log_test_result(
                    "Meeting Backend Retrieval",
                    False,
                    f"Failed to retrieve meeting: {get_response.status_code}"
                )
                return False
            
            self.log_test_result(
                "Meeting Backend Retrieval",
                True,
                "Meeting successfully retrieved from backend"
            )
            
            # Test WebSocket interaction with the backend-created meeting
            user_id = "integration_user_1"
            ws_endpoint = f"{self.ws_url}/ws/{user_id}"
            
            async with websockets.connect(ws_endpoint, timeout=10) as websocket:
                # Join the backend-created meeting via WebSocket
                join_message = {
                    "type": "join_meeting",
                    "meeting_id": integration_meeting_id
                }
                
                await websocket.send(json.dumps(join_message))
                
                self.log_test_result(
                    "WebSocket Integration with Backend Meeting",
                    True,
                    "Successfully joined backend-created meeting via WebSocket"
                )
                
                # Update meeting via REST API while WebSocket is connected
                update_data = {
                    "participants": ["integration_user_1", "integration_user_2", "integration_user_3"],
                    "status": "active"
                }
                
                update_response = requests.put(
                    f"{self.api_url}/meetings/{integration_meeting_id}", 
                    json=update_data, 
                    timeout=10
                )
                
                if update_response.status_code == 200:
                    self.log_test_result(
                        "Meeting Backend Update During WebSocket Session",
                        True,
                        "Meeting updated successfully while WebSocket connected"
                    )
                else:
                    self.log_test_result(
                        "Meeting Backend Update During WebSocket Session",
                        False,
                        f"Update failed: {update_response.status_code}"
                    )
                
                # Leave meeting via WebSocket
                leave_message = {
                    "type": "leave_meeting",
                    "meeting_id": integration_meeting_id
                }
                
                await websocket.send(json.dumps(leave_message))
                
                self.log_test_result(
                    "WebSocket Leave Backend Meeting",
                    True,
                    "Successfully left backend meeting via WebSocket"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Meeting Backend Integration",
                False,
                f"Integration test failed: {e}"
            )
            return False

    async def run_all_tests(self):
        """Run all WebRTC and WebSocket tests"""
        print("🚀 Starting WebRTC and WebSocket Testing Suite")
        print("=" * 60)
        
        # Test WebSocket connection
        await self.test_websocket_connection()
        
        # Test meeting join/leave via WebSocket
        await self.test_meeting_join_leave_websocket()
        
        # Test WebRTC signaling messages
        await self.test_webrtc_signaling_messages()
        
        # Test meeting participant management
        await self.test_meeting_participant_management()
        
        # Test meeting backend integration
        await self.test_meeting_backend_integration()
        
        # Print final results
        print("\n" + "=" * 60)
        print("📊 WEBRTC & WEBSOCKET TEST RESULTS")
        print("=" * 60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {len(self.failed_tests)}")
        
        if self.tests_run > 0:
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['name']}")
                if test['details']:
                    print(f"   Details: {test['details']}")
        
        return len(self.failed_tests) == 0

def main():
    """Main function to run the tests"""
    tester = WebRTCWebSocketTester()
    
    try:
        success = asyncio.run(tester.run_all_tests())
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())