import urllib.request
import urllib.parse
import json
import re
import html

def is_predominantly_turkish(text):
    """Check if text already contains Turkish specific characters or frequent words."""
    if not text or len(text.strip()) < 8:
        return True
    
    # Turkish specific letters
    tr_chars = set("çÇğĞıİöÖşŞüÜ")
    if any(c in tr_chars for c in text):
        return True
        
    text_lower = f" {text.lower()} "
    common_tr_words = [" ve ", " bir ", " için ", " bu ", " ile ", " da ", " de ", " gibi ", " kadar ", " sonra ", " olan ", " çok ", " en ", " hakkında ", " nasıl ", " neden "]
    if any(w in text_lower for w in common_tr_words):
        return True
        
    return False

def translate_to_turkish_fast(text):
    """Accurate zero-cost translator using MyMemory open translation API."""
    if not text or is_predominantly_turkish(text):
        return text
        
    try:
        # Take snippet to translate if very long
        clean_input = text[:400]
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(clean_input)}&langpair=autodetect|tr"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 agent-reach"})
        resp = urllib.request.urlopen(req, timeout=4)
        data = json.loads(resp.read().decode("utf-8"))
        translated = data.get("responseData", {}).get("translatedText")
        if translated and len(translated.strip()) > 3 and not translated.startswith("MYMEMORY WARNING"):
            return html.unescape(translated.strip())
    except Exception:
        pass
        
    return text
