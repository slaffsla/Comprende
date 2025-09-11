#!/usr/bin/env python3
"""
Focused test for the specific language detection scenarios mentioned in the review request
"""
import requests
import json

def test_specific_language_detection():
    """Test the exact text samples from the review request"""
    base_url = "https://comprende-comms.preview.emergentagent.com/api"
    
    # Test cases from the review request
    test_cases = [
        {
            "name": "Hebrew Auto-Detection",
            "text": "שלום עולם! איך אתה היום?",
            "expected_lang": "heb",
            "description": "Hebrew text should be detected as 'heb'"
        },
        {
            "name": "Arabic Auto-Detection", 
            "text": "أهلاً وسهلاً! كيف حالك اليوم؟",
            "expected_lang": "ara",
            "description": "Arabic text should be detected as 'ara'"
        },
        {
            "name": "English Auto-Detection",
            "text": "Hello world! How are you today?",
            "expected_lang": "eng", 
            "description": "English text should be detected as 'eng'"
        }
    ]
    
    print("🔍 FOCUSED LANGUAGE DETECTION TESTS")
    print("=" * 50)
    print("Testing the exact scenarios from the review request...")
    print()
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        print(f"Expected: {test_case['expected_lang']}")
        
        # Test translation API with auto-detection (no source_language provided)
        translation_data = {
            "text": test_case['text'],
            "target_language": "eng",  # Translate to English
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
                
                print(f"Detected: {detected_lang}")
                print(f"Translation: {result.get('translated_text', '')}")
                
                if detected_lang == test_case['expected_lang']:
                    print("✅ PASSED - Language correctly detected")
                else:
                    print(f"❌ FAILED - Expected {test_case['expected_lang']}, got {detected_lang}")
                    all_passed = False
                    
            elif response.status_code == 500:
                print("❌ FAILED - 500 Internal Server Error (ObjectId serialization issue)")
                print(f"Response: {response.text}")
                all_passed = False
            else:
                print(f"❌ FAILED - HTTP {response.status_code}")
                print(f"Response: {response.text}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            all_passed = False
            
        print("-" * 50)
    
    print("\n🎯 SUMMARY")
    if all_passed:
        print("✅ ALL LANGUAGE DETECTION TESTS PASSED")
        print("✅ Hebrew text correctly detected as 'heb'")
        print("✅ Arabic text correctly detected as 'ara'") 
        print("✅ English text correctly detected as 'eng'")
        print("✅ No more 500 Internal Server Error for auto-detection")
        print("✅ MongoDB ObjectId serialization issues resolved")
    else:
        print("❌ SOME TESTS FAILED - Issues still exist")
    
    return all_passed

if __name__ == "__main__":
    test_specific_language_detection()