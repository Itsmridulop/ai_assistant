import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
import webbrowser
import requests
import platform
import shutil
import time
import re
from pathlib import Path
from urllib.parse import quote
from modules.output import voice_assistant

class TaskExecutor:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.home_dir = str(Path.home())
        self.download_dir = self.get_download_dir()
        
    def get_download_dir(self):
        """Get platform-specific download directory"""
        download_dir = os.path.join(self.home_dir, 'Downloads')
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        return download_dir
    
    def _validate_path(self, path):
        """Validate file or folder path"""
        if not path:
            raise ValueError("Path cannot be empty")
        invalid_chars = r'[<>:"\\|?*\x00-\x1F]'
        if re.search(invalid_chars, path):
            raise ValueError(f"Path contains invalid characters: {path}")
        return True
    
    def create_file(self, filename):
        """Create a new file with optional content"""
        try:
            voice_assistant.speak(f"Creating file")
            self._validate_path(filename)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                f.write(" ")
            voice_assistant.speak(f"file created successfully")
        except (PermissionError, OSError, ValueError) as e:
            voice_assistant.speak("Some Error occured in creating file")
            print(f"{str(e)}")
            exit(1)
    
    def create_folder(self, foldername):
        """Create a new directory"""
        try:
            voice_assistant.speak(f"Creating folder")
            self._validate_path(foldername)
            os.makedirs(foldername, exist_ok=True)
            voice_assistant.speak(f"folder Created successfully")
        except (PermissionError, OSError, ValueError) as e:
            voice_assistant.speak("Some Error occured in creating folder")
            print(f"{str(e)}")
            exit(1)
    
    def open_application(self, app_name):
        """Open applications with cross-platform support"""
        try:
            app_map = {
                'browser': {
                    'windows': ['start', 'chrome'],
                    'darwin': ['open', '-a', 'Google Chrome'],
                    'linux': ['google-chrome']
                },
                'notepad': {
                    'windows': ['notepad'],
                    'darwin': ['open', '-a', 'TextEdit'],
                    'linux': ['gedit']
                },
                'calculator': {
                    'windows': ['calc'],
                    'darwin': ['open', '-a', 'Calculator'],
                    'linux': ['gnome-calculator']
                },
                'terminal': {
                    'windows': ['cmd.exe'],
                    'darwin': ['open', '-a', 'Terminal'],
                    'linux': ['gnome-terminal']
                }
            }
            
            app_key = app_name.lower()
            if app_key in app_map:
                command = app_map[app_key].get(self.os_type)
                if command and shutil.which(command[0]):
                    voice_assistant.speak("Opening chrome")
                    subprocess.Popen(command, start_new_session=True)
                else:
                    voice_assistant.speak("Error {app_name} not found on {self.os_type}")
                    exit(1)
            
            if self.os_type == 'windows':
                if shutil.which(app_name):
                    subprocess.Popen([app_name], start_new_session=True)
                    print(f"Opened {app_name}")
            elif self.os_type == 'darwin':
                if subprocess.run(['mdfind', f'kMDItemKind == "Application" && kMDItemFSName == "{app_name}.app"'], capture_output=True, text=True).returncode == 0:
                    subprocess.Popen(['open', '-a', app_name])
                    print(f"Opened {app_name}")
            else: 
                if shutil.which(app_name):
                    subprocess.Popen([app_name], start_new_session=True)
                    print(f"Opened {app_name}")
            
            voice_assistant.speak(f"Error: Application {app_name} not found")
            exit(1)
        except Exception as e:
            voice_assistant.speak("Error opening application")
            print(f"Error: {str(e)}")
            exit(1)
    
    def web_search(self, query):
        """Perform web search using default browser"""
        try:
            if not query.strip():
                voice_assistant.speak("Search query cannot be empty")
                exit(1)
            search_url = f"https://www.google.com/search?q={quote(query)}"
            webbrowser.open(search_url)
            voice_assistant.speak(f"Searching for: {query}")
        except Exception as e:
            voice_assistant.speak("Error performing web search")
            print(f"{str(e)}")
            exit(1)
    
    def download_file(self, url, filename=None):
        """Download file from URL"""
        try:
            if not url:
                return "Error: URL cannot be empty"
            if not filename:
                filename = os.path.basename(url) or "downloaded_file"
            
            self._validate_path(filename)
            download_path = os.path.join(self.download_dir, filename)
            
            if os.path.exists(download_path):
                return f"Error: File {download_path} already exists"
            
            with requests.get(url, stream=True, timeout=10) as r:
                r.raise_for_status()
                with open(download_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            return f"Downloaded file to: {download_path}"
        except (requests.RequestException, ValueError, OSError) as e:
            return f"Error downloading file: {str(e)}"
    
    def system_command(self, command):
        """Execute system commands with cross-platform support"""
        try:
            cmd_map = {
                'shutdown': {
                    "msz": 'shutingdown',
                    'windows': ['shutdown', '/s', '/t', '0'],
                    'darwin': ['osascript', '-e', 'tell app "System sausystem to shut down'],
                    'linux': ['shutdown', 'now']
                },
                'restart': {
                    "msz": 'restarting',
                    'windows': ['shutdown', '/r', '/t', '0'],
                    'darwin': ['osascript', '-e', 'tell app "System Events" to restart'],
                    'linux': ['reboot']
                },
                'sleep': {
                    "msz": 'sleeping',
                    'windows': ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'],
                    'darwin': ['pmset', 'sleepnow'],
                    'linux': ['systemctl', 'suspend']
                },
                'increase volume': {
                    'msz': 'increasing volume',
                    'windows': None,
                    'darwin': ['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) + 10)'],
                    'linux': ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+10%']
                },
                'decrease volume': {
                    'msz': 'decreasing volume',
                    'windows': None,
                    'darwin': ['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) - 10)'],
                    'linux': ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-10%']
                }
            }
            
            cmd_key = command.lower()
            if cmd_key in cmd_map:
                cmd = cmd_map[cmd_key].get(self.os_type)
                if cmd and shutil.which(cmd[0]):
                    try:
                        voice_assistant.speak(f"{cmd_map[cmd_key].get('msz')}")
                        subprocess.run(cmd, check=True, capture_output=True, text=True)
                        print(f"Executed: {command}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error: Command {command} failed, may require elevated privileges: {str(e)}")
                        exit(1)
                else:
                    print(f"Error: Command {command} not supported or dependency missing on {self.os_type}")
                    exit(1)
            
            try:
                cmd_args = command.split()
                if not cmd_args:
                    print("Error: Command cannot be empty")
                    exit(1)
                if shutil.which(cmd_args[0]):
                    result = subprocess.run(cmd_args, capture_output=True, text=True)
                    voice_assistant.speak("Command executed.")
                    print(f"Output: {result.stdout[:100]}")
                voice_assistant.speak(f"Error: Command {cmd_args[0]} not found")
                exit(1)
            except Exception as e:
                voice_assistant.speak("Error executing command")
                print(f'{str(e)}')
                exit(1)
        except Exception as e:
            voice_assistant.speak("Error executing system command")
            print(f"Error: {str(e)}")
            exit(1)
    
    def exit_program(self):
        """Clean exit from the program"""
        try:
            voice_assistant.speak("Exiting")
            time.sleep(1)  
            sys.exit(0)
        except Exception as e:
            voice_assistant.speak("Error during exit")
            print(f"Error: {str(e)}")
            sys.exit(1)

executor = TaskExecutor()