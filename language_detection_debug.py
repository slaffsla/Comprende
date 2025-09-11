import requests
import json

def test_language_detection():
    """Debug language detection issues"""
    base_url = "https://comprende-comms.preview.emergentagent.com/api"
    
    # Test cases with different English texts
    test_cases = [
        {
            "name": "Simple English",
            "text": "Hello world, how are you today?",
            "expected": "eng"
        },
        {
            "name": "Professional English",
            "text": "Vladislav Zhiltsov is a Frontend Developer with experience in React.js and Redux.",
            "expected": "eng"
        },
        {
            "name": "Technical English",
            "text": "JavaScript, TypeScript, HTML, CSS, React.js, Redux, Firebase, React Native, GIT",
            "expected": "eng"
        },
        {
            "name": "Resume Content",
            "text": "B.Sc. Mechanical Engineering Technion 2001-2006 Haifa, Israel. Developed visually appealing user interfaces and seamless user experiences using cutting-edge technologies.",
            "expected": "eng"
        },
        {
            "name": "German Text (Control)",
            "text": "Der gemächliche Rhythmus der Hufe auf dem frisch gefallenen Schnee",
            "expected": "deu"
        },
        {
            "name": "Spanish Text (Control)",
            "text": "Hola mundo, ¿cómo estás hoy? Este es un texto en español.",
            "expected": "spa"
        }
    ]
    
    print("🔍 LANGUAGE DETECTION DEBUG TEST")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Text: {test_case['text'][:80]}...")
        print(f"   Expected: {test_case['expected']}")
        
        # Test with translation API (auto-detect)
        translation_data = {
            "text": test_case['text'],
            "target_language": "rus"
        }
        
        try:
            response = requests.post(
                f"{base_url}/translate",
                json=translation_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                detected = result.get('source_language', 'unknown')
                print(f"   Detected: {detected}")
                
                if detected == test_case['expected']:
                    print("   ✅ CORRECT")
                else:
                    print(f"   ❌ INCORRECT - Expected {test_case['expected']}, got {detected}")
                    
                    # Show translation to verify it's working
                    translation = result.get('translated_text', '')
                    if translation:
                        print(f"   Translation: {translation[:100]}...")
            else:
                print(f"   ❌ API ERROR: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_language_detection()