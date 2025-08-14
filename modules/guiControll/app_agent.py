import os
import platform
from dotenv import load_dotenv
from agno.agent import Agent
from agno.tools import tool
from agno.models.google import Gemini
from agno.models.openrouter import OpenRouter
from modules.guiControll.gui_toolkit import GuiTools

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
os_type = os.getenv("OS_TYPE", platform.system().lower())
os.environ["OS_TYPE"] = os_type

app_agent = None
try:
    model = OpenRouter(id="google/gemini-2.5-flash", temperature=0.1, api_key=openrouter_api_key)
    
    if model:
        app_agent = Agent(
            model=model,
            name="App Agent",
            tools=[
                GuiTools()
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
