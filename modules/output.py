from gtts import gTTS
from playsound import playsound
import os
import time

class VoiceAssistant:
    def speak(self, text, filename="output.mp3"):
        tts = gTTS(text)
        tts.save(filename)
        playsound(filename)
        time.sleep(0.1)
        os.remove(filename)  

voice_assistant = VoiceAssistant()