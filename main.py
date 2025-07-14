from modules.voice_input import VoiceProcessing
from modules.intent_recognition import IntentRecognizer

voice=VoiceProcessing()
input_text = voice.take_speech()
if input_text:
	recognizer = IntentRecognizer()
	recognizer.recognize(input_text)
