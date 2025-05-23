import os
import tempfile
from gtts import gTTS
import logging

logger = logging.getLogger(__name__)

def synthesize(text, lang='uk'):
    """
    Synthesize text to speech using Google Text-to-Speech.
    
    Args:
        text (str): Text to synthesize.
        lang (str): Language code (default: 'uk' for Ukrainian).
    
    Returns:
        str: Path to the generated audio file.
    """
    try:
        # Create a temporary file to store the audio
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        
        # Map language code to gTTS supported language with fallbacks
        language_map = {
            'uk': 'uk',  # Ukrainian
            'en': 'en',  # English
            'de': 'de',  # German
            'ru': 'ru',  # Russian
            # Add more language mappings as needed
        }
        
        # Use the mapped language or default to English if not supported
        tts_lang = language_map.get(lang, 'en')
        
        # For debugging
        logger.info(f"Synthesizing speech with language: {tts_lang}, text length: {len(text)}")
        
        try:
            # Generate speech
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            tts.save(temp_file.name)
            
            logger.info(f"Successfully generated audio file: {temp_file.name}")
            return temp_file.name
        except ValueError as e:
            # Language might not be supported, try English as fallback
            logger.warning(f"Language {tts_lang} failed, trying English: {str(e)}")
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file.name)
            logger.info(f"Generated fallback audio file in English: {temp_file.name}")
            return temp_file.name
    
    except Exception as e:
        logger.exception(f"Error synthesizing speech: {str(e)}")
        # Return a path to a default error message audio or None
        return None
