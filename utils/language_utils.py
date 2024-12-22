from langdetect import detect, DetectorFactory
from googletrans import Translator

DetectorFactory.seed = 0
translator = Translator()

def detect_language(text):
    """Detects the language of the given text."""
    return detect(text) if text.strip() else 'en'

def transliterate_if_needed(text):
    """Transliterates the text to English if it's not already in English."""
    if not text or text.strip() == "":
        return "NA"
    try:
        language = detect_language(text)
        if language != 'en':
            translated_text = translator.translate(text, dest='en').text
            return translated_text
        return text
    except Exception as e:
        print(f"Error in transliteration: {e}")
        return "NA"

def get_language_mapping():
    """Returns the extended language mapping."""
    return {
        "AT": ("de", "eng"), "AU": ("eng", "eng"), "AZ": ("aze", "eng"), "BA": ("bos", "eng"),
        "BG": ("bul", "eng"), "BR": ("por", "eng"), "BY": ("bel", "eng"), "CA": ("eng", "eng"),
        "CH": ("de", "eng"), "CL": ("spa", "eng"), "CN": ("chi_sim", "eng"), "CO": ("spa", "eng"),
        "CU": ("spa", "eng"), "CZ": ("ces", "eng"), "DE": ("de", "eng"), "DK": ("da", "eng"),
        "DO": ("spa", "eng"), "DZ": ("ara", "eng"), "EA": ("eng", "eng"), "EG": ("ara", "eng"),
        "EP": ("eng", "eng"), "ES": ("spa", "eng"), "FI": ("fin", "eng"), "FR": ("fra", "eng"),
        "GB": ("eng", "eng"), "GE": ("geo", "eng"), "GR": ("gre", "eng"), "HR": ("hrv", "eng"),
        "HU": ("hun", "eng"), "IB": ("eng", "eng"), "IE": ("eng", "eng"), "IL": ("heb", "eng"),
        "IR": ("fas", "eng"), "IS": ("isl", "eng"), "IT": ("ita", "eng"), "JO": ("ara", "eng"),
        "JP": ("jpn", "eng"), "KE": ("eng", "eng"), "KR": ("kor", "eng"), "KZ": ("kaz", "eng"),
        "LV": ("lav", "eng"), "MA": ("ara", "eng"), "MD": ("ron", "eng"), "MX": ("spa", "eng"),
        "MY": ("eng", "eng"), "NL": ("nld", "eng"), "NO": ("nor", "eng"), "NZ": ("eng", "eng"),
        "OM": ("ara", "eng"), "PA": ("spa", "eng"), "PE": ("spa", "eng"), "PH": ("eng", "eng"),
        "PL": ("pol", "eng"), "PT": ("por", "eng"), "QA": ("ara", "eng"), "RO": ("ron", "eng"),
        "RS": ("srp", "eng"), "RU": ("rus", "eng"), "SA": ("ara", "eng"), "SD": ("ara", "eng"),
        "SE": ("swe", "eng"), "SG": ("eng", "eng"), "SI": ("slv", "eng"), "SK": ("slk", "eng"),
        "SY": ("ara", "eng"), "TH": ("tha", "eng"), "TN": ("ara", "eng"), "TR": ("tur", "eng"),
        "TT": ("eng", "eng"), "UA": ("ukr", "eng"), "US": ("eng", "eng"), "VN": ("vie", "eng"),
        "ZA": ("eng", "eng")
    }