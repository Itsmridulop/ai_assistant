import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import pyaudio
import numpy as np
import logging
import speech_recognition as sr
from collections import deque
from config import Config
from modules.output import voice_assistant
from modules.voice_input import voice
from modules.task_executor import executor
from modules.intent_recognition import recognizer
from modules.assistant_gui import AssistantGUI
from PyQt5.QtWidgets import QApplication

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
sys.tracebacklimit = 0

class CypherAi(Config):
    def __init__(self):
        super().__init__()
        logging.basicConfig(
            filename="assistant.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        self.audio_buffer = deque(maxlen=int(self.RATE * 10 / self.CHUNK)) 
        self.is_listening = False
        self.is_running = True
        self.stream_active = False
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recognizer = sr.Recognizer()
        
        # Initialize GUI
        self.app = QApplication(sys.argv)
        self.gui = AssistantGUI()
        self.gui.hide()  # Hide GUI initially
        self.logger.info("GUI initialized and hidden")

        self.initialize_silence_threshold()

    def initialize_silence_threshold(self):
        """Initialize SILENCE_THRESHOLD by calculating ambient noise level"""
        try:
            temp_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            self.logger.info("Temporary audio stream opened for threshold calculation")
            
            ambient_data = []
            for _ in range(int(self.RATE / self.CHUNK * 5)):
                data = temp_stream.read(self.CHUNK, exception_on_overflow=False)
                ambient_data.append(data)
            
            temp_stream.stop_stream()
            temp_stream.close()
            
            self.SILENCE_THRESHOLD = self.calculate_dynamic_threshold(ambient_data)
            self.logger.info(f"Initial SILENCE_THRESHOLD set to {self.SILENCE_THRESHOLD}")
        except Exception as e:
            self.logger.error(f"Failed to calculate initial silence threshold: {e}")
            self.SILENCE_THRESHOLD = 300
            voice_assistant.speak("Failed to initialize audio threshold")

    def is_silent(self, data, threshold):
        """Check if audio data is silent based on the threshold"""
        if not data:
            return True
        try:
            audio_data = np.frombuffer(data, dtype=np.int16)
            avg_amplitude = np.abs(audio_data).mean()
            return avg_amplitude < threshold
        except:
            return True

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback for continuous listening"""
        self.audio_buffer.append(in_data)
        return (in_data, pyaudio.paContinue)

    def detect_wake_word(self):
        """Detect wake word using speech_recognition in-memory processing"""
        if not self.audio_buffer:
            self.logger.debug("Audio buffer empty")
            return False

        try:
            latest_chunk = self.audio_buffer[-1] if self.audio_buffer else b''
            if self.is_silent(latest_chunk, self.SILENCE_THRESHOLD):
                self.logger.debug("Audio is silent, skipping wake word detection")
                return False
            logging.info("Detecting wake word...")
            audio_array = np.frombuffer(b''.join(list(self.audio_buffer)), dtype=np.int16)
            audio_data_sr = sr.AudioData(
                audio_array.tobytes(),
                sample_rate=self.RATE,
                sample_width=self.audio.get_sample_size(self.FORMAT)
            )

            self.logger.debug("Processing audio for wake word detection...")

            try:
                detected_text = self.recognizer.recognize_google(
                    audio_data_sr, 
                    show_all=False
                ).lower().strip()
                
                self.logger.info(f"Detected text: {detected_text}")
                return detected_text == self.WAKE_WORD.lower()
            except sr.UnknownValueError:
                self.logger.debug("Speech recognition could not understand audio")
                return False
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition error: {e}")
                return False
        except Exception as e:
            self.logger.error(f"Wake word detection error: {e}")
            return False

    def start(self):
        """Start the background assistant service"""
        try:
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True, 
                frames_per_buffer=self.CHUNK,
                stream_callback=self.audio_callback,
                start=True
            )
            self.stream_active = True
            self.logger.info("Audio stream started in callback mode")
        except Exception as e:
            self.logger.error(f"Failed to start audio stream: {e}")
            voice_assistant.speak("Failed to start audio stream")
            self.cleanup()
            return

        try:
            threshold_update_time = time.time()
            while self.is_running:
                self.app.processEvents()  
                if time.time() - threshold_update_time > 60:
                    self.update_silence_threshold()
                    threshold_update_time = time.time()

                if self.detect_wake_word():
                    self.logger.info("Wake word detected, showing GUI and listening for command...")
                    self.gui.set_state("wake_detected")
                    self.gui.show()
                    voice_assistant.speak("Hello! How can I help?")
                    self.is_listening = True
                    while True:
                        self.gui.set_state("listening")
                        command = voice.take_speech(self.SILENCE_THRESHOLD)
                        if command:
                            self.logger.info(f"Command received: {command}")
                            self.gui.set_state("processing")
                            result = recognizer.recognize(command)
                            if result['entity'] == 'exit' and result['entity'] == "None":
                                voice_assistant.speak("Enter file name is in wrong format, Please try again.")
                            else:
                                self.process_command(result)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            voice_assistant.speak("An error occurred, shutting down")
        finally:
            self.cleanup()

    def update_silence_threshold(self):
        """Update silence threshold using a temporary stream"""
        try:
            temp_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            ambient_data = []
            for _ in range(int(self.RATE / self.CHUNK * 5)):
                data = temp_stream.read(self.CHUNK, exception_on_overflow=False)
                ambient_data.append(data)
            
            temp_stream.stop_stream()
            temp_stream.close()
            
            self.SILENCE_THRESHOLD = self.calculate_dynamic_threshold(ambient_data)
            self.logger.info(f"Updated SILENCE_THRESHOLD to {self.SILENCE_THRESHOLD}")
        except Exception as e:
            self.logger.error(f"Failed to update silence threshold: {e}")

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.stream and self.stream_active:
                if not self.stream.is_stopped():
                    self.stream.stop_stream()
                if not self.stream.is_closed():
                    self.stream.close()
                self.stream_active = False
                
            if self.audio:
                self.audio.terminate()
                
            self.gui.hide()
            self.gui.close()
            self.app.quit()
            self.logger.info("GUI and audio resources cleaned up")
            voice_assistant.speak("Assistant stopped")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def process_command(self, result):
        """Process the recognized command and update GUI state"""
        try:
            if result['intent'] == "create_file":
                self.gui.set_state("processing")
                executor.create_file(os.path.join(executor.download_dir, result['entity']))
            elif result['intent'] == "create_folder":
                self.gui.set_state("processing")
                executor.create_folder(os.path.join(executor.download_dir, result['entity']))
            elif result['intent'] == "open_application":
                self.gui.set_state("processing")
                executor.open_application('browser')
            elif result['intent'] == "web_search":
                self.gui.set_state("processing")
                executor.web_search(result['entity'])
            elif result['intent'] == "download_file":
                self.gui.set_state("processing")
                executor.download_file(result['entity'])
            elif result['intent'] == "system_command":
                self.gui.set_state("processing")
                executor.system_command(result['entity'])
            elif result['intent'] == "exit":
                self.cleanup()
                executor.exit_program()
                self.is_listening = False
                self.is_running = False
            else:
                self.gui.set_state("speaking")
                voice_assistant.speak("I think you entered a wrong command")
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            self.gui.set_state("speaking")
            voice_assistant.speak("An error occurred while processing the command")
            self.gui.set_state("idle")
            self.gui.hide()
            self.is_listening = False

cypher = CypherAi()