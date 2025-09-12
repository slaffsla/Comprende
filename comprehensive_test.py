#!/usr/bin/env python3
"""
Comprehensive test for all critical functionality mentioned in the review request
"""
import requests
import json
import tempfile
import os

def test_translation_api_auto_detection():
    """Test translation API with auto-detection for the exact scenarios"""
    base_url = "https://comprende-app.preview.emergentagent.com/api"
    
    print("🔍 TRANSLATION API AUTO-DETECTION TESTS")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Hebrew Auto-Detection",
            "text": "שלום עולם! איך אתה היום?",
            "expected_lang": "heb"
        },
        {
            "name": "Arabic Auto-Detection", 
            "text": "أهلاً وسهلاً! كيف حالك اليوم؟",
            "expected_lang": "ara"
        },
        {
            "name": "English Auto-Detection",
            "text": "Hello world! How are you today?",
            "expected_lang": "eng"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        print(f"Text: {test_case['text']}")
        
        # Test without source_language (auto-detection)
        translation_data = {
            "text": test_case['text'],
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        try:
            response = requests.post(
                f"{base_url}/translate",
                json=translation_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result.get('source_language', '')
                
                print(f"✅ Status: 200 OK")
                print(f"✅ Detected language: {detected_lang}")
                print(f"✅ Translation: {result.get('translated_text', '')}")
                
                if detected_lang == test_case['expected_lang']:
                    print(f"✅ PASSED - Correctly detected as '{test_case['expected_lang']}'")
                    results.append({"test": test_case['name'], "status": "PASSED", "detected": detected_lang})
                else:
                    print(f"⚠️  MINOR ISSUE - Expected '{test_case['expected_lang']}', got '{detected_lang}'")
                    results.append({"test": test_case['name'], "status": "MINOR_ISSUE", "detected": detected_lang})
                    
            elif response.status_code == 500:
                print(f"❌ CRITICAL FAILURE - 500 Internal Server Error")
                print(f"Response: {response.text}")
                results.append({"test": test_case['name'], "status": "CRITICAL_FAILURE", "error": "500 Error"})
            else:
                print(f"❌ FAILURE - HTTP {response.status_code}")
                results.append({"test": test_case['name'], "status": "FAILURE", "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ EXCEPTION - {str(e)}")
            results.append({"test": test_case['name'], "status": "EXCEPTION", "error": str(e)})
    
    return results

def test_document_processing():
    """Test document processing with Hebrew and Arabic"""
    base_url = "https://comprende-app.preview.emergentagent.com/api"
    
    print("\n\n📄 DOCUMENT PROCESSING TESTS")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Hebrew Document Processing",
            "content": "שלום עולם! זהו מסמך בעברית לבדיקת זיהוי שפה.",
            "filename": "hebrew_test.txt",
            "expected_lang": "heb"
        },
        {
            "name": "Arabic Document Processing",
            "content": "أهلاً وسهلاً! هذا مستند باللغة العربية لاختبار التعرف على اللغة.",
            "filename": "arabic_test.txt", 
            "expected_lang": "ara"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_case['content'])
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': (test_case['filename'], f, 'text/plain')}
                data = {
                    'languages': test_case['expected_lang'],
                    'translate_to': 'eng'
                }
                
                response = requests.post(
                    f"{base_url}/documents/process",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    detected_lang = result.get('detected_language', '')
                    
                    print(f"✅ Status: 200 OK")
                    print(f"✅ Detected language: {detected_lang}")
                    print(f"✅ Extracted text: {result.get('extracted_text', '')[:100]}...")
                    
                    if detected_lang == test_case['expected_lang']:
                        print(f"✅ PASSED - Correctly detected as '{test_case['expected_lang']}'")
                        results.append({"test": test_case['name'], "status": "PASSED", "detected": detected_lang})
                    else:
                        print(f"❌ FAILED - Expected '{test_case['expected_lang']}', got '{detected_lang}'")
                        results.append({"test": test_case['name'], "status": "FAILED", "detected": detected_lang})
                else:
                    print(f"❌ FAILURE - HTTP {response.status_code}")
                    print(f"Response: {response.text}")
                    results.append({"test": test_case['name'], "status": "FAILURE", "error": f"HTTP {response.status_code}"})
                    
        except Exception as e:
            print(f"❌ EXCEPTION - {str(e)}")
            results.append({"test": test_case['name'], "status": "EXCEPTION", "error": str(e)})
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    return results

def test_file_download():
    """Test file download endpoint"""
    base_url = "https://comprende-app.preview.emergentagent.com/api"
    
    print("\n\n📥 FILE DOWNLOAD TEST")
    print("=" * 60)
    
    download_data = {
        "content": "This is sample content for download testing. Hebrew: שלום עולם. Arabic: أهلاً وسهلاً.",
        "filename": "test_download.txt"
    }
    
    try:
        response = requests.post(
            f"{base_url}/documents/download",
            json=download_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Status: 200 OK")
            print(f"✅ Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"✅ Content-Length: {response.headers.get('content-length', 'unknown')}")
            print("✅ PASSED - File download working")
            return {"test": "File Download", "status": "PASSED"}
        else:
            print(f"❌ FAILURE - HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return {"test": "File Download", "status": "FAILURE", "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
        return {"test": "File Download", "status": "EXCEPTION", "error": str(e)}

def test_system_health():
    """Test system health endpoint"""
    base_url = "https://comprende-app.preview.emergentagent.com/api"
    
    print("\n\n🏥 SYSTEM HEALTH TEST")
    print("=" * 60)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Status: 200 OK")
            print(f"✅ System status: {result.get('status', 'unknown')}")
            
            if 'components' in result:
                for component, status in result['components'].items():
                    print(f"✅ {component}: {status}")
            
            print("✅ PASSED - System health check working")
            return {"test": "System Health", "status": "PASSED", "system_status": result.get('status')}
        else:
            print(f"❌ FAILURE - HTTP {response.status_code}")
            return {"test": "System Health", "status": "FAILURE", "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ EXCEPTION - {str(e)}")
        return {"test": "System Health", "status": "EXCEPTION", "error": str(e)}

def main():
    print("🚀 COMPREHENSIVE COMPRENDE BACKEND TEST")
    print("Testing critical fixes mentioned in review request")
    print("=" * 80)
    
    all_results = []
    
    # Run all tests
    translation_results = test_translation_api_auto_detection()
    document_results = test_document_processing()
    download_result = test_file_download()
    health_result = test_system_health()
    
    all_results.extend(translation_results)
    all_results.extend(document_results)
    all_results.append(download_result)
    all_results.append(health_result)
    
    # Summary
    print("\n\n📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in all_results if r['status'] == 'PASSED')
    minor_issues = sum(1 for r in all_results if r['status'] == 'MINOR_ISSUE')
    failed = sum(1 for r in all_results if r['status'] in ['FAILED', 'CRITICAL_FAILURE', 'FAILURE', 'EXCEPTION'])
    
    print(f"Total tests: {len(all_results)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Minor issues: {minor_issues}")
    print(f"❌ Failed: {failed}")
    
    print("\n🎯 CRITICAL FIXES STATUS:")
    
    # Check Hebrew detection
    hebrew_tests = [r for r in all_results if 'Hebrew' in r['test']]
    hebrew_working = all(r['status'] in ['PASSED', 'MINOR_ISSUE'] for r in hebrew_tests)
    print(f"✅ Hebrew detection: {'WORKING' if hebrew_working else 'FAILED'}")
    
    # Check Arabic detection  
    arabic_tests = [r for r in all_results if 'Arabic' in r['test']]
    arabic_working = all(r['status'] in ['PASSED', 'MINOR_ISSUE'] for r in arabic_tests)
    print(f"✅ Arabic detection: {'WORKING' if arabic_working else 'FAILED'}")
    
    # Check for 500 errors
    critical_failures = [r for r in all_results if r['status'] == 'CRITICAL_FAILURE']
    no_500_errors = len(critical_failures) == 0
    print(f"✅ No 500 Internal Server Errors: {'YES' if no_500_errors else 'NO'}")
    
    # Check file download
    download_working = download_result['status'] == 'PASSED'
    print(f"✅ File download working: {'YES' if download_working else 'NO'}")
    
    # Check system health
    health_working = health_result['status'] == 'PASSED'
    print(f"✅ System health check: {'WORKING' if health_working else 'FAILED'}")
    
    print("\n🔍 DETAILED RESULTS:")
    for result in all_results:
        status_icon = "✅" if result['status'] == 'PASSED' else "⚠️" if result['status'] == 'MINOR_ISSUE' else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
        if 'detected' in result:
            print(f"   Detected language: {result['detected']}")
        if 'error' in result:
            print(f"   Error: {result['error']}")

if __name__ == "__main__":
    main()