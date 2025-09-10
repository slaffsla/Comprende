#!/usr/bin/env python3
"""
Focused Backend Testing for Comprende API
Testing the core functionality mentioned in the review request
"""

import requests
import json
import tempfile
import os
from pathlib import Path

class FocusedAPITester:
    def __init__(self):
        self.base_url = "https://translate-hub-22.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.results = {
            'passed': [],
            'failed': [],
            'critical_issues': []
        }

    def test_health_and_languages(self):
        """Test health and supported languages endpoints"""
        print("🏥 Testing Health and Language Support...")
        
        # Health check
        try:
            response = requests.get(f"{self.api_url}/health", timeout=30)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health Check: {health_data.get('status', 'unknown')}")
                self.results['passed'].append("Health Check")
            else:
                print(f"❌ Health Check Failed: {response.status_code}")
                self.results['failed'].append("Health Check")
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
            self.results['failed'].append("Health Check")

        # Supported languages
        try:
            response = requests.get(f"{self.api_url}/languages/supported", timeout=30)
            if response.status_code == 200:
                lang_data = response.json()
                print(f"✅ Supported Languages: {len(lang_data.get('languages', {}))} languages")
                self.results['passed'].append("Supported Languages")
            else:
                print(f"❌ Supported Languages Failed: {response.status_code}")
                self.results['failed'].append("Supported Languages")
        except Exception as e:
            print(f"❌ Supported Languages Error: {e}")
            self.results['failed'].append("Supported Languages")

    def test_translation_api(self):
        """Test translation API with different languages"""
        print("\n🌐 Testing Translation API...")
        
        test_cases = [
            {
                "name": "English to Spanish",
                "data": {
                    "text": "Hello, how are you today?",
                    "source_language": "eng",
                    "target_language": "spa",
                    "context": "general"
                }
            },
            {
                "name": "English to Hebrew",
                "data": {
                    "text": "Hello world, this is a test",
                    "source_language": "eng", 
                    "target_language": "heb",
                    "context": "general"
                }
            },
            {
                "name": "English to Arabic",
                "data": {
                    "text": "Welcome to our application",
                    "source_language": "eng",
                    "target_language": "ara",
                    "context": "general"
                }
            },
            {
                "name": "Hebrew to English (Explicit)",
                "data": {
                    "text": "שלום עולם! איך אתה היום?",
                    "source_language": "heb",
                    "target_language": "eng",
                    "context": "general"
                }
            }
        ]

        for test_case in test_cases:
            try:
                response = requests.post(f"{self.api_url}/translate", json=test_case["data"], timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {test_case['name']}: {result.get('translated_text', '')[:50]}...")
                    self.results['passed'].append(f"Translation - {test_case['name']}")
                else:
                    print(f"❌ {test_case['name']} Failed: {response.status_code}")
                    self.results['failed'].append(f"Translation - {test_case['name']}")
            except Exception as e:
                print(f"❌ {test_case['name']} Error: {e}")
                self.results['failed'].append(f"Translation - {test_case['name']}")

    def test_language_detection_accuracy(self):
        """Test language detection accuracy - CRITICAL TEST"""
        print("\n🔍 Testing Language Detection Accuracy (CRITICAL)...")
        
        # Test with Hebrew text auto-detection (this was the main issue)
        hebrew_text = "שלום עולם! זהו טקסט בעברית לבדיקת זיהוי השפה."
        
        print(f"Testing Hebrew detection with text: {hebrew_text[:30]}...")
        
        # Try auto-detection (this might fail due to the 500 error we saw)
        try:
            data = {
                "text": hebrew_text,
                "target_language": "eng",
                "context": "general"
            }
            response = requests.post(f"{self.api_url}/translate", json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result.get('source_language', 'unknown')
                print(f"✅ Hebrew Auto-Detection: Detected as '{detected_lang}'")
                
                if detected_lang == 'heb':
                    print("✅ CRITICAL: Hebrew correctly detected as 'heb'")
                    self.results['passed'].append("Hebrew Language Detection")
                else:
                    print(f"❌ CRITICAL: Hebrew incorrectly detected as '{detected_lang}' instead of 'heb'")
                    self.results['critical_issues'].append(f"Hebrew detected as '{detected_lang}' not 'heb'")
                    self.results['failed'].append("Hebrew Language Detection")
            else:
                print(f"❌ Hebrew Auto-Detection Failed: {response.status_code}")
                print("⚠️  CRITICAL: Auto-detection not working - this was a key issue to fix")
                self.results['critical_issues'].append("Hebrew auto-detection API returns 500 error")
                self.results['failed'].append("Hebrew Language Detection")
                
        except Exception as e:
            print(f"❌ Hebrew Auto-Detection Error: {e}")
            self.results['critical_issues'].append(f"Hebrew auto-detection error: {e}")
            self.results['failed'].append("Hebrew Language Detection")

        # Test Arabic detection
        arabic_text = "أهلاً وسهلاً! هذا نص باللغة العربية."
        print(f"Testing Arabic detection with text: {arabic_text[:30]}...")
        
        try:
            data = {
                "text": arabic_text,
                "target_language": "eng",
                "context": "general"
            }
            response = requests.post(f"{self.api_url}/translate", json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result.get('source_language', 'unknown')
                print(f"✅ Arabic Auto-Detection: Detected as '{detected_lang}'")
                
                if detected_lang == 'ara':
                    print("✅ Arabic correctly detected as 'ara'")
                    self.results['passed'].append("Arabic Language Detection")
                else:
                    print(f"❌ Arabic incorrectly detected as '{detected_lang}' instead of 'ara'")
                    self.results['failed'].append("Arabic Language Detection")
            else:
                print(f"❌ Arabic Auto-Detection Failed: {response.status_code}")
                self.results['failed'].append("Arabic Language Detection")
                
        except Exception as e:
            print(f"❌ Arabic Auto-Detection Error: {e}")
            self.results['failed'].append("Arabic Language Detection")

    def test_document_processing(self):
        """Test document processing with different file types and languages"""
        print("\n📄 Testing Document Processing...")
        
        test_cases = [
            {
                "name": "English Text Document",
                "content": "This is a sample English document for testing OCR and translation capabilities.",
                "filename": "english_test.txt",
                "expected_lang": "eng",
                "translate_to": "spa"
            },
            {
                "name": "Hebrew Text Document", 
                "content": "שלום עולם! זהו מסמך בעברית לבדיקת זיהוי שפה ותרגום.",
                "filename": "hebrew_test.txt",
                "expected_lang": "heb",
                "translate_to": "eng"
            },
            {
                "name": "Arabic Text Document",
                "content": "أهلاً وسهلاً! هذا مستند باللغة العربية لاختبار التعرف على اللغة.",
                "filename": "arabic_test.txt", 
                "expected_lang": "ara",
                "translate_to": "eng"
            }
        ]

        for test_case in test_cases:
            print(f"Testing {test_case['name']}...")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(test_case['content'])
                temp_file_path = f.name

            try:
                with open(temp_file_path, 'rb') as f:
                    files = {'file': (test_case['filename'], f, 'text/plain')}
                    data = {
                        'languages': test_case['expected_lang'],
                        'translate_to': test_case['translate_to']
                    }
                    
                    response = requests.post(f"{self.api_url}/documents/process", files=files, data=data, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        detected_lang = result.get('detected_language', 'unknown')
                        
                        print(f"✅ {test_case['name']}: Detected as '{detected_lang}'")
                        
                        if detected_lang == test_case['expected_lang']:
                            print(f"✅ Language detection correct for {test_case['name']}")
                            self.results['passed'].append(f"Document Processing - {test_case['name']}")
                        else:
                            print(f"❌ Expected '{test_case['expected_lang']}', got '{detected_lang}'")
                            if test_case['expected_lang'] == 'heb' and detected_lang == 'eng':
                                self.results['critical_issues'].append(f"Hebrew document detected as English in {test_case['name']}")
                            self.results['failed'].append(f"Document Processing - {test_case['name']}")
                            
                        # Check if translation was provided
                        if result.get('translated_text'):
                            print(f"   Translation: {result['translated_text'][:50]}...")
                        
                    else:
                        print(f"❌ {test_case['name']} Failed: {response.status_code}")
                        self.results['failed'].append(f"Document Processing - {test_case['name']}")
                        
            except Exception as e:
                print(f"❌ {test_case['name']} Error: {e}")
                self.results['failed'].append(f"Document Processing - {test_case['name']}")
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

    def test_file_download(self):
        """Test file download functionality"""
        print("\n📥 Testing File Download...")
        
        download_data = {
            "content": "This is sample content for download testing. The new file download functionality should work properly through the backend API endpoint.",
            "filename": "test_download.txt"
        }
        
        try:
            response = requests.post(f"{self.api_url}/documents/download", json=download_data, timeout=30)
            
            if response.status_code == 200:
                print("✅ File Download: Endpoint working correctly")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   Content-Length: {len(response.content)} bytes")
                self.results['passed'].append("File Download")
            else:
                print(f"❌ File Download Failed: {response.status_code}")
                self.results['failed'].append("File Download")
                
        except Exception as e:
            print(f"❌ File Download Error: {e}")
            self.results['failed'].append("File Download")

    def run_all_tests(self):
        """Run all focused tests"""
        print("🚀 Starting Focused Comprende Backend Testing")
        print("=" * 60)
        print("Focus: Translation API, Language Detection, Document Processing, File Downloads")
        print("=" * 60)
        
        self.test_health_and_languages()
        self.test_translation_api()
        self.test_language_detection_accuracy()
        self.test_document_processing()
        self.test_file_download()
        
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        success_rate = (len(self.results['passed']) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {len(self.results['passed'])}")
        print(f"Failed: {len(self.results['failed'])}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.results['critical_issues'])}):")
            for i, issue in enumerate(self.results['critical_issues'], 1):
                print(f"{i}. {issue}")
        
        if self.results['failed']:
            print(f"\n❌ FAILED TESTS ({len(self.results['failed'])}):")
            for i, test in enumerate(self.results['failed'], 1):
                print(f"{i}. {test}")
        
        if self.results['passed']:
            print(f"\n✅ PASSED TESTS ({len(self.results['passed'])}):")
            for i, test in enumerate(self.results['passed'], 1):
                print(f"{i}. {test}")

if __name__ == "__main__":
    tester = FocusedAPITester()
    tester.run_all_tests()