import requests
import json

def test_german_detection():
    """Test the exact German text mentioned by the user"""
    
    # The exact German text from the user's request
    german_text = "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee und das Schellen der Glöckchen am Zaumzeug der Haflinger-Pferde klingen wie süße Musik in der klaren Bergluft."
    
    print("🇩🇪 TESTING GERMAN LANGUAGE DETECTION")
    print("=" * 60)
    print(f"Text: {german_text}")
    print("=" * 60)
    
    # Test with auto-detection
    url = "https://comprende-comms.preview.emergentagent.com/api/translate"
    
    data = {
        "text": german_text,
        "target_language": "eng",
        "context": "general",
        "industry": "general"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            detected_lang = result.get('source_language', 'unknown')
            translated_text = result.get('translated_text', '')
            confidence = result.get('confidence', 0)
            
            print(f"✅ API Response: {response.status_code}")
            print(f"🔍 Detected Language: {detected_lang}")
            print(f"🎯 Expected: 'deu' (German)")
            print(f"📝 Translation: {translated_text}")
            print(f"📊 Confidence: {confidence*100:.1f}%")
            
            # Critical check
            if detected_lang == 'deu':
                print("\n✅ SUCCESS: German text correctly detected as 'deu'")
                return True
            elif detected_lang == 'spa':
                print("\n❌ CRITICAL FAILURE: German text incorrectly detected as Spanish ('spa')")
                return False
            else:
                print(f"\n⚠️  ISSUE: German text detected as '{detected_lang}' instead of 'deu'")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {str(e)}")
        return False

def test_multiple_german_texts():
    """Test various German texts to ensure consistent detection"""
    
    german_texts = [
        "Guten Morgen! Wie geht es Ihnen heute?",
        "Das Wetter ist heute sehr schön und sonnig.",
        "Ich möchte gerne einen Kaffee bestellen, bitte.",
        "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee und das Schellen der Glöckchen am Zaumzeug der Haflinger-Pferde klingen wie süße Musik in der klaren Bergluft.",
        "Die deutsche Sprache hat viele interessante Wörter und Ausdrücke."
    ]
    
    print("\n🔄 TESTING MULTIPLE GERMAN TEXTS")
    print("=" * 60)
    
    url = "https://comprende-comms.preview.emergentagent.com/api/translate"
    all_passed = True
    
    for i, text in enumerate(german_texts, 1):
        print(f"\nTest {i}: {text[:50]}...")
        
        data = {
            "text": text,
            "target_language": "eng",
            "context": "general",
            "industry": "general"
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result.get('source_language', 'unknown')
                
                if detected_lang == 'deu':
                    print(f"   ✅ Correctly detected as German ('deu')")
                elif detected_lang == 'spa':
                    print(f"   ❌ FAILED: Detected as Spanish ('spa') instead of German")
                    all_passed = False
                else:
                    print(f"   ⚠️  Detected as '{detected_lang}' instead of German")
                    all_passed = False
            else:
                print(f"   ❌ API Error: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Request Error: {str(e)}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚨 GERMAN LANGUAGE DETECTION CRITICAL TEST")
    print("Testing the specific issue reported by the user")
    print("Expected: German text should be detected as 'deu', NOT 'spa'")
    print()
    
    # Test the exact text mentioned by user
    main_test_passed = test_german_detection()
    
    # Test multiple German texts for consistency
    multiple_tests_passed = test_multiple_german_texts()
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if main_test_passed:
        print("✅ MAIN TEST: German detection working correctly")
    else:
        print("❌ MAIN TEST: German detection FAILED")
    
    if multiple_tests_passed:
        print("✅ REGRESSION TESTS: All German texts detected correctly")
    else:
        print("❌ REGRESSION TESTS: Some German texts not detected correctly")
    
    if main_test_passed and multiple_tests_passed:
        print("\n🎉 ALL TESTS PASSED: German language detection is working correctly")
        exit(0)
    else:
        print("\n🚨 TESTS FAILED: German language detection needs attention")
        exit(1)