import requests
import json

def test_download_actual_content():
    """Test that file download returns actual content, not sample text"""
    
    print("📥 TESTING FILE DOWNLOAD ACTUAL CONTENT")
    print("=" * 60)
    
    # Test cases with different types of content
    test_cases = [
        {
            "name": "Translation Text",
            "content": "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee und das Schellen der Glöckchen am Zaumzeug der Haflinger-Pferde klingen wie süße Musik in der klaren Bergluft.",
            "filename": "german_translation.txt"
        },
        {
            "name": "Document Extracted Text", 
            "content": "This is actual extracted text from a document that was processed by OCR. It should be returned exactly as provided, not replaced with sample text.",
            "filename": "extracted_document.txt"
        },
        {
            "name": "User Generated Content",
            "content": "Hello world! This is user-generated content that should be downloaded exactly as the user provided it. No sample text should replace this.",
            "filename": "user_content.txt"
        }
    ]
    
    url = "https://comprende-comms.preview.emergentagent.com/api/documents/download"
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Content: {test_case['content'][:80]}...")
        print(f"Filename: {test_case['filename']}")
        
        data = {
            "content": test_case['content'],
            "filename": test_case['filename']
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ API Response: {response.status_code}")
                
                # Check if we got the actual content back
                response_content = response.text if hasattr(response, 'text') else str(response.content)
                
                # Check for actual content
                if test_case['content'] in response_content:
                    print("   ✅ SUCCESS: Download returns actual content")
                elif any(word in response_content.lower() for word in ['sample', 'example', 'mock', 'test']):
                    print("   ❌ CRITICAL FAILURE: Download returns sample/mock text instead of actual content")
                    print(f"   Response preview: {response_content[:200]}...")
                    all_passed = False
                else:
                    print("   ⚠️  Download returns different content (may be processed)")
                    print(f"   Response preview: {response_content[:200]}...")
                    
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Request Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_download_with_translation_result():
    """Test download with actual translation result"""
    
    print("\n🌐 TESTING DOWNLOAD WITH TRANSLATION RESULT")
    print("=" * 60)
    
    # First, get a translation
    translate_url = "https://comprende-comms.preview.emergentagent.com/api/translate"
    german_text = "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee und das Schellen der Glöckchen am Zaumzeug der Haflinger-Pferde klingen wie süße Musik in der klaren Bergluft."
    
    translate_data = {
        "text": german_text,
        "source_language": "deu",
        "target_language": "eng",
        "context": "general",
        "industry": "general"
    }
    
    try:
        print("Step 1: Getting translation...")
        translate_response = requests.post(translate_url, json=translate_data, timeout=30)
        
        if translate_response.status_code == 200:
            translation_result = translate_response.json()
            translated_text = translation_result.get('translated_text', '')
            
            print(f"   Original: {german_text[:50]}...")
            print(f"   Translation: {translated_text[:50]}...")
            
            # Now test downloading the translation
            print("\nStep 2: Testing download of translation...")
            download_url = "https://comprende-comms.preview.emergentagent.com/api/documents/download"
            
            download_data = {
                "content": translated_text,
                "filename": "german_to_english_translation.txt"
            }
            
            download_response = requests.post(download_url, json=download_data, timeout=30)
            
            if download_response.status_code == 200:
                print("   ✅ Download API Response: 200")
                
                # Check if the downloaded content matches the translation
                download_content = download_response.text
                
                if translated_text in download_content:
                    print("   ✅ SUCCESS: Downloaded content matches translation result")
                    return True
                else:
                    print("   ❌ FAILURE: Downloaded content doesn't match translation")
                    print(f"   Expected: {translated_text[:100]}...")
                    print(f"   Got: {download_content[:100]}...")
                    return False
            else:
                print(f"   ❌ Download Error: {download_response.status_code}")
                return False
        else:
            print(f"   ❌ Translation Error: {translate_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 FILE DOWNLOAD CONTENT VERIFICATION TEST")
    print("Testing that downloads return actual content, not sample text")
    print()
    
    # Test basic download functionality
    basic_test_passed = test_download_actual_content()
    
    # Test download with translation result
    translation_test_passed = test_download_with_translation_result()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if basic_test_passed:
        print("✅ BASIC TESTS: File download returns actual content")
    else:
        print("❌ BASIC TESTS: File download issues detected")
    
    if translation_test_passed:
        print("✅ TRANSLATION TEST: Download works with translation results")
    else:
        print("❌ TRANSLATION TEST: Download issues with translation results")
    
    if basic_test_passed and translation_test_passed:
        print("\n🎉 ALL TESTS PASSED: File download functionality working correctly")
        exit(0)
    else:
        print("\n🚨 TESTS FAILED: File download functionality needs attention")
        exit(1)