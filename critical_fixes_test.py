#!/usr/bin/env python3
"""
Critical Fixes Testing Suite for Comprende App
Focus: PDF download issue and document processing fixes
"""

import requests
import sys
import json
import time
import tempfile
import os
from pathlib import Path

class CriticalFixesTester:
    def __init__(self, base_url="https://translate-hub-22.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_issues = []

    def log_critical_issue(self, test_name, issue_description):
        """Log critical issues that need immediate attention"""
        self.critical_issues.append({
            'test': test_name,
            'issue': issue_description
        })
        print(f"🚨 CRITICAL ISSUE: {issue_description}")

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

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        response_data = response.json()
                        return True, response_data
                    else:
                        return True, response.text
                except:
                    return True, response.text
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

    def test_pdf_document_processing_german(self):
        """Test PDF processing with German filename to verify no sample text"""
        print("\n🎯 CRITICAL TEST: PDF Document Processing (German)")
        
        # Create a temporary PDF-like file with German filename
        german_content = "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee, begleitet von den süßen Klängen der Glöckchen am Zaumzeug der Haflinger, erfüllt die klare Bergluft mit einer Musik, die das Herz berührt."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, prefix='german_') as f:
            f.write(german_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('german.pdf', f, 'application/pdf')}
                data = {
                    'languages': 'deu',
                    'translate_to': 'eng'
                }
                
                success, response = self.run_test(
                    "PDF Processing - German Document",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    extracted_text = response.get('extracted_text', '')
                    detected_lang = response.get('detected_language', '')
                    
                    print(f"   Detected language: {detected_lang}")
                    print(f"   Extracted text preview: {extracted_text[:100]}...")
                    
                    # CRITICAL CHECK: Verify it's NOT the problematic sample text
                    if extracted_text.startswith("Sample extracted text from PDF document"):
                        self.log_critical_issue(
                            "PDF Processing",
                            "PDF processing still returns sample text instead of actual content"
                        )
                        return False
                    
                    # CRITICAL CHECK: Verify language detection
                    if detected_lang != 'deu':
                        self.log_critical_issue(
                            "Language Detection",
                            f"German text detected as '{detected_lang}' instead of 'deu'"
                        )
                    
                    print("   ✅ PDF processing returns actual content (not sample text)")
                    return True
                
                return success
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_pdf_document_processing_hebrew(self):
        """Test PDF processing with Hebrew filename"""
        print("\n🎯 CRITICAL TEST: PDF Document Processing (Hebrew)")
        
        hebrew_content = "שלום עולם! זהו מסמך PDF בעברית לבדיקת עיבוד מסמכים."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, prefix='hebrew_', encoding='utf-8') as f:
            f.write(hebrew_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('hebrew.pdf', f, 'application/pdf')}
                data = {
                    'languages': 'heb',
                    'translate_to': 'eng'
                }
                
                success, response = self.run_test(
                    "PDF Processing - Hebrew Document",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    extracted_text = response.get('extracted_text', '')
                    detected_lang = response.get('detected_language', '')
                    
                    print(f"   Detected language: {detected_lang}")
                    print(f"   Extracted text preview: {extracted_text[:100]}...")
                    
                    # CRITICAL CHECK: Verify it's NOT the problematic sample text
                    if extracted_text.startswith("Sample extracted text from PDF document"):
                        self.log_critical_issue(
                            "PDF Processing",
                            "PDF processing still returns sample text instead of actual content"
                        )
                        return False
                    
                    print("   ✅ PDF processing returns actual content (not sample text)")
                    return True
                
                return success
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_download_functionality_with_translation(self):
        """Test download functionality with actual translated content"""
        print("\n🎯 CRITICAL TEST: Download Functionality with Translation")
        
        # First, perform a translation to get actual content
        german_text = "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee"
        
        translation_data = {
            "text": german_text,
            "source_language": "deu",
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        # Get translation
        success, translation_response = self.run_test(
            "Translation for Download Test",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if not success:
            self.log_critical_issue("Translation Service", "Translation failed - cannot test download")
            return False
        
        translated_text = translation_response.get('translated_text', '')
        if not translated_text:
            self.log_critical_issue("Translation Service", "No translated text returned")
            return False
        
        print(f"   Translation result: {translated_text[:100]}...")
        
        # Now test download with the translated content
        download_data = {
            "content": translated_text,
            "filename": "german_to_english_translation.txt"
        }
        
        success, download_response = self.run_test(
            "Download Translated Content",
            "POST",
            "documents/download",
            200,
            data=download_data
        )
        
        if success:
            # CRITICAL CHECK: Verify the download doesn't return sample text
            if isinstance(download_response, str) and "Sample extracted text" in download_response:
                self.log_critical_issue(
                    "Download Functionality",
                    "Download endpoint returns sample text instead of actual content"
                )
                return False
            
            print("   ✅ Download returns actual content (not sample text)")
            return True
        
        return success

    def test_german_language_detection_critical(self):
        """Critical test for German language detection as mentioned in review"""
        print("\n🎯 CRITICAL TEST: German Language Detection")
        
        # Exact text from review request
        german_text = "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee..."
        
        translation_data = {
            "text": german_text,
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "German Language Detection (Critical)",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            detected_lang = response.get('source_language', '')
            print(f"   German text: {german_text[:50]}...")
            print(f"   Detected language: {detected_lang}")
            
            # CRITICAL CHECK: Must be detected as 'deu' (German)
            if detected_lang != 'deu':
                self.log_critical_issue(
                    "German Language Detection",
                    f"German text detected as '{detected_lang}' instead of 'deu' - CRITICAL ISSUE NOT FIXED"
                )
                return False
            
            print("   ✅ German language correctly detected as 'deu'")
            
            # Also check translation quality
            translated_text = response.get('translated_text', '')
            confidence = response.get('confidence', 0)
            print(f"   Translation: {translated_text[:100]}...")
            print(f"   Confidence: {confidence*100:.1f}%")
            
            return True
        
        return success

    def test_user_management(self):
        """Test user creation and management"""
        print("\n🎯 TEST: User Management")
        
        user_data = {
            "username": "test_user_critical",
            "email": "test@comprende.com",
            "preferred_languages": ["eng", "deu", "heb", "ara"]
        }
        
        success, response = self.run_test(
            "User Creation",
            "POST",
            "users",
            200,
            data=user_data
        )
        
        if success:
            user_id = response.get('id', '')
            print(f"   Created user ID: {user_id}")
            print(f"   Username: {response.get('username', '')}")
            print(f"   Email: {response.get('email', '')}")
            
            # Test user retrieval
            if user_id:
                success2, user_response = self.run_test(
                    "User Retrieval",
                    "GET",
                    f"users/{user_id}",
                    200
                )
                
                if success2:
                    print("   ✅ User creation and retrieval working")
                    return True
        
        return success

    def test_download_with_different_content_types(self):
        """Test download with different types of content"""
        print("\n🎯 CRITICAL TEST: Download with Various Content Types")
        
        test_contents = [
            {
                "content": "This is actual document content extracted from a real PDF file.",
                "filename": "real_pdf_content.txt",
                "description": "Real PDF content"
            },
            {
                "content": "זהו תוכן אמיתי שחולץ ממסמך עברי.",
                "filename": "hebrew_content.txt", 
                "description": "Hebrew content"
            },
            {
                "content": "Dies ist echter deutscher Inhalt aus einem verarbeiteten Dokument.",
                "filename": "german_content.txt",
                "description": "German content"
            }
        ]
        
        all_passed = True
        
        for test_content in test_contents:
            download_data = {
                "content": test_content["content"],
                "filename": test_content["filename"]
            }
            
            success, response = self.run_test(
                f"Download {test_content['description']}",
                "POST",
                "documents/download",
                200,
                data=download_data
            )
            
            if success:
                # CRITICAL CHECK: Verify no sample text
                if isinstance(response, str) and "Sample extracted text" in response:
                    self.log_critical_issue(
                        "Download Functionality",
                        f"Download returns sample text for {test_content['description']}"
                    )
                    all_passed = False
                else:
                    print(f"   ✅ {test_content['description']} download working correctly")
            else:
                all_passed = False
        
        return all_passed

def main():
    print("🚀 Starting CRITICAL FIXES Testing Suite")
    print("Focus: PDF download issue and document processing fixes")
    print("=" * 70)
    
    tester = CriticalFixesTester()
    
    # Critical PDF Processing Tests
    print("\n📄 CRITICAL PDF PROCESSING TESTS")
    print("-" * 40)
    tester.test_pdf_document_processing_german()
    tester.test_pdf_document_processing_hebrew()
    
    # Critical Download Functionality Tests
    print("\n📥 CRITICAL DOWNLOAD FUNCTIONALITY TESTS")
    print("-" * 40)
    tester.test_download_functionality_with_translation()
    tester.test_download_with_different_content_types()
    
    # Critical Language Detection Tests
    print("\n🔍 CRITICAL LANGUAGE DETECTION TESTS")
    print("-" * 40)
    tester.test_german_language_detection_critical()
    
    # User Management Tests
    print("\n👤 USER MANAGEMENT TESTS")
    print("-" * 30)
    tester.test_user_management()
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 CRITICAL FIXES TEST RESULTS")
    print("=" * 70)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(tester.failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    # Report critical issues
    if tester.critical_issues:
        print("\n🚨 CRITICAL ISSUES FOUND:")
        print("=" * 40)
        for i, issue in enumerate(tester.critical_issues, 1):
            print(f"{i}. {issue['test']}: {issue['issue']}")
        print("\n⚠️  These issues need IMMEDIATE attention!")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND - All fixes working correctly!")
    
    if tester.failed_tests:
        print("\n❌ FAILED TESTS:")
        for i, test in enumerate(tester.failed_tests, 1):
            print(f"{i}. {test['name']}")
            if 'expected' in test:
                print(f"   Expected: {test['expected']}, Got: {test['actual']}")
            if 'error' in test:
                print(f"   Error: {test['error']}")
    
    return 0 if len(tester.critical_issues) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())