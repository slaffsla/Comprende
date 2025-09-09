import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import tempfile
import os

class ComprehendeAPITester:
    def __init__(self, base_url="https://translatify-8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

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

    def test_health_check(self):
        """Test system health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        if success:
            print(f"   System status: {response.get('status', 'unknown')}")
            if 'components' in response:
                for component, status in response['components'].items():
                    print(f"   - {component}: {status}")
        return success

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_supported_languages(self):
        """Test supported languages endpoint"""
        success, response = self.run_test(
            "Supported Languages",
            "GET",
            "languages/supported",
            200
        )
        if success and 'languages' in response:
            print(f"   Supported languages: {len(response['languages'])}")
        return success

    def test_basic_translation(self):
        """Test basic text translation"""
        translation_data = {
            "text": "Hello, how are you today?",
            "source_language": "eng",
            "target_language": "spa",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "Basic Translation (English to Spanish)",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            print(f"   Original: {response.get('original_text', '')}")
            print(f"   Translated: {response.get('translated_text', '')}")
            print(f"   Confidence: {response.get('confidence', 0)*100:.1f}%")
            print(f"   Processing time: {response.get('processing_time', 0):.2f}s")
        
        return success

    def test_auto_detect_translation(self):
        """Test translation with auto language detection"""
        translation_data = {
            "text": "Bonjour, comment allez-vous?",
            "target_language": "eng",
            "context": "casual",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "Auto-detect Translation (French to English)",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            print(f"   Detected language: {response.get('source_language', 'unknown')}")
            print(f"   Translated: {response.get('translated_text', '')}")
        
        return success

    def test_rtl_translation(self):
        """Test RTL language translation"""
        translation_data = {
            "text": "Hello world",
            "source_language": "eng",
            "target_language": "heb",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "RTL Translation (English to Hebrew)",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            print(f"   Hebrew translation: {response.get('translated_text', '')}")
        
        return success

    def test_industry_context_translation(self):
        """Test translation with industry context"""
        translation_data = {
            "text": "The patient needs immediate medical attention",
            "source_language": "eng",
            "target_language": "spa",
            "context": "formal",
            "industry": "healthcare"
        }
        
        success, response = self.run_test(
            "Healthcare Context Translation",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            print(f"   Healthcare translation: {response.get('translated_text', '')}")
        
        return success

    def test_document_processing(self):
        """Test document processing endpoint"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a sample document for testing OCR and translation capabilities.")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_document.txt', f, 'text/plain')}
                data = {
                    'languages': 'eng',
                    'translate_to': 'spa'
                }
                
                success, response = self.run_test(
                    "Document Processing",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    print(f"   Filename: {response.get('filename', '')}")
                    print(f"   Detected language: {response.get('detected_language', '')}")
                    print(f"   Extracted text: {response.get('extracted_text', '')[:100]}...")
                    if response.get('translated_text'):
                        print(f"   Translated text: {response.get('translated_text', '')[:100]}...")
                
                return success
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_translation_history(self):
        """Test translation history endpoint"""
        success, response = self.run_test(
            "Translation History",
            "GET",
            "translations/history?limit=5",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Found {len(response)} translations in history")
            else:
                print(f"   History response: {response}")
        
        return success

    def test_audit_logs(self):
        """Test audit logs endpoint"""
        success, response = self.run_test(
            "Audit Logs",
            "GET",
            "audit/logs?limit=5",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"   Found {len(response)} audit log entries")
            else:
                print(f"   Audit logs response: {response}")
        
        return success

    def test_invalid_translation(self):
        """Test translation with invalid data"""
        translation_data = {
            "text": "",  # Empty text
            "target_language": "invalid_lang"
        }
        
        success, response = self.run_test(
            "Invalid Translation Request",
            "POST",
            "translate",
            422  # Expecting validation error
        )
        
        return success

    def test_large_text_translation(self):
        """Test translation with large text"""
        large_text = "This is a test sentence. " * 100  # 2500+ characters
        
        translation_data = {
            "text": large_text,
            "source_language": "eng",
            "target_language": "fra",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "Large Text Translation",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            print(f"   Large text processed successfully")
            print(f"   Processing time: {response.get('processing_time', 0):.2f}s")
        
        return success

def main():
    print("🚀 Starting Comprende API Testing Suite")
    print("=" * 60)
    
    tester = ComprehendeAPITester()
    
    # Core API Tests
    print("\n📋 CORE API TESTS")
    print("-" * 30)
    tester.test_root_endpoint()
    tester.test_health_check()
    tester.test_supported_languages()
    
    # Translation Tests
    print("\n🌐 TRANSLATION TESTS")
    print("-" * 30)
    tester.test_basic_translation()
    tester.test_auto_detect_translation()
    tester.test_rtl_translation()
    tester.test_industry_context_translation()
    tester.test_large_text_translation()
    
    # Document Processing Tests
    print("\n📄 DOCUMENT PROCESSING TESTS")
    print("-" * 30)
    tester.test_document_processing()
    
    # History and Audit Tests
    print("\n📊 DATA RETRIEVAL TESTS")
    print("-" * 30)
    tester.test_translation_history()
    tester.test_audit_logs()
    
    # Error Handling Tests
    print("\n⚠️  ERROR HANDLING TESTS")
    print("-" * 30)
    tester.test_invalid_translation()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
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