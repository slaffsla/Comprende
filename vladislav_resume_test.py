import requests
import sys
import json
import time
import tempfile
import os

class VladislavResumeTranslationTester:
    def __init__(self, base_url="https://comprende-comms.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        
        # Actual resume content from Vladislav Zhiltsov
        self.resume_content = """Vladislav Zhiltsov
slasla@gmail.com (+972) 58-410-410-5 Haifa, Israel

EDUCATION
B.Sc. Mechanical Engineering Technion 2001-2006 Haifa, Israel

SKILLS
JavaScript, TypeScript, HTML, CSS, React.js, Redux, Firebase, React Native, GIT

WORK EXPERIENCE
Frontend Developer - Siema (March 2021 - March 2022)
Developed visually appealing user interfaces and seamless user experiences using cutting-edge technologies including React.js, Redux for state management, and modern CSS frameworks. Collaborated with cross-functional teams to deliver high-quality web applications that enhanced user engagement and satisfaction.

Key Achievements:
- Implemented responsive design principles ensuring optimal user experience across all devices
- Optimized application performance resulting in 40% faster load times
- Integrated third-party APIs and services to enhance application functionality
- Mentored junior developers and contributed to code review processes
- Participated in agile development methodologies and sprint planning

Technical Skills:
- Frontend: React.js, Redux, JavaScript (ES6+), TypeScript, HTML5, CSS3, SASS
- Mobile: React Native, iOS/Android development
- Tools: Git, Webpack, npm/yarn, VS Code, Chrome DevTools
- Databases: Firebase, MongoDB
- Other: RESTful APIs, GraphQL, Responsive Design, Cross-browser compatibility

PROJECTS
Personal Portfolio Website
Developed a fully responsive portfolio website showcasing projects and skills using React.js and modern CSS techniques. Implemented smooth animations and interactive elements to create an engaging user experience.

E-commerce Application
Built a complete e-commerce solution with React.js frontend and Firebase backend. Features include user authentication, product catalog, shopping cart, and payment integration.

LANGUAGES
Hebrew (Native), English (Fluent), Russian (Conversational)

INTERESTS
Technology trends, Web development, Mobile applications, User experience design, Open source contributions"""

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
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            self.failed_tests.append({'name': name, 'error': 'Timeout'})
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({'name': name, 'error': str(e)})
            return False, {}

    def test_resume_pdf_processing_english_to_russian(self):
        """Test processing Vladislav's resume as PDF with English to Russian translation"""
        print("\n" + "="*80)
        print("🎯 CRITICAL TEST: Real Resume Content Translation (English → Russian)")
        print("="*80)
        
        # Create a temporary PDF-like file with the actual resume content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, encoding='utf-8') as f:
            f.write(self.resume_content)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('vladislav_resume.pdf', f, 'application/pdf')}
                data = {
                    'languages': 'eng',
                    'translate_to': 'rus'
                }
                
                success, response = self.run_test(
                    "Vladislav Resume PDF Processing (English → Russian)",
                    "POST",
                    "documents/process",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    # Critical verification checks
                    extracted_text = response.get('extracted_text', '')
                    translated_text = response.get('translated_text', '')
                    detected_language = response.get('detected_language', '')
                    filename = response.get('filename', '')
                    
                    print(f"\n📋 VERIFICATION RESULTS:")
                    print(f"   Filename: {filename}")
                    print(f"   Detected Language: {detected_language}")
                    print(f"   Processing Time: {response.get('processing_time', 0):.2f}s")
                    print(f"   Confidence: {response.get('confidence', 0)*100:.1f}%")
                    
                    # Check 1: Filename should be correct
                    if filename == 'vladislav_resume.pdf':
                        print("   ✅ Filename verification PASSED")
                    else:
                        print(f"   ❌ Filename verification FAILED - Expected: vladislav_resume.pdf, Got: {filename}")
                        self.failed_tests.append({
                            'name': 'Resume Filename Verification',
                            'expected': 'vladislav_resume.pdf',
                            'actual': filename,
                            'response': 'Incorrect filename returned'
                        })
                    
                    # Check 2: Language detection should be English ('eng')
                    if detected_language == 'eng':
                        print("   ✅ Language detection PASSED (English detected)")
                    else:
                        print(f"   ❌ Language detection FAILED - Expected: eng, Got: {detected_language}")
                        self.failed_tests.append({
                            'name': 'Resume Language Detection',
                            'expected': 'eng',
                            'actual': detected_language,
                            'response': 'English resume not detected as English'
                        })
                    
                    # Check 3: Extracted text should contain actual resume content, NOT sample text
                    print(f"\n📄 EXTRACTED TEXT VERIFICATION:")
                    print(f"   Length: {len(extracted_text)} characters")
                    print(f"   Preview: {extracted_text[:200]}...")
                    
                    # Critical check: Should contain actual resume content
                    if "Vladislav Zhiltsov" in extracted_text:
                        print("   ✅ CRITICAL: Contains actual resume content (Vladislav Zhiltsov found)")
                    else:
                        print("   ❌ CRITICAL FAILURE: Does NOT contain actual resume content")
                        self.failed_tests.append({
                            'name': 'Resume Content Verification',
                            'expected': 'Actual resume content with Vladislav Zhiltsov',
                            'actual': 'Sample or generic text',
                            'response': 'Extracted text does not contain expected resume content'
                        })
                    
                    # Check for sample text patterns (should NOT be present)
                    sample_patterns = [
                        "Sample extracted text from PDF document",
                        "This is sample text",
                        "sample content",
                        "mock implementation"
                    ]
                    
                    contains_sample = any(pattern.lower() in extracted_text.lower() for pattern in sample_patterns)
                    if not contains_sample:
                        print("   ✅ CRITICAL: No sample text patterns found - using real content")
                    else:
                        print("   ❌ CRITICAL FAILURE: Contains sample text patterns instead of real content")
                        self.failed_tests.append({
                            'name': 'No Sample Text Verification',
                            'expected': 'Real extracted content',
                            'actual': 'Sample/mock text detected',
                            'response': 'System returning sample text instead of actual document content'
                        })
                    
                    # Check 4: Translation should be in Russian (Cyrillic script)
                    if translated_text:
                        print(f"\n🌐 RUSSIAN TRANSLATION VERIFICATION:")
                        print(f"   Length: {len(translated_text)} characters")
                        print(f"   Preview: {translated_text[:200]}...")
                        
                        # Check for Cyrillic characters (Russian script)
                        cyrillic_chars = sum(1 for char in translated_text if '\u0400' <= char <= '\u04ff')
                        cyrillic_percentage = (cyrillic_chars / len(translated_text)) * 100 if translated_text else 0
                        
                        print(f"   Cyrillic characters: {cyrillic_chars} ({cyrillic_percentage:.1f}%)")
                        
                        if cyrillic_percentage > 20:  # Should have significant Cyrillic content
                            print("   ✅ CRITICAL: Translation contains Russian (Cyrillic) text")
                        else:
                            print("   ❌ CRITICAL FAILURE: Translation does NOT contain Russian text")
                            self.failed_tests.append({
                                'name': 'Russian Translation Verification',
                                'expected': 'Russian (Cyrillic) text',
                                'actual': f'Non-Cyrillic text ({cyrillic_percentage:.1f}% Cyrillic)',
                                'response': 'Translation not in Russian language'
                            })
                        
                        # Check if translation contains key resume elements in Russian
                        if any(name in translated_text for name in ["Владислав", "Жильцов"]):
                            print("   ✅ CRITICAL: Russian translation contains translated name")
                        else:
                            print("   ⚠️  WARNING: Russian translation may not contain properly translated name")
                    else:
                        print("   ❌ CRITICAL FAILURE: No translation provided")
                        self.failed_tests.append({
                            'name': 'Translation Presence',
                            'expected': 'Russian translation provided',
                            'actual': 'No translation',
                            'response': 'translate_to=rus specified but no translation returned'
                        })
                    
                    return success, response
                else:
                    print("   ❌ CRITICAL FAILURE: Document processing request failed")
                    return False, {}
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_download_russian_translation(self):
        """Test downloading the Russian translation"""
        print("\n📥 TESTING DOWNLOAD OF RUSSIAN TRANSLATION")
        print("-" * 50)
        
        # Use sample Russian translation content for download test
        russian_content = """Владислав Жильцов
slasla@gmail.com (+972) 58-410-410-5 Хайфа, Израиль

ОБРАЗОВАНИЕ
Бакалавр наук по машиностроению Технион 2001-2006 Хайфа, Израиль

НАВЫКИ
JavaScript, TypeScript, HTML, CSS, React.js, Redux, Firebase, React Native, GIT

ОПЫТ РАБОТЫ
Frontend разработчик - Siema (март 2021 - март 2022)
Разработал визуально привлекательные пользовательские интерфейсы и бесшовные пользовательские опыты, используя передовые технологии."""
        
        download_data = {
            "content": russian_content,
            "filename": "vladislav_resume_russian.txt"
        }
        
        success, response = self.run_test(
            "Download Russian Resume Translation",
            "POST",
            "documents/download",
            200,
            data=download_data
        )
        
        if success:
            print("   ✅ CRITICAL: Download endpoint working for Russian content")
            print(f"   Content length: {len(russian_content)} characters")
            
            # Verify the response is a file download
            if isinstance(response, str) and len(response) > 100:
                print("   ✅ Download response contains substantial content")
            else:
                print("   ⚠️  WARNING: Download response may be truncated or invalid")
        else:
            print("   ❌ CRITICAL FAILURE: Download endpoint failed")
            self.failed_tests.append({
                'name': 'Russian Translation Download',
                'expected': 'Successful file download',
                'actual': 'Download failed',
                'response': 'Download endpoint not working for Russian content'
            })
        
        return success

    def test_english_language_detection_verification(self):
        """Verify English language detection with resume content"""
        print("\n🔍 VERIFYING ENGLISH LANGUAGE DETECTION")
        print("-" * 50)
        
        # Test with a portion of the resume content
        english_text = "Vladislav Zhiltsov is a Frontend Developer with experience in React.js, Redux, and modern web technologies. He has a B.Sc. in Mechanical Engineering from Technion."
        
        translation_data = {
            "text": english_text,
            "target_language": "rus",
            "context": "professional",
            "industry": "technology"
        }
        
        success, response = self.run_test(
            "English Language Detection (Resume Content)",
            "POST",
            "translate",
            200,
            data=translation_data
        )
        
        if success:
            detected_lang = response.get('source_language', '')
            translated_text = response.get('translated_text', '')
            
            print(f"   Original text: {english_text[:100]}...")
            print(f"   Detected language: {detected_lang}")
            print(f"   Expected: eng, Got: {detected_lang}")
            
            if detected_lang == 'eng':
                print("   ✅ CRITICAL: English language detection PASSED")
            else:
                print(f"   ❌ CRITICAL FAILURE: English language detection FAILED - detected as {detected_lang}")
                self.failed_tests.append({
                    'name': 'English Language Detection',
                    'expected': 'eng',
                    'actual': detected_lang,
                    'response': 'English resume content not detected as English'
                })
            
            if translated_text:
                print(f"   Russian translation: {translated_text[:100]}...")
                
                # Check for Cyrillic characters
                cyrillic_chars = sum(1 for char in translated_text if '\u0400' <= char <= '\u04ff')
                if cyrillic_chars > 10:
                    print("   ✅ CRITICAL: Translation contains Russian (Cyrillic) characters")
                else:
                    print("   ❌ CRITICAL FAILURE: Translation does not contain Russian characters")
        
        return success

def main():
    print("🎯 VLADISLAV RESUME TRANSLATION TESTING")
    print("Testing document processing with actual English resume content for translation to Russian")
    print("=" * 80)
    
    tester = VladislavResumeTranslationTester()
    
    # Run the critical tests
    print("\n🔥 CRITICAL TESTS - Real Document Translation (English → Russian)")
    print("=" * 80)
    
    # Test 1: Process actual resume content as PDF
    tester.test_resume_pdf_processing_english_to_russian()
    
    # Test 2: Verify English language detection
    tester.test_english_language_detection_verification()
    
    # Test 3: Test download functionality
    tester.test_download_russian_translation()
    
    # Print final results
    print("\n" + "=" * 80)
    print("📊 VLADISLAV RESUME TRANSLATION TEST RESULTS")
    print("=" * 80)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(tester.failed_tests)}")
    
    if tester.tests_run > 0:
        success_rate = (tester.tests_passed / tester.tests_run) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    if tester.failed_tests:
        print("\n❌ CRITICAL FAILURES FOUND:")
        for i, test in enumerate(tester.failed_tests, 1):
            print(f"\n{i}. {test['name']}")
            if 'expected' in test:
                print(f"   Expected: {test['expected']}")
                print(f"   Actual: {test['actual']}")
            if 'error' in test:
                print(f"   Error: {test['error']}")
            if 'response' in test:
                print(f"   Details: {test['response']}")
    else:
        print("\n✅ ALL CRITICAL TESTS PASSED!")
        print("✅ Document processing works with real content (not sample text)")
        print("✅ English language detection working correctly")
        print("✅ Russian translation working correctly")
        print("✅ Download functionality working correctly")
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())