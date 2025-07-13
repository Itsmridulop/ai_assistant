import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import speech_recognition as sr
import pyaudio
import platform
import numpy as np
from config import CHANNELS, RATE, CHUNK, PAUSE_DURATION, OUTPUT_FILE_NAME

class VoiceProcessing:
    def __init__(self):
        self.threshold = None

    def calculate_dynamic_threshold(self, ambient_data):
        ambient_array = np.frombuffer(b''.join(ambient_data), dtype=np.int16)
        avg_amplitude = np.abs(ambient_array).mean()
        return avg_amplitude * 2.0

    def is_silent(self, data, threshold):
        audio_data = np.frombuffer(data, dtype=np.int16)
        avg_amplitude = np.abs(audio_data).mean()
        return avg_amplitude < threshold

    def speech_to_text(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("Adjusting for ambient noise... Please wait.")
        ambient_data = []
        for _ in range(int(RATE / CHUNK * 5)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            ambient_data.append(data)
        
        self.threshold = self.calculate_dynamic_threshold(ambient_data)
        print(f"Dynamic silence threshold set to: {self.threshold:.2f}")
        
        print(f"Listening... Speak now. (Recording stops after {PAUSE_DURATION}s pause)")
        
        frames = []
        silent_chunks = 0
        max_silent_chunks = int(PAUSE_DURATION / 0.05) 
        max_duration_chunks = int(10 / 0.05)  
        speech_started = False
        
        try:
            for i in range(max_duration_chunks):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                silent = self.is_silent(data, self.threshold)
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
                
                if i % int(RATE / CHUNK) == 0:  
                    print(".", end="", flush=True)
            
            print("\nProcessing speech...")
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if not frames or not speech_started:
                print("Error: No speech detected.")
                return None
            
            audio_data = sr.AudioData(b''.join(frames), RATE, 2)  
            
            recognizer = sr.Recognizer()
            try:
                text = recognizer.recognize_google(audio_data)
                print("You said:", text)
                return text
            except sr.UnknownValueError:
                print("Error: Could not understand the audio.")
                return None
            except sr.RequestError as e:
                print(f"Error: Could not connect to Google Speech Recognition service; {e}")
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

    def take_speech(self):
        print(f"Running on {platform.system()} {platform.release()}")
        result = self.speech_to_text()
        
        if result:
            with open(OUTPUT_FILE_NAME, "a", encoding="utf-8") as f:
                f.write(result + '\n')
            print(f"Transcription saved to {OUTPUT_FILE_NAME}")
            return result
        else:
            print("No transcription to save.")
