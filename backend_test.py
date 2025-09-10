import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import tempfile
import os

class ComprehendeAPITester:
    def __init__(self, base_url="https://translate-hub-22.preview.emergentagent.com"):
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

    def test_hebrew_document_processing(self):
        """Test Hebrew document processing and language detection"""
        # Create a temporary text file with Hebrew content
        hebrew_text = "שלום עולם! זהו מסמך בעברית לבדיקת זיהוי שפה ותרגום."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(hebrew_text)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('hebrew_document.txt', f, 'text/plain')}
                data = {
                    'languages': 'heb',
                    'translate_to': 'eng'
                }
                
                success, response = self.run_test(
                    "Hebrew Document Processing",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    detected_lang = response.get('detected_language', '')
                    print(f"   Detected language: {detected_lang}")
                    print(f"   Expected: heb, Got: {detected_lang}")
                    
                    # Check if Hebrew was correctly detected
                    if detected_lang == 'heb':
                        print("   ✅ Hebrew language detection PASSED")
                    else:
                        print("   ❌ Hebrew language detection FAILED - detected as English instead")
                        self.failed_tests.append({
                            'name': 'Hebrew Language Detection',
                            'expected': 'heb',
                            'actual': detected_lang,
                            'response': 'Hebrew text incorrectly detected as English'
                        })
                    
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

    def test_arabic_document_processing(self):
        """Test Arabic document processing and language detection"""
        # Create a temporary text file with Arabic content
        arabic_text = "أهلاً وسهلاً! هذا مستند باللغة العربية لاختبار التعرف على اللغة والترجمة."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(arabic_text)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('arabic_document.txt', f, 'text/plain')}
                data = {
                    'languages': 'ara',
                    'translate_to': 'eng'
                }
                
                success, response = self.run_test(
                    "Arabic Document Processing",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    detected_lang = response.get('detected_language', '')
                    print(f"   Detected language: {detected_lang}")
                    print(f"   Expected: ara, Got: {detected_lang}")
                    
                    # Check if Arabic was correctly detected
                    if detected_lang == 'ara':
                        print("   ✅ Arabic language detection PASSED")
                    else:
                        print("   ❌ Arabic language detection FAILED")
                    
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

    def test_document_download(self):
        """Test document download functionality"""
        download_data = {
            "content": "This is sample content for download testing. The file download functionality should work properly.",
            "filename": "test_download.txt"
        }
        
        success, response = self.run_test(
            "Document Download",
            "POST",
            "documents/download",
            200,
            data=download_data
        )
        
        if success:
            print("   ✅ Document download endpoint working")
        else:
            print("   ❌ Document download endpoint failed")
        
        return success

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

    def test_vladislav_resume_pdf_processing(self):
        """Test critical PDF processing fix - Vladislav resume with Russian translation"""
        print("\n🎯 CRITICAL TEST: PDF Processing Fix Verification")
        print("   Testing actual resume content extraction vs sample text")
        
        # Create a temporary PDF file with resume content (simulating PDF upload)
        resume_content = """Vladislav Zhiltsov
slasla@gmail.com (+972) 58-410-410-5 Haifa, Israel

EDUCATION
B.Sc. Mechanical Engineering Technion 2001-2006 Haifa, Israel

SKILLS
JavaScript, TypeScript, HTML, CSS, React.js, Redux, Firebase, React Native, GIT
Familiar with: UX, UI, Web Design, Three.js, Tailwind CSS, Node.js

WORK EXPERIENCE
Frontend Developer - Siema (March 2021 - March 2022)
Developed visually appealing user interfaces and seamless user experiences using cutting-edge technologies, with special attention to code cleanness and maintainability.

Product Localization Manager - Optima Global (April 2022 - current)
Ensuring seamless product adaptation for local markets, addressing its needs and regulations. Developing and executing localization strategies, striving to maximize market penetration.

PERSONAL STRENGTHS
Written and Verbal Communication - excellent language and communication skills (in 3 languages)
Thinking outside the box
Attentive to details

PERSONAL INTERESTS
Brazilian Jiu Jitsu
Playing musical instruments (Mostly Handpan)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, encoding='utf-8') as f:
            f.write(resume_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('vladislav_resume.pdf', f, 'application/pdf')}
                data = {
                    'languages': 'eng',
                    'translate_to': 'rus'  # Russian translation as requested
                }
                
                success, response = self.run_test(
                    "CRITICAL: Vladislav Resume PDF Processing with Russian Translation",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    extracted_text = response.get('extracted_text', '')
                    translated_text = response.get('translated_text', '')
                    detected_lang = response.get('detected_language', '')
                    
                    print(f"   Detected language: {detected_lang}")
                    print(f"   Extracted text preview: {extracted_text[:100]}...")
                    
                    # CRITICAL VERIFICATION 1: Check for actual resume content, NOT sample text
                    sample_text_indicators = [
                        "This is successfully extracted content from PDF document",
                        "Sample extracted text from PDF document",
                        "successfully extracted PDF content"
                    ]
                    
                    has_sample_text = any(indicator in extracted_text for indicator in sample_text_indicators)
                    has_vladislav_name = "Vladislav Zhiltsov" in extracted_text
                    
                    if has_sample_text:
                        print("   ❌ CRITICAL FAILURE: Still returning sample text instead of actual content!")
                        self.failed_tests.append({
                            'name': 'PDF Processing Fix - Sample Text Issue',
                            'expected': 'Actual resume content',
                            'actual': 'Sample text returned',
                            'response': f'Found sample text indicators in: {extracted_text[:200]}'
                        })
                        return False
                    elif has_vladislav_name:
                        print("   ✅ CRITICAL SUCCESS: Actual resume content extracted (contains 'Vladislav Zhiltsov')")
                    else:
                        print("   ⚠️  WARNING: No sample text found, but 'Vladislav Zhiltsov' not detected either")
                        print(f"   Full extracted text: {extracted_text}")
                    
                    # CRITICAL VERIFICATION 2: Check Russian translation quality
                    if translated_text:
                        print(f"   Russian translation preview: {translated_text[:100]}...")
                        
                        # Check for proper Cyrillic characters
                        cyrillic_chars = sum(1 for char in translated_text if '\u0400' <= char <= '\u04ff')
                        cyrillic_percentage = (cyrillic_chars / len(translated_text)) * 100 if translated_text else 0
                        
                        print(f"   Cyrillic characters: {cyrillic_percentage:.1f}% of text")
                        
                        # Check for key Russian terms
                        russian_name_variants = ["Владислав Жильцов", "Владислав", "Жильцов"]
                        has_russian_name = any(name in translated_text for name in russian_name_variants)
                        
                        if has_russian_name:
                            print("   ✅ Russian translation contains proper name translation")
                        else:
                            print("   ⚠️  Russian translation may not contain proper name translation")
                        
                        # Check for broken Russian patterns
                        broken_patterns = ["успешно извлеченное", "успешно извлеченный"]
                        has_broken_russian = any(pattern in translated_text for pattern in broken_patterns)
                        
                        if has_broken_russian:
                            print("   ❌ WARNING: Detected broken Russian translation patterns")
                        else:
                            print("   ✅ No broken Russian patterns detected")
                        
                        if cyrillic_percentage > 30 and not has_broken_russian:
                            print("   ✅ CRITICAL SUCCESS: High-quality Russian translation confirmed")
                        else:
                            print("   ⚠️  Russian translation quality needs verification")
                    else:
                        print("   ❌ No Russian translation provided")
                        self.failed_tests.append({
                            'name': 'Russian Translation Missing',
                            'expected': 'Russian translation of resume',
                            'actual': 'No translation provided',
                            'response': 'translate_to=rus but no translated_text in response'
                        })
                    
                    # CRITICAL VERIFICATION 3: Frontend integration simulation
                    print("   🔄 Simulating frontend integration...")
                    if has_vladislav_name and not has_sample_text:
                        print("   ✅ FRONTEND INTEGRATION: Will receive actual resume content")
                    else:
                        print("   ❌ FRONTEND INTEGRATION: Will still receive incorrect content")
                        return False
                
                return success
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass

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

    def test_hebrew_language_detection(self):
        """Test Hebrew language detection in translation"""
        hebrew_text = "שלום עולם! איך אתה היום? זהו טקסט בעברית לבדיקת זיהוי השפה."
        
        translation_data = {
            "text": hebrew_text,
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "Hebrew Language Detection in Translation",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            detected_lang = response.get('source_language', '')
            print(f"   Hebrew text: {hebrew_text[:50]}...")
            print(f"   Detected language: {detected_lang}")
            print(f"   Expected: heb, Got: {detected_lang}")
            
            # Critical check: Hebrew should be detected as 'heb', not 'eng'
            if detected_lang == 'heb':
                print("   ✅ Hebrew language detection PASSED")
            else:
                print("   ❌ Hebrew language detection FAILED - detected as English instead")
                self.failed_tests.append({
                    'name': 'Hebrew Language Detection',
                    'expected': 'heb',
                    'actual': detected_lang,
                    'response': 'Hebrew text incorrectly detected as English'
                })
            
            print(f"   Translated: {response.get('translated_text', '')}")
        
        return success

    def test_arabic_language_detection(self):
        """Test Arabic language detection in translation"""
        arabic_text = "أهلاً وسهلاً! كيف حالك اليوم؟ هذا نص باللغة العربية لاختبار التعرف على اللغة."
        
        translation_data = {
            "text": arabic_text,
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "Arabic Language Detection in Translation",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            detected_lang = response.get('source_language', '')
            print(f"   Arabic text: {arabic_text[:50]}...")
            print(f"   Detected language: {detected_lang}")
            print(f"   Expected: ara, Got: {detected_lang}")
            
            if detected_lang == 'ara':
                print("   ✅ Arabic language detection PASSED")
            else:
                print("   ❌ Arabic language detection FAILED")
            
            print(f"   Translated: {response.get('translated_text', '')}")
        
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
    
    # Language Detection Tests (Critical)
    print("\n🔍 LANGUAGE DETECTION TESTS (CRITICAL)")
    print("-" * 40)
    tester.test_hebrew_language_detection()
    tester.test_arabic_language_detection()
    
    # Document Processing Tests
    print("\n📄 DOCUMENT PROCESSING TESTS")
    print("-" * 30)
    tester.test_document_processing()
    tester.test_hebrew_document_processing()
    tester.test_arabic_document_processing()
    
    # CRITICAL PDF Processing Fix Test
    print("\n🎯 CRITICAL PDF PROCESSING FIX VERIFICATION")
    print("-" * 50)
    tester.test_vladislav_resume_pdf_processing()
    
    # File Download Tests
    print("\n📥 FILE DOWNLOAD TESTS")
    print("-" * 30)
    tester.test_document_download()
    
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