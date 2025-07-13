from modules.voice_input import VoiceProcessing

voice=VoiceProcessing()
input_text = voice.take_speech()
print(input_text)