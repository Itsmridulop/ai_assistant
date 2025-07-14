import os
import sys
import subprocess
import webbrowser
import requests
import platform
import shutil
import time
from pathlib import Path
from urllib.parse import quote
import re

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
            self._validate_path(filename)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                f.write(" ")
            print(f"Created file: {filename}")
            exit(0)
        except (PermissionError, OSError, ValueError) as e:
            print(f"Error creating file: {str(e)}")
            exit(1)
    
    def create_folder(self, foldername):
        """Create a new directory"""
        try:
            self._validate_path(foldername)
            os.makedirs(foldername, exist_ok=True)
            print(f"Created folder: {foldername}")
        except (PermissionError, OSError, ValueError) as e:
            print(f"Error creating folder: {str(e)}")
    
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
                    subprocess.Popen(command, start_new_session=True)
                    print(f"Opened {app_name}")
                    exit(0)
                print(f"Error: {app_name} not found on {self.os_type}")
                exit(1)
            
            if self.os_type == 'windows':
                if shutil.which(app_name):
                    subprocess.Popen([app_name], start_new_session=True)
                    print(f"Opened {app_name}")
                    exit(0)
            elif self.os_type == 'darwin':
                if subprocess.run(['mdfind', f'kMDItemKind == "Application" && kMDItemFSName == "{app_name}.app"'], capture_output=True, text=True).returncode == 0:
                    subprocess.Popen(['open', '-a', app_name])
                    print(f"Opened {app_name}")
                    exit(0)
            else: 
                if shutil.which(app_name):
                    subprocess.Popen([app_name], start_new_session=True)
                    print(f"Opened {app_name}")
                    exit(0)
            
            print(f"Error: Application {app_name} not found")
            exit(1)
        except Exception as e:
            print(f"Error opening application: {str(e)}")
            exit(1)
    
    def web_search(self, query):
        """Perform web search using default browser"""
        try:
            if not query.strip():
                print("Error: Search query cannot be empty")
                exit(1)
            search_url = f"https://www.google.com/search?q={quote(query)}"
            webbrowser.open(search_url)
            print(f"Searching for: {query}")
            exit(0)
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
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
                    'windows': ['shutdown', '/s', '/t', '0'],
                    'darwin': ['osascript', '-e', 'tell app "System sausystem to shut down'],
                    'linux': ['sudo', 'shutdown', 'now']
                },
                'restart': {
                    'windows': ['shutdown', '/r', '/t', '0'],
                    'darwin': ['osascript', '-e', 'tell app "System Events" to restart'],
                    'linux': ['sudo', 'reboot']
                },
                'sleep': {
                    'windows': ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'],
                    'darwin': ['pmset', 'sleepnow'],
                    'linux': ['systemctl', 'suspend']
                },
                'increase volume': {
                    'windows': None,
                    'darwin': ['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) + 10)'],
                    'linux': ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+10%']
                },
                'decrease volume': {
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
                        subprocess.run(cmd, check=True, capture_output=True, text=True)
                        print(f"Executed: {command}")
                        exit(0)
                    except subprocess.CalledProcessError as e:
                        print(f"Error: Command {command} failed, may require elevated privileges: {str(e)}")
                        exit(1)
                print(f"Error: Command {command} not supported or dependency missing on {self.os_type}")
                exit(1)
            
            try:
                cmd_args = command.split()
                if not cmd_args:
                    print("Error: Command cannot be empty")
                    exit(1)
                if shutil.which(cmd_args[0]):
                    result = subprocess.run(cmd_args, capture_output=True, text=True)
                    print(f"Command executed. Output: {result.stdout[:100]}")
                    exit(0)
                print(f"Error: Command {cmd_args[0]} not found")
                exit(1)
            except Exception as e:
                print(f"Error executing command: {str(e)}")
                exit(1)
        except Exception as e:
            print(f"Error executing system command: {str(e)}")
            exit(1)
    
    def exit_program(self):
        """Clean exit from the program"""
        try:
            print("Exiting the program...")
            time.sleep(1)  
            sys.exit(0)
        except Exception as e:
            print(f"Error during exit: {str(e)}")
            sys.exit(1)