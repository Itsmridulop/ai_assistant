from gtts import gTTS
from playsound import playsound
import os

class VoiceAssistant:
    def speak(self, text, filename="output.mp3"):
        tts = gTTS(text)
        tts.save(filename)
        playsound(filename)
        os.remove(filename)  

voice_assistant = VoiceAssistant()