import os
import platform
import pyautogui
import logging
import time
from dotenv import load_dotenv
from agno.agent import Agent
from agno.tools import tool
from agno.models.google import Gemini
from agno.models.openrouter import OpenRouter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  

api_key = os.getenv("GOOGLE_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
os_type = os.getenv("OS_TYPE", platform.system().lower())
os.environ["OS_TYPE"] = os_type

@tool(show_result=True)
def press_key_combination(target: str) -> str:
    """Presses a key combination using PyAutoGUI's hotkey function
    
    Args:
        target (str): The key combination to press, e.g., 'alt + f2', 'alt + f4'
    
    Returns:
        str: A string describing the key combination that was pressed
    """
    try:
        keys = [key.strip() for key in target.replace(" ", "").split("+")]
        pyautogui.hotkey(*keys)
        time.sleep(0.5)
        logger.info(f"Pressed key combination: {target}")
        return f"Pressed: {target} "
    except Exception as e:
        logger.error(f"Error in press_key_combination: {str(e)}")
        return f"Error pressing {target}: {str(e)}"

@tool(show_result=True)
def execute_type(target: str) -> str:
    """Type specified text
    
    Args:
        target (str): The text to type
    
    Returns:
        str: A string describing the text that was typed
    """
    try:
        pyautogui.typewrite(target)
        time.sleep(0.3) 
        logger.info(f"Typed text: {target}")
        return f"Typed: {target} "
    except Exception as e:
        logger.error(f"Error in execute_type: {str(e)}")
        return f"Error typing {target}: {str(e)}"

app_agent = None
try:
    if api_key:
        model = Gemini(id="gemini-2.0-flash-exp", api_key=api_key, temperature=0.1)
        print("🎆 Using Google Gemini API")
    elif openrouter_api_key:
        model = OpenRouter(id="google/gemini-2.5-flash", temperature=0.1, api_key=openrouter_api_key)
        print("🎆 Using OpenRouter API")
    else:
        print("⚠️  No API key found - will use simple command mode")
        model = None
    
    if model:
        app_agent = Agent(
            model=model,
            name="app_agent",
            tools=[
                press_key_combination,
                execute_type,
            ],
            instructions=f"""
You are a GUI automation agent for {os_type} operating system. 

IMPORTANT RULES:
- Execute each command EXACTLY ONCE
- Do NOT repeat or retry actions
- Complete the task and provide a brief confirmation
- Do NOT get stuck in thinking loops

For opening applications:
1. Press 'alt + f2' to open run dialog
2. Type the application name (use 'google-chrome' for chrome)
3. Press 'enter'
4. Done - provide confirmation

For closing applications:
1. Press 'alt + f4' to close current application
2. Done - provide confirmation

Execute the steps in sequence, then STOP.
""",
            description="GUI automation agent for opening and closing applications.",
            show_tool_calls=True,
            markdown=True
        )
except Exception as e:
    print(f"⚠️  Could not initialize AI agent: {str(e)}")
    print("Will use simple command mode instead")
    app_agent = None


def simple_command_handler(user_input):
    """Simple command handler without AI when API is not available"""
    user_input = user_input.lower().strip()
    
    if "open" in user_input and "chrome" in user_input:
        print("Opening Chrome...")
        press_key_combination("alt + f2")
        time.sleep(0.5)
        execute_type("google-chrome")
        time.sleep(0.3)
        press_key_combination("enter")
        return "Chrome opened successfully"
    
    elif "close" in user_input:
        print("Closing application...")
        press_key_combination("alt + f4")
        return "Application closed"
    
    else:
        return "Command not recognized. Try: 'open chrome' or 'close app'"