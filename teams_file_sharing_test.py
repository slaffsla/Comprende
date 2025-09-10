import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import tempfile
import os
import uuid

class TeamsFileShareTester:
    def __init__(self, base_url="https://translate-hub-22.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_team_id = None
        self.test_invite_code = None
        self.test_file_id = None
        self.test_shared_file_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        
        if headers is None:
            headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response preview: {str(response_data)[:200]}...")
                    return True, response_data
                except:
                    return True, response.text[:200]
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:300]
                })
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            self.failed_tests.append({'name': name, 'error': 'Timeout'})
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({'name': name, 'error': str(e)})
            return False, {}

    def test_team_creation(self):
        """Test team creation with name and description"""
        team_data = {
            "name": "Test Development Team",
            "description": "A team for testing comprehensive team and file sharing functionality"
        }
        
        success, response = self.run_test(
            "Team Creation",
            "POST",
            "teams",
            200,
            data=team_data
        )
        
        if success:
            self.test_team_id = response.get('id', '')
            self.test_invite_code = response.get('invite_code', '')
            
            print(f"   Team ID: {self.test_team_id}")
            print(f"   Team Name: {response.get('name', '')}")
            print(f"   Description: {response.get('description', '')}")
            print(f"   Invite Code: {self.test_invite_code}")
            print(f"   Created By: {response.get('created_by', '')}")
            print(f"   Members: {response.get('members', [])}")
            
            # Verify UUID format for team ID
            if self.test_team_id and len(self.test_team_id) == 36 and self.test_team_id.count('-') == 4:
                print("   ✅ Team ID is proper UUID format")
            else:
                print("   ❌ Team ID is not proper UUID format")
                self.failed_tests.append({
                    'name': 'Team ID Format',
                    'expected': 'UUID format',
                    'actual': f'ID: {self.test_team_id}',
                    'response': 'Team ID should be UUID format'
                })
            
            # Verify invite code format
            if self.test_invite_code and len(self.test_invite_code) == 8:
                print("   ✅ Invite code is proper 8-character format")
            else:
                print("   ❌ Invite code format issue")
            
            # Verify creator is automatically added as member
            members = response.get('members', [])
            if 'demo-user' in members:
                print("   ✅ Creator automatically added as team member")
            else:
                print("   ❌ Creator not automatically added as member")
        
        return success

    def test_get_user_teams(self):
        """Test getting user teams"""
        success, response = self.run_test(
            "Get User Teams",
            "GET",
            "teams",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Found {len(response)} teams for user")
                
                # Check if our test team is in the list
                test_team_found = False
                if self.test_team_id:
                    for team in response:
                        if team.get('id') == self.test_team_id:
                            test_team_found = True
                            print("   ✅ Test team found in user teams list")
                            break
                    
                    if not test_team_found:
                        print("   ❌ Test team not found in user teams list")
                        self.failed_tests.append({
                            'name': 'Test Team in User Teams',
                            'expected': 'Test team in list',
                            'actual': 'Test team not found',
                            'response': 'Created team should appear in user teams'
                        })
                
                # Verify no ObjectId fields
                objectid_found = False
                for team in response:
                    if '_id' in team:
                        objectid_found = True
                        break
                
                if objectid_found:
                    print("   ❌ MongoDB ObjectId fields found in teams list")
                    self.failed_tests.append({
                        'name': 'Teams List ObjectId Cleanup',
                        'expected': 'No _id fields',
                        'actual': '_id fields present',
                        'response': 'ObjectId fields should be removed'
                    })
                else:
                    print("   ✅ No MongoDB ObjectId fields in teams list")
            else:
                print(f"   Unexpected response format: {type(response)}")
        
        return success

    def test_get_specific_team(self):
        """Test getting specific team details"""
        if not self.test_team_id:
            print("   ⚠️  Skipping specific team test - no team ID from creation")
            return False
        
        success, response = self.run_test(
            "Get Specific Team Details",
            "GET",
            f"teams/{self.test_team_id}",
            200
        )
        
        if success:
            print(f"   Retrieved Team ID: {response.get('id', '')}")
            print(f"   Team Name: {response.get('name', '')}")
            print(f"   Description: {response.get('description', '')}")
            print(f"   Members: {response.get('members', [])}")
            print(f"   Invite Code: {response.get('invite_code', '')}")
            
            # Verify no ObjectId fields
            if '_id' in response:
                print("   ❌ MongoDB ObjectId field found in response")
                self.failed_tests.append({
                    'name': 'Team Details ObjectId Cleanup',
                    'expected': 'No _id field',
                    'actual': '_id field present',
                    'response': 'ObjectId should be removed'
                })
            else:
                print("   ✅ No MongoDB ObjectId fields in response")
            
            # Verify team data integrity
            if response.get('id') == self.test_team_id:
                print("   ✅ Team ID matches created team")
            else:
                print("   ❌ Team ID mismatch")
        
        return success

    def test_join_team_with_invite_code(self):
        """Test joining team with invite code"""
        if not self.test_invite_code:
            print("   ⚠️  Skipping join team test - no invite code from creation")
            return False
        
        join_data = {
            "invite_code": self.test_invite_code,
            "user_id": "test-user-2"
        }
        
        success, response = self.run_test(
            "Join Team with Invite Code",
            "POST",
            "teams/join",
            200,
            data=join_data
        )
        
        if success:
            print(f"   Team ID: {response.get('id', '')}")
            print(f"   Team Name: {response.get('name', '')}")
            print(f"   Updated Members: {response.get('members', [])}")
            
            # Verify new member was added
            members = response.get('members', [])
            if 'test-user-2' in members:
                print("   ✅ New member successfully added to team")
            else:
                print("   ❌ New member not added to team")
                self.failed_tests.append({
                    'name': 'Team Member Addition',
                    'expected': 'test-user-2 in members',
                    'actual': f'Members: {members}',
                    'response': 'New member should be added to team'
                })
            
            # Verify original member still exists
            if 'demo-user' in members:
                print("   ✅ Original team creator still in members")
            else:
                print("   ❌ Original team creator missing from members")
        
        return success

    def test_join_team_invalid_code(self):
        """Test joining team with invalid invite code"""
        join_data = {
            "invite_code": "INVALID1",
            "user_id": "test-user-3"
        }
        
        success, response = self.run_test(
            "Join Team with Invalid Invite Code",
            "POST",
            "teams/join",
            404,
            data=join_data
        )
        
        if success:
            print("   ✅ Proper 404 response for invalid invite code")
        
        return success

    def test_update_team_details(self):
        """Test updating team details"""
        if not self.test_team_id:
            print("   ⚠️  Skipping team update test - no team ID from creation")
            return False
        
        update_data = {
            "name": "Updated Development Team",
            "description": "Updated description for comprehensive testing",
            "settings": {
                "file_sharing_enabled": True,
                "max_file_size": "10MB",
                "allowed_file_types": ["pdf", "txt", "jpg", "png"]
            }
        }
        
        success, response = self.run_test(
            "Update Team Details",
            "PUT",
            f"teams/{self.test_team_id}",
            200,
            data=update_data
        )
        
        if success:
            print(f"   Updated Name: {response.get('name', '')}")
            print(f"   Updated Description: {response.get('description', '')}")
            print(f"   Updated Settings: {response.get('settings', {})}")
            
            # Verify updates were applied
            if response.get('name') == "Updated Development Team":
                print("   ✅ Team name updated successfully")
            else:
                print("   ❌ Team name update failed")
            
            if response.get('description') == "Updated description for comprehensive testing":
                print("   ✅ Team description updated successfully")
            else:
                print("   ❌ Team description update failed")
            
            if response.get('settings', {}).get('file_sharing_enabled') == True:
                print("   ✅ Team settings updated successfully")
            else:
                print("   ❌ Team settings update failed")
        
        return success

    def test_upload_team_file(self):
        """Test uploading file to team workspace"""
        if not self.test_team_id:
            print("   ⚠️  Skipping team file upload - no team ID from creation")
            return False
        
        # Create a test file
        test_content = """Team Collaboration Document
        
This is a test document for team file sharing functionality.
It contains important project information and collaboration notes.

Features to test:
- File upload to team workspace
- File metadata (description, tags)
- Access permissions for team members
- File download functionality
- File deletion with proper permissions

Team: Test Development Team
Created: """ + datetime.now().isoformat()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('team_collaboration_doc.txt', f, 'text/plain')}
                data = {
                    'description': 'Team collaboration document for testing file sharing',
                    'tags': 'testing,collaboration,documentation'
                }
                
                success, response = self.run_test(
                    "Upload Team File",
                    "POST",
                    f"teams/{self.test_team_id}/files/upload",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    self.test_file_id = response.get('file_id', '')
                    print(f"   File ID: {self.test_file_id}")
                    print(f"   Filename: {response.get('filename', '')}")
                    print(f"   Team ID: {response.get('team_id', '')}")
                    print(f"   Message: {response.get('message', '')}")
                    
                    # Verify file ID is UUID format
                    if self.test_file_id and len(self.test_file_id) == 36:
                        print("   ✅ File ID is proper UUID format")
                    else:
                        print("   ❌ File ID format issue")
                    
                    # Verify team ID matches
                    if response.get('team_id') == self.test_team_id:
                        print("   ✅ File uploaded to correct team")
                    else:
                        print("   ❌ File team ID mismatch")
                
                return success
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_get_team_files(self):
        """Test getting team files"""
        if not self.test_team_id:
            print("   ⚠️  Skipping get team files - no team ID from creation")
            return False
        
        success, response = self.run_test(
            "Get Team Files",
            "GET",
            f"teams/{self.test_team_id}/files",
            200
        )
        
        if success:
            print(f"   Team ID: {response.get('team_id', '')}")
            print(f"   Team Name: {response.get('team_name', '')}")
            
            files = response.get('files', [])
            print(f"   Found {len(files)} files in team")
            
            # Check if our test file is in the list
            test_file_found = False
            if self.test_file_id:
                for file_obj in files:
                    if hasattr(file_obj, 'id') and file_obj.id == self.test_file_id:
                        test_file_found = True
                        print("   ✅ Test file found in team files")
                        print(f"   File details: {file_obj.original_name}, {file_obj.description}")
                        break
                    elif isinstance(file_obj, dict) and file_obj.get('id') == self.test_file_id:
                        test_file_found = True
                        print("   ✅ Test file found in team files")
                        print(f"   File details: {file_obj.get('original_name')}, {file_obj.get('description')}")
                        break
                
                if not test_file_found:
                    print("   ❌ Test file not found in team files")
                    self.failed_tests.append({
                        'name': 'Test File in Team Files',
                        'expected': 'Test file in list',
                        'actual': 'Test file not found',
                        'response': 'Uploaded file should appear in team files'
                    })
            
            # Verify file metadata
            if files:
                first_file = files[0]
                if isinstance(first_file, dict):
                    print(f"   File metadata: tags={first_file.get('tags', [])}, size={first_file.get('file_size', 0)}")
                else:
                    print(f"   File metadata: tags={getattr(first_file, 'tags', [])}, size={getattr(first_file, 'file_size', 0)}")
        
        return success

    def test_download_team_file(self):
        """Test downloading team file"""
        if not self.test_team_id or not self.test_file_id:
            print("   ⚠️  Skipping team file download - missing team ID or file ID")
            return False
        
        success, response = self.run_test(
            "Download Team File",
            "GET",
            f"teams/{self.test_team_id}/files/{self.test_file_id}/download",
            200
        )
        
        if success:
            print("   ✅ Team file download successful")
            # For file downloads, response might be binary content
            if isinstance(response, str) and len(response) > 0:
                print(f"   Downloaded content preview: {response[:100]}...")
            else:
                print("   Downloaded file content (binary)")
        
        return success

    def test_enhanced_file_sharing(self):
        """Test enhanced file sharing with team support"""
        if not self.test_team_id:
            print("   ⚠️  Skipping enhanced file sharing - no team ID")
            return False
        
        # Create a test file for sharing
        share_content = """Shared Project Document

This document is being shared with the team using enhanced file sharing functionality.

Key Features:
- Team-based sharing
- Access level controls
- File descriptions and tags
- Notification system for recipients

Shared by: demo-user
Team: Test Development Team
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(share_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('shared_project_doc.txt', f, 'text/plain')}
                data = {
                    'team_id': self.test_team_id,
                    'access_level': 'read',
                    'description': 'Shared project document with team collaboration features',
                    'tags': 'project,shared,collaboration'
                }
                
                success, response = self.run_test(
                    "Enhanced File Sharing with Team Support",
                    "POST",
                    "files/share",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    self.test_shared_file_id = response.get('file_id', '')
                    print(f"   Shared File ID: {self.test_shared_file_id}")
                    print(f"   Shared with: {response.get('shared_with', 0)} users")
                    print(f"   Team context: {response.get('team_context', False)}")
                    print(f"   Message: {response.get('message', '')}")
                    
                    # Verify team context
                    if response.get('team_context') == True:
                        print("   ✅ File shared with team context")
                    else:
                        print("   ❌ Team context not properly set")
                    
                    # Verify shared file ID format
                    if self.test_shared_file_id and len(self.test_shared_file_id) == 36:
                        print("   ✅ Shared file ID is proper UUID format")
                    else:
                        print("   ❌ Shared file ID format issue")
                
                return success
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_get_shared_files(self):
        """Test getting shared files with team filtering"""
        success, response = self.run_test(
            "Get Shared Files",
            "GET",
            "files/shared",
            200
        )
        
        if success:
            files = response.get('files', [])
            total_files = response.get('total_files', 0)
            team_filter = response.get('team_filter', None)
            
            print(f"   Total shared files: {total_files}")
            print(f"   Team filter: {team_filter}")
            print(f"   Files found: {len(files)}")
            
            # Check if our shared file is in the list
            shared_file_found = False
            if self.test_shared_file_id:
                for file_obj in files:
                    file_id = file_obj.get('id') if isinstance(file_obj, dict) else getattr(file_obj, 'id', None)
                    if file_id == self.test_shared_file_id:
                        shared_file_found = True
                        print("   ✅ Test shared file found in shared files")
                        break
                
                if not shared_file_found:
                    print("   ❌ Test shared file not found in shared files")
        
        return success

    def test_get_shared_files_with_team_filter(self):
        """Test getting shared files with team filtering"""
        if not self.test_team_id:
            print("   ⚠️  Skipping team-filtered shared files - no team ID")
            return False
        
        success, response = self.run_test(
            "Get Shared Files with Team Filter",
            "GET",
            f"files/shared?team_id={self.test_team_id}",
            200
        )
        
        if success:
            files = response.get('files', [])
            total_files = response.get('total_files', 0)
            team_filter = response.get('team_filter', None)
            
            print(f"   Total team-filtered files: {total_files}")
            print(f"   Team filter applied: {team_filter}")
            print(f"   Files found: {len(files)}")
            
            # Verify team filter was applied
            if team_filter == self.test_team_id:
                print("   ✅ Team filter properly applied")
            else:
                print("   ❌ Team filter not properly applied")
        
        return success

    def test_remove_team_member(self):
        """Test removing team member"""
        if not self.test_team_id:
            print("   ⚠️  Skipping remove team member - no team ID")
            return False
        
        # Remove the member we added earlier
        success, response = self.run_test(
            "Remove Team Member",
            "DELETE",
            f"teams/{self.test_team_id}/members/test-user-2",
            200
        )
        
        if success:
            print(f"   Message: {response.get('message', '')}")
            
            # Verify member was removed by getting team details
            verify_success, verify_response = self.run_test(
                "Verify Member Removal",
                "GET",
                f"teams/{self.test_team_id}",
                200
            )
            
            if verify_success:
                members = verify_response.get('members', [])
                if 'test-user-2' not in members:
                    print("   ✅ Member successfully removed from team")
                else:
                    print("   ❌ Member still in team after removal")
                    self.failed_tests.append({
                        'name': 'Team Member Removal',
                        'expected': 'test-user-2 not in members',
                        'actual': f'Members: {members}',
                        'response': 'Member should be removed from team'
                    })
        
        return success

    def test_delete_team_file(self):
        """Test deleting team file"""
        if not self.test_team_id or not self.test_file_id:
            print("   ⚠️  Skipping team file deletion - missing team ID or file ID")
            return False
        
        success, response = self.run_test(
            "Delete Team File",
            "DELETE",
            f"teams/{self.test_team_id}/files/{self.test_file_id}",
            200
        )
        
        if success:
            print(f"   Message: {response.get('message', '')}")
            
            # Verify file was deleted by trying to get team files
            verify_success, verify_response = self.run_test(
                "Verify File Deletion",
                "GET",
                f"teams/{self.test_team_id}/files",
                200
            )
            
            if verify_success:
                files = verify_response.get('files', [])
                file_found = False
                for file_obj in files:
                    file_id = file_obj.get('id') if isinstance(file_obj, dict) else getattr(file_obj, 'id', None)
                    if file_id == self.test_file_id:
                        file_found = True
                        break
                
                if not file_found:
                    print("   ✅ File successfully deleted from team")
                else:
                    print("   ❌ File still exists after deletion")
                    self.failed_tests.append({
                        'name': 'Team File Deletion',
                        'expected': 'File not in team files',
                        'actual': 'File still exists',
                        'response': 'File should be deleted from team'
                    })
        
        return success

    def test_access_control_verification(self):
        """Test access control for team operations"""
        if not self.test_team_id:
            print("   ⚠️  Skipping access control test - no team ID")
            return False
        
        # Test accessing team with unauthorized user
        success, response = self.run_test(
            "Access Control - Unauthorized Team Access",
            "GET",
            f"teams/{self.test_team_id}?user_id=unauthorized-user",
            403
        )
        
        if success:
            print("   ✅ Proper 403 response for unauthorized team access")
        
        # Test uploading file with unauthorized user
        test_content = "Unauthorized upload attempt"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('unauthorized.txt', f, 'text/plain')}
                data = {'user_id': 'unauthorized-user'}
                
                upload_success, upload_response = self.run_test(
                    "Access Control - Unauthorized File Upload",
                    "POST",
                    f"teams/{self.test_team_id}/files/upload",
                    403,
                    data=data,
                    files=files
                )
                
                if upload_success:
                    print("   ✅ Proper 403 response for unauthorized file upload")
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        return success and upload_success

    def test_team_not_found_scenarios(self):
        """Test various team not found scenarios"""
        invalid_team_id = "00000000-0000-0000-0000-000000000000"
        
        # Test getting non-existent team
        success1, response1 = self.run_test(
            "Team Not Found - Get Team",
            "GET",
            f"teams/{invalid_team_id}",
            404
        )
        
        # Test uploading to non-existent team
        test_content = "Test upload to non-existent team"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                
                success2, response2 = self.run_test(
                    "Team Not Found - File Upload",
                    "POST",
                    f"teams/{invalid_team_id}/files/upload",
                    404,
                    files=files
                )
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        # Test updating non-existent team
        success3, response3 = self.run_test(
            "Team Not Found - Update Team",
            "PUT",
            f"teams/{invalid_team_id}",
            404,
            data={"name": "Updated Name"}
        )
        
        if success1 and success2 and success3:
            print("   ✅ All team not found scenarios handled properly")
        
        return success1 and success2 and success3

def main():
    print("🚀 Starting Teams and File Sharing API Testing Suite")
    print("=" * 70)
    
    tester = TeamsFileShareTester()
    
    # Team Management Tests
    print("\n👥 TEAM MANAGEMENT TESTS")
    print("-" * 40)
    tester.test_team_creation()
    tester.test_get_user_teams()
    tester.test_get_specific_team()
    tester.test_join_team_with_invite_code()
    tester.test_join_team_invalid_code()
    tester.test_update_team_details()
    
    # Team File Sharing Tests
    print("\n📁 TEAM FILE SHARING TESTS")
    print("-" * 40)
    tester.test_upload_team_file()
    tester.test_get_team_files()
    tester.test_download_team_file()
    tester.test_delete_team_file()
    
    # Enhanced File Sharing Tests
    print("\n🔗 ENHANCED FILE SHARING TESTS")
    print("-" * 40)
    tester.test_enhanced_file_sharing()
    tester.test_get_shared_files()
    tester.test_get_shared_files_with_team_filter()
    
    # Access Control and Security Tests
    print("\n🔒 ACCESS CONTROL & SECURITY TESTS")
    print("-" * 40)
    tester.test_access_control_verification()
    tester.test_team_not_found_scenarios()
    tester.test_remove_team_member()
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS")
    print("=" * 70)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(tester.failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.failed_tests:
        print("\n❌ FAILED TESTS:")
        for i, test in enumerate(tester.failed_tests, 1):
            print(f"{i}. {test['name']}")
            if 'expected' in test:
                print(f"   Expected: {test['expected']}, Got: {test['actual']}")
            if 'error' in test:
                print(f"   Error: {test['error']}")
            if 'response' in test:
                print(f"   Response: {test['response']}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())