import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import tempfile
import os

class CriticalIssuesTester:
    def __init__(self, base_url="https://comprende-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_issues = []

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
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:500]
                })
                return False, response.text

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            self.failed_tests.append({'name': name, 'error': 'Timeout'})
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({'name': name, 'error': str(e)})
            return False, {}

    def test_german_language_detection_critical(self):
        """CRITICAL: Test the exact German text mentioned by user"""
        german_text = "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee und das Schellen der Glöckchen am Zaumzeug der Haflinger-Pferde klingen wie süße Musik in der klaren Bergluft."
        
        print(f"\n🚨 CRITICAL TEST: German Language Detection")
        print(f"   Testing exact text: {german_text[:80]}...")
        
        translation_data = {
            "text": german_text,
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "CRITICAL: German Language Detection",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            detected_lang = response.get('source_language', '')
            print(f"   Detected language: {detected_lang}")
            print(f"   Expected: 'deu' (German)")
            print(f"   Actual: '{detected_lang}'")
            
            # CRITICAL CHECK: German text should be detected as 'deu', NOT 'spa'
            if detected_lang == 'deu':
                print("   ✅ CRITICAL TEST PASSED: German correctly detected as 'deu'")
            elif detected_lang == 'spa':
                print("   🚨 CRITICAL FAILURE: German text detected as Spanish ('spa') instead of German ('deu')")
                self.critical_issues.append({
                    'issue': 'German text incorrectly detected as Spanish',
                    'expected': 'deu',
                    'actual': 'spa',
                    'text': german_text[:100] + '...',
                    'severity': 'CRITICAL'
                })
            else:
                print(f"   ❌ CRITICAL ISSUE: German text detected as '{detected_lang}' instead of 'deu'")
                self.critical_issues.append({
                    'issue': f'German text incorrectly detected as {detected_lang}',
                    'expected': 'deu',
                    'actual': detected_lang,
                    'text': german_text[:100] + '...',
                    'severity': 'CRITICAL'
                })
            
            print(f"   Translation: {response.get('translated_text', '')[:100]}...")
            print(f"   Confidence: {response.get('confidence', 0)*100:.1f}%")
        
        return success

    def test_file_download_with_actual_content(self):
        """CRITICAL: Test file download returns actual content, not sample text"""
        print(f"\n🚨 CRITICAL TEST: File Download with Actual Content")
        
        # Test with translation text
        test_content = "This is the actual content that should be downloaded exactly as provided. Not sample text."
        test_filename = "actual_content_test.txt"
        
        download_data = {
            "content": test_content,
            "filename": test_filename
        }
        
        print(f"   Testing download with content: {test_content[:50]}...")
        
        success, response = self.run_test(
            "CRITICAL: File Download Actual Content",
            "POST",
            "documents/download",
            200,
            data=download_data
        )
        
        if success:
            # Check if we got the actual content back
            if isinstance(response, str):
                if test_content in response:
                    print("   ✅ CRITICAL TEST PASSED: Download returns actual content")
                elif "sample" in response.lower() or "example" in response.lower():
                    print("   🚨 CRITICAL FAILURE: Download returns sample text instead of actual content")
                    self.critical_issues.append({
                        'issue': 'File download returns sample text instead of actual content',
                        'expected': 'Actual provided content',
                        'actual': 'Sample/example text',
                        'severity': 'CRITICAL'
                    })
                else:
                    print(f"   ⚠️  Download content: {response[:100]}...")
            else:
                print("   ✅ File download endpoint working (binary response)")
        
        return success

    def test_document_processing_actual_vs_sample(self):
        """CRITICAL: Test document processing returns extracted text, not sample text"""
        print(f"\n🚨 CRITICAL TEST: Document Processing - Actual vs Sample Text")
        
        # Create a text file with specific content
        actual_content = "This is the real document content that should be extracted exactly. Not sample or mock text."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(actual_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('real_document.txt', f, 'text/plain')}
                data = {
                    'languages': 'eng',
                    'translate_to': 'spa'
                }
                
                success, response = self.run_test(
                    "CRITICAL: Document Processing Actual Content",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    extracted_text = response.get('extracted_text', '')
                    print(f"   Original content: {actual_content[:50]}...")
                    print(f"   Extracted text: {extracted_text[:50]}...")
                    
                    # Check if we got actual content or sample text
                    if actual_content in extracted_text:
                        print("   ✅ CRITICAL TEST PASSED: Document processing returns actual content")
                    elif "sample" in extracted_text.lower() or "example" in extracted_text.lower():
                        print("   🚨 CRITICAL FAILURE: Document processing returns sample text instead of actual content")
                        self.critical_issues.append({
                            'issue': 'Document processing returns sample text instead of extracted content',
                            'expected': 'Actual document content',
                            'actual': 'Sample/mock text',
                            'severity': 'CRITICAL'
                        })
                    else:
                        print(f"   ⚠️  Extracted different content: {extracted_text[:100]}...")
                
                return success
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_multiple_language_detection_regression(self):
        """Test multiple languages to ensure no regression"""
        print(f"\n🔍 REGRESSION TEST: Multiple Language Detection")
        
        test_cases = [
            ("שלום עולם! איך אתה היום?", "heb", "Hebrew"),
            ("أهلاً وسهلاً! كيف حالك اليوم؟", "ara", "Arabic"),
            ("Hello world! How are you today?", "eng", "English"),
            ("Bonjour le monde! Comment allez-vous?", "fra", "French"),
            ("Ciao mondo! Come stai oggi?", "ita", "Italian"),
            ("Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee", "deu", "German")
        ]
        
        all_passed = True
        
        for text, expected_lang, lang_name in test_cases:
            translation_data = {
                "text": text,
                "target_language": "eng",
                "context": "general",
                "industry": "general"
            }
            
            success, response = self.run_test(
                f"Language Detection: {lang_name}",
                "POST",
                "translate",
                200,
                data=translation_data
            )
            
            if success:
                detected_lang = response.get('source_language', '')
                print(f"   {lang_name}: Expected '{expected_lang}', Got '{detected_lang}'")
                
                if detected_lang != expected_lang:
                    print(f"   ❌ {lang_name} detection failed")
                    all_passed = False
                    if lang_name == "German" and detected_lang == "spa":
                        self.critical_issues.append({
                            'issue': f'{lang_name} text detected as Spanish instead of {expected_lang}',
                            'expected': expected_lang,
                            'actual': detected_lang,
                            'severity': 'CRITICAL'
                        })
                else:
                    print(f"   ✅ {lang_name} detection passed")
            else:
                all_passed = False
        
        return all_passed

    def test_system_health_and_performance(self):
        """Test system health and API response times"""
        print(f"\n🏥 SYSTEM HEALTH AND PERFORMANCE TEST")
        
        start_time = time.time()
        success, response = self.run_test(
            "System Health Check",
            "GET",
            "health",
            200
        )
        response_time = time.time() - start_time
        
        if success:
            print(f"   Response time: {response_time:.2f}s")
            print(f"   System status: {response.get('status', 'unknown')}")
            
            if 'components' in response:
                for component, status in response['components'].items():
                    print(f"   - {component}: {status}")
                    if 'unhealthy' in str(status).lower():
                        self.critical_issues.append({
                            'issue': f'System component {component} is unhealthy',
                            'status': status,
                            'severity': 'HIGH'
                        })
            
            # Check response time
            if response_time > 5.0:
                print(f"   ⚠️  Slow response time: {response_time:.2f}s")
                self.critical_issues.append({
                    'issue': 'Slow API response time',
                    'response_time': f'{response_time:.2f}s',
                    'severity': 'MEDIUM'
                })
            else:
                print(f"   ✅ Good response time: {response_time:.2f}s")
        
        return success

    def test_translation_quality_and_confidence(self):
        """Test translation quality for the German text"""
        print(f"\n🎯 TRANSLATION QUALITY TEST")
        
        german_text = "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee und das Schellen der Glöckchen am Zaumzeug der Haflinger-Pferde klingen wie süße Musik in der klaren Bergluft."
        
        translation_data = {
            "text": german_text,
            "source_language": "deu",  # Explicitly specify German
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        success, response = self.run_test(
            "Translation Quality: German to English",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            confidence = response.get('confidence', 0)
            translated_text = response.get('translated_text', '')
            processing_time = response.get('processing_time', 0)
            
            print(f"   Original: {german_text[:80]}...")
            print(f"   Translation: {translated_text[:80]}...")
            print(f"   Confidence: {confidence*100:.1f}%")
            print(f"   Processing time: {processing_time:.2f}s")
            
            # Check translation quality indicators
            if confidence < 0.8:
                print(f"   ⚠️  Low confidence: {confidence*100:.1f}%")
                self.critical_issues.append({
                    'issue': 'Low translation confidence',
                    'confidence': f'{confidence*100:.1f}%',
                    'severity': 'MEDIUM'
                })
            else:
                print(f"   ✅ Good confidence: {confidence*100:.1f}%")
            
            # Check for key translated words
            key_words = ['rhythm', 'hooves', 'snow', 'bells', 'horses', 'music', 'mountain', 'air']
            found_words = sum(1 for word in key_words if word.lower() in translated_text.lower())
            
            print(f"   Key words found: {found_words}/{len(key_words)}")
            if found_words < len(key_words) * 0.6:  # At least 60% of key words
                print(f"   ⚠️  Translation may be incomplete")
            else:
                print(f"   ✅ Translation appears comprehensive")
        
        return success

def main():
    print("🚨 CRITICAL ISSUES TESTING SUITE")
    print("=" * 60)
    print("Testing specific issues reported by user:")
    print("1. German text detection (should be 'deu', not 'spa')")
    print("2. File download actual content (not sample text)")
    print("3. Document processing actual vs sample text")
    print("4. System health and performance")
    print("5. Translation quality and confidence")
    print("=" * 60)
    
    tester = CriticalIssuesTester()
    
    # CRITICAL TESTS - Focus on user-reported issues
    print("\n🚨 CRITICAL ISSUE TESTS")
    print("-" * 40)
    tester.test_german_language_detection_critical()
    tester.test_file_download_with_actual_content()
    tester.test_document_processing_actual_vs_sample()
    
    # REGRESSION TESTS
    print("\n🔄 REGRESSION TESTS")
    print("-" * 30)
    tester.test_multiple_language_detection_regression()
    
    # SYSTEM HEALTH
    print("\n🏥 SYSTEM HEALTH TESTS")
    print("-" * 30)
    tester.test_system_health_and_performance()
    
    # QUALITY TESTS
    print("\n🎯 QUALITY TESTS")
    print("-" * 30)
    tester.test_translation_quality_and_confidence()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 CRITICAL TESTING RESULTS")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(tester.failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    # Report critical issues
    if tester.critical_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND: {len(tester.critical_issues)}")
        print("-" * 40)
        for i, issue in enumerate(tester.critical_issues, 1):
            print(f"{i}. [{issue['severity']}] {issue['issue']}")
            if 'expected' in issue and 'actual' in issue:
                print(f"   Expected: {issue['expected']}, Got: {issue['actual']}")
            if 'text' in issue:
                print(f"   Text: {issue['text']}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
    
    # Report failed tests
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS: {len(tester.failed_tests)}")
        print("-" * 30)
        for i, test in enumerate(tester.failed_tests, 1):
            print(f"{i}. {test['name']}")
            if 'expected' in test:
                print(f"   Expected: {test['expected']}, Got: {test['actual']}")
            if 'error' in test:
                print(f"   Error: {test['error']}")
    
    return 0 if len(tester.critical_issues) == 0 and tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())