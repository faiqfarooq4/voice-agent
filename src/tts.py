import pyttsx3
from loguru import logger

class TTS:
    def __init__(self, config):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('voice', config.get('voice', 'com.apple.speech.synthesis.voice.Alex'))

    def speak(self, text):
        try:
            logger.info(f"Generating TTS for: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            return True  # Indicate success
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False