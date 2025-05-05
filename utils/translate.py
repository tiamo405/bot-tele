import requests

def translate_text(text, source="auto", target="vi"):
    """
    Translate text using LibreTranslate API
    
    Args:
        text (str): Text to translate
        source (str): Source language code (default: auto)
        target (str): Target language code (default: vi)
        
    Returns:
        dict: Translation response
    """
    url = "https://libretranslate.com/translate"
    
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text",
        "alternatives": 3,
        "api_key": ""
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    # Example usage
    text_to_translate = "Hello, how are you?"
    translation = translate_text(text_to_translate)
    print(translation)