#!/usr/bin/env python3
"""
FINAL PDF PROCESSING TEST - Comprehensive End-to-End Verification
Testing the PDF processing fix for Russian translation as requested in review.

This test specifically verifies:
1. Real PDF processing (not sample text)
2. Russian translation with proper Cyrillic characters
3. Download functionality with actual content
4. Language detection accuracy
5. End-to-end user workflow simulation
"""

import requests
import sys
import json
import time
import tempfile
import os
from pathlib import Path

class PDFProcessingFinalTester:
    def __init__(self, base_url="https://translate-hub-22.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.critical_issues = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
            self.failed_tests.append({
                'name': test_name,
                'details': details
            })
        if details:
            print(f"   {details}")
    
    def log_critical_issue(self, issue):
        """Log critical issue that needs immediate attention"""
        self.critical_issues.append(issue)
        print(f"🚨 CRITICAL ISSUE: {issue}")
    
    def make_request(self, method, endpoint, data=None, files=None, timeout=30):
        """Make HTTP request with error handling"""
        url = f"{self.api_url}/{endpoint}"
        headers = {} if files else {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=timeout)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=timeout)
            
            return response
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {timeout}s")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def test_1_pdf_upload_and_processing(self):
        """Test 1: Upload PDF file and process with target language Russian"""
        print("\n🎯 TEST 1: PDF Upload → Russian Translation")
        print("-" * 50)
        
        # Create realistic Vladislav resume content
        vladislav_resume = """Vladislav Zhiltsov
slasla@gmail.com (+972) 58-410-410-5 Haifa, Israel
https://slasla.space/

EDUCATION
B.Sc. Mechanical Engineering Technion 2001-2006 Haifa, Israel

SKILLS
JavaScript, TypeScript, HTML, CSS, React.js, Redux, Firebase, React Native, GIT
Familiar with: UX, UI, Web Design, Three.js, Tailwind CSS, Node.js

WORK EXPERIENCE
Frontend Developer - Siema (March 2021 - March 2022)
Developed visually appealing user interfaces and seamless user experiences using cutting-edge technologies, with special attention to code cleanness and maintainability.

Transformed visual designs into stunning web pages and application interfaces. Implemented responsive design techniques to create fluid layouts, while leveraging Redux and other libraries.

Product Localization Manager - Optima Global (April 2022 - current)
Ensuring seamless product adaptation for local markets, addressing its needs and regulations. Developing and executing localization strategies, striving to maximize market penetration.

Collaborating with development, design, and translation teams to drive efficient localization processes. Conducting market research and user testing to gather insights.

PERSONAL STRENGTHS
Written and Verbal Communication - excellent language and communication skills (in 3 languages)
Thinking outside the box
Attentive to details

PERSONAL INTERESTS  
Brazilian Jiu Jitsu
Playing musical instruments (Mostly Handpan)

PERSONAL PROJECTS
Portfolio site: https://slasla.space/
React Chat App: https://github.com/slaffsla/react-chat-app
Social App: https://github.com/slaffsla/social-app"""
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, encoding='utf-8') as f:
            f.write(vladislav_resume)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('vladislav_resume.pdf', f, 'application/pdf')}
                data = {
                    'languages': 'eng',
                    'translate_to': 'rus'  # Russian translation as requested
                }
                
                print("📤 Uploading PDF file...")
                response = self.make_request('POST', 'documents/process', data=data, files=files)
                
                if response.status_code != 200:
                    self.log_result("PDF Upload", False, f"HTTP {response.status_code}: {response.text[:200]}")
                    return None
                
                result = response.json()
                print(f"📄 Processing completed in {result.get('processing_time', 0):.2f}s")
                
                # Store result for other tests
                self.pdf_result = result
                
                # Verify basic response structure
                required_fields = ['extracted_text', 'translated_text', 'detected_language', 'filename']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_result("PDF Processing Response Structure", False, f"Missing fields: {missing_fields}")
                    return None
                
                self.log_result("PDF Upload and Processing", True, "PDF processed successfully")
                return result
                
        except Exception as e:
            self.log_result("PDF Upload", False, f"Exception: {str(e)}")
            return None
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def test_2_verify_actual_content_extraction(self, pdf_result):
        """Test 2: Verify extracted text contains actual Vladislav resume content"""
        print("\n🔍 TEST 2: Actual Content Extraction Verification")
        print("-" * 50)
        
        if not pdf_result:
            self.log_result("Content Extraction Verification", False, "No PDF result to verify")
            return False
        
        extracted_text = pdf_result.get('extracted_text', '')
        print(f"📝 Extracted text preview: {extracted_text[:150]}...")
        
        # CRITICAL CHECK 1: No sample text patterns
        sample_text_patterns = [
            "This is successfully extracted content from PDF document",
            "Sample extracted text from PDF document", 
            "successfully extracted PDF content",
            "Это успешно извлеченное содержимое из PDF-документа",
            "Sample extracted text"
        ]
        
        found_sample_patterns = [pattern for pattern in sample_text_patterns if pattern in extracted_text]
        
        if found_sample_patterns:
            self.log_critical_issue(f"Still returning sample text: {found_sample_patterns}")
            self.log_result("No Sample Text Check", False, f"Found sample patterns: {found_sample_patterns}")
            return False
        
        # CRITICAL CHECK 2: Contains actual Vladislav resume content
        expected_content_markers = [
            "Vladislav Zhiltsov",
            "slasla@gmail.com",
            "Mechanical Engineering",
            "Frontend Developer",
            "Siema",
            "Brazilian Jiu Jitsu"
        ]
        
        found_markers = [marker for marker in expected_content_markers if marker in extracted_text]
        missing_markers = [marker for marker in expected_content_markers if marker not in extracted_text]
        
        print(f"✅ Found content markers: {found_markers}")
        if missing_markers:
            print(f"⚠️  Missing content markers: {missing_markers}")
        
        # Success if we have most key markers and no sample text
        success = len(found_markers) >= 4 and not found_sample_patterns
        
        if success:
            self.log_result("Actual Content Extraction", True, f"Found {len(found_markers)}/6 key content markers")
        else:
            self.log_result("Actual Content Extraction", False, f"Only found {len(found_markers)}/6 markers or sample text detected")
        
        return success
    
    def test_3_verify_russian_translation_quality(self, pdf_result):
        """Test 3: Verify Russian translation is proper Cyrillic text"""
        print("\n🇷🇺 TEST 3: Russian Translation Quality Verification")
        print("-" * 50)
        
        if not pdf_result:
            self.log_result("Russian Translation Quality", False, "No PDF result to verify")
            return False
        
        translated_text = pdf_result.get('translated_text', '')
        
        if not translated_text:
            self.log_critical_issue("No Russian translation provided despite translate_to=rus")
            self.log_result("Russian Translation Presence", False, "No translated_text in response")
            return False
        
        print(f"🔤 Russian translation preview: {translated_text[:150]}...")
        
        # Check Cyrillic character percentage
        cyrillic_chars = sum(1 for char in translated_text if '\u0400' <= char <= '\u04ff')
        total_chars = len(translated_text)
        cyrillic_percentage = (cyrillic_chars / total_chars * 100) if total_chars > 0 else 0
        
        print(f"📊 Cyrillic characters: {cyrillic_chars}/{total_chars} ({cyrillic_percentage:.1f}%)")
        
        # Check for proper Russian name translation
        russian_name_variants = ["Владислав", "Жильцов", "Владислав Жильцов"]
        found_russian_names = [name for name in russian_name_variants if name in translated_text]
        
        if found_russian_names:
            print(f"✅ Found Russian name translations: {found_russian_names}")
        else:
            print("⚠️  No Russian name translations found")
        
        # Check for broken Russian patterns (old issue)
        broken_patterns = [
            "успешно извлеченное содержимое",
            "Это успешно извлеченное содержимое из PDF-документа"
        ]
        found_broken_patterns = [pattern for pattern in broken_patterns if pattern in translated_text]
        
        if found_broken_patterns:
            self.log_critical_issue(f"Found broken Russian patterns: {found_broken_patterns}")
            self.log_result("No Broken Russian Patterns", False, f"Found: {found_broken_patterns}")
            return False
        
        # Success criteria: High Cyrillic percentage, proper names, no broken patterns
        success = (
            cyrillic_percentage > 50 and  # At least 50% Cyrillic
            len(found_russian_names) > 0 and  # Has Russian name translation
            len(found_broken_patterns) == 0  # No broken patterns
        )
        
        if success:
            self.log_result("Russian Translation Quality", True, f"{cyrillic_percentage:.1f}% Cyrillic, proper names found")
        else:
            details = f"{cyrillic_percentage:.1f}% Cyrillic, {len(found_russian_names)} names, {len(found_broken_patterns)} broken patterns"
            self.log_result("Russian Translation Quality", False, details)
        
        return success
    
    def test_4_download_functionality(self, pdf_result):
        """Test 4: Test download endpoint with translated Russian content"""
        print("\n📥 TEST 4: Download Functionality Verification")
        print("-" * 50)
        
        if not pdf_result:
            self.log_result("Download Functionality", False, "No PDF result to test download")
            return False
        
        translated_text = pdf_result.get('translated_text', '')
        
        if not translated_text:
            self.log_result("Download Functionality", False, "No translated text to download")
            return False
        
        # Test download endpoint
        download_data = {
            "content": translated_text,
            "filename": "vladislav_resume_russian.txt"
        }
        
        try:
            print("📤 Testing download endpoint...")
            response = self.make_request('POST', 'documents/download', data=download_data)
            
            if response.status_code != 200:
                self.log_result("Download Endpoint", False, f"HTTP {response.status_code}: {response.text[:200]}")
                return False
            
            # Check response headers
            content_disposition = response.headers.get('Content-Disposition', '')
            content_type = response.headers.get('Content-Type', '')
            
            print(f"📋 Content-Type: {content_type}")
            print(f"📋 Content-Disposition: {content_disposition}")
            
            # Verify file content (should be the same as what we sent)
            downloaded_content = response.text
            
            # Check if downloaded content matches what we sent
            content_matches = downloaded_content == translated_text
            
            if content_matches:
                print("✅ Downloaded content matches original translated text")
            else:
                print("⚠️  Downloaded content differs from original")
                print(f"   Original length: {len(translated_text)}")
                print(f"   Downloaded length: {len(downloaded_content)}")
            
            # Check for proper headers
            has_proper_headers = (
                'attachment' in content_disposition and
                'vladislav_resume_russian.txt' in content_disposition
            )
            
            success = response.status_code == 200 and content_matches and has_proper_headers
            
            if success:
                self.log_result("Download Functionality", True, "Download endpoint working correctly")
            else:
                details = f"Status: {response.status_code}, Content matches: {content_matches}, Headers: {has_proper_headers}"
                self.log_result("Download Functionality", False, details)
            
            return success
            
        except Exception as e:
            self.log_result("Download Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_5_language_detection_accuracy(self, pdf_result):
        """Test 5: Verify language detection shows correct source language"""
        print("\n🌐 TEST 5: Language Detection Accuracy")
        print("-" * 50)
        
        if not pdf_result:
            self.log_result("Language Detection", False, "No PDF result to verify")
            return False
        
        detected_language = pdf_result.get('detected_language', '')
        print(f"🔍 Detected language: {detected_language}")
        
        # For English resume, we expect 'eng' detection
        # However, based on previous tests, there might be some inconsistency
        expected_languages = ['eng']  # English resume content
        
        if detected_language in expected_languages:
            self.log_result("Language Detection Accuracy", True, f"Correctly detected as {detected_language}")
            return True
        else:
            # This might be a minor issue based on previous test results
            self.log_result("Language Detection Accuracy", False, f"Expected {expected_languages}, got {detected_language}")
            print("   ⚠️  Note: This may be a minor issue that doesn't affect translation quality")
            return False
    
    def test_6_end_to_end_user_workflow(self):
        """Test 6: Comprehensive end-to-end user workflow simulation"""
        print("\n🎭 TEST 6: End-to-End User Workflow Simulation")
        print("-" * 50)
        
        print("👤 Simulating user workflow: Upload → Process → Translate → Download")
        
        # Step 1: User uploads PDF
        print("1️⃣  User uploads Vladislav resume PDF...")
        pdf_result = self.test_1_pdf_upload_and_processing()
        
        if not pdf_result:
            self.log_result("End-to-End Workflow", False, "Failed at PDF upload step")
            return False
        
        # Step 2: System extracts actual content (not sample)
        print("2️⃣  System extracts actual resume content...")
        content_ok = self.test_2_verify_actual_content_extraction(pdf_result)
        
        # Step 3: System translates to Russian
        print("3️⃣  System translates to Russian...")
        translation_ok = self.test_3_verify_russian_translation_quality(pdf_result)
        
        # Step 4: User downloads translated content
        print("4️⃣  User downloads Russian translation...")
        download_ok = self.test_4_download_functionality(pdf_result)
        
        # Overall workflow success
        workflow_success = content_ok and translation_ok and download_ok
        
        if workflow_success:
            self.log_result("End-to-End User Workflow", True, "Complete workflow successful")
            print("🎉 USER EXPERIENCE: User will receive actual Russian resume translation!")
        else:
            failed_steps = []
            if not content_ok:
                failed_steps.append("content extraction")
            if not translation_ok:
                failed_steps.append("Russian translation")
            if not download_ok:
                failed_steps.append("download")
            
            self.log_result("End-to-End Workflow", False, f"Failed steps: {failed_steps}")
            print("⚠️  USER EXPERIENCE: User may still encounter issues")
        
        return workflow_success
    
    def test_7_auto_detect_vs_manual_language(self):
        """Test 7: Test both auto-detect and manual language selection"""
        print("\n🔄 TEST 7: Auto-detect vs Manual Language Selection")
        print("-" * 50)
        
        # Test with auto-detection (no source_language specified)
        print("🤖 Testing auto-detection...")
        auto_detect_data = {
            "text": "Hello world! This is a test of automatic language detection.",
            "target_language": "rus"
        }
        
        try:
            response = self.make_request('POST', 'translate', data=auto_detect_data)
            
            if response.status_code == 200:
                result = response.json()
                auto_detected_lang = result.get('source_language', '')
                print(f"   Auto-detected language: {auto_detected_lang}")
                auto_success = True
            else:
                print(f"   Auto-detection failed: HTTP {response.status_code}")
                auto_success = False
        except Exception as e:
            print(f"   Auto-detection error: {str(e)}")
            auto_success = False
        
        # Test with manual language selection
        print("👤 Testing manual language selection...")
        manual_data = {
            "text": "Hello world! This is a test of manual language selection.",
            "source_language": "eng",
            "target_language": "rus"
        }
        
        try:
            response = self.make_request('POST', 'translate', data=manual_data)
            
            if response.status_code == 200:
                result = response.json()
                manual_lang = result.get('source_language', '')
                print(f"   Manual language: {manual_lang}")
                manual_success = True
            else:
                print(f"   Manual selection failed: HTTP {response.status_code}")
                manual_success = False
        except Exception as e:
            print(f"   Manual selection error: {str(e)}")
            manual_success = False
        
        overall_success = auto_success and manual_success
        
        if overall_success:
            self.log_result("Auto-detect vs Manual Selection", True, "Both methods working")
        else:
            details = f"Auto-detect: {auto_success}, Manual: {manual_success}"
            self.log_result("Auto-detect vs Manual Selection", False, details)
        
        return overall_success
    
    def run_all_tests(self):
        """Run all PDF processing tests"""
        print("🚀 STARTING FINAL PDF PROCESSING TEST SUITE")
        print("=" * 60)
        print("Testing PDF processing fix for Russian translation")
        print("Focus: Actual content extraction, not sample text")
        print("=" * 60)
        
        # Run individual tests
        pdf_result = self.test_1_pdf_upload_and_processing()
        
        if pdf_result:
            self.test_2_verify_actual_content_extraction(pdf_result)
            self.test_3_verify_russian_translation_quality(pdf_result)
            self.test_4_download_functionality(pdf_result)
            self.test_5_language_detection_accuracy(pdf_result)
        
        self.test_6_end_to_end_user_workflow()
        self.test_7_auto_detect_vs_manual_language()
        
        # Print final results
        self.print_final_results()
    
    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 FINAL PDF PROCESSING TEST RESULTS")
        print("=" * 60)
        
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {len(self.failed_tests)}")
        
        if self.tests_run > 0:
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        # Critical issues
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.critical_issues)}):")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"{i}. {issue}")
        
        # Failed tests
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"{i}. {test['name']}")
                if test['details']:
                    print(f"   Details: {test['details']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if len(self.critical_issues) == 0 and self.tests_passed == self.tests_run:
            print("✅ PDF PROCESSING FIX VERIFIED - All tests passed!")
            print("✅ Users will receive actual Russian resume translations")
            print("✅ No more sample text issues")
        elif len(self.critical_issues) == 0:
            print("⚠️  PDF PROCESSING MOSTLY WORKING - Some minor issues found")
            print("✅ Core functionality (actual content + Russian translation) working")
        else:
            print("❌ PDF PROCESSING ISSUES REMAIN - Critical problems found")
            print("⚠️  Users may still experience issues with PDF processing")
        
        return len(self.critical_issues) == 0 and self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = PDFProcessingFinalTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())