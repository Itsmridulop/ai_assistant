import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import speech_recognition as sr
import pyaudio
import numpy as np
from modules.output import voice_assistant
from config import Config

class VoiceProcessing(Config):
    def __init__(self):
        super().__init__()

    def is_silent(self, data, threshold):
        """Check if audio chunk is silent based on dynamic threshold."""
        audio_data = np.frombuffer(data, dtype=np.int16)
        avg_amplitude = np.abs(audio_data).mean()
        return avg_amplitude < threshold

    def speech_to_text(self, threshold):
        """Convert speech to text, stopping after a 1.5s pause."""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
    
        
        frames = []
        silent_chunks = 0
        max_silent_chunks = int(self.PAUSE_DURATION / 0.05)
        speech_started = False
        
        try:
            while True:
                # print("Listening...")
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)

                silent = self.is_silent(data, threshold)
                if silent:
                    if speech_started:
                        silent_chunks += 1
                        if silent_chunks >= max_silent_chunks:
                            print("\nDetected 1.5s pause. Stopping recording.")
                            break
                else:
                    if not speech_started:
                        speech_started = True
                    silent_chunks = 0
                
        
            voice_assistant.speak("Processing your speech, please wait...")
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if not frames or not speech_started:
                voice_assistant.speak("No speech detected.")
                return None
            
            audio_data = sr.AudioData(b''.join(frames), self.RATE, 2)
            
            recognizer = sr.Recognizer()
            try:
                text = recognizer.recognize_google(audio_data)
                voice_assistant.speak(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                # voice_assistant.speak("Could not understand the audio.")
                return None
            except sr.RequestError as e:
                voice_assistant.speak("Could not connect to Google Speech Recognition service.")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None
                
        except Exception as e:
            print(f"\nError during recording: {e}")
            stream.stop_stream()
            stream.close()
            p.terminate()
            return None

    def take_speech(self, threshold):
        """Run the speech-to-text process and save the result."""
        result = self.speech_to_text(threshold)
        
        if result:
            with open(self.OUTPUT_FILE_NAME, "a", encoding="utf-8") as f:
                f.write(result + '\n')
            print(f"Transcription saved to {self.OUTPUT_FILE_NAME}")
            return result
        else:
            print("No transcription to save.")

voice = VoiceProcessing()