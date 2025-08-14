import os
import platform
from dotenv import load_dotenv
from agno.agent import Agent
from agno.tools.shell import ShellTools
from agno.models.openrouter import OpenRouter

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
os.environ["OS_TYPE"] = platform.system().lower()

shell_agent = Agent(
        tools=[ShellTools()],
        model =OpenRouter(id="google/gemini-2.5-flash", temperature=0, api_key=openrouter_api_key),
        name="Shell Command Agent",
        role="Execute shell commands and system operations",
        description="Specialized agent for terminal and command-line tasks",
        instructions="""
            You have to execute shell commands based on user input and operating system. Take which operating system is used by user with the help of OS_TYPE environment variable.
            On the basis and these input, you have to decide which shell command to execute.
            Then deciding execute shell command and get the output.
            If you need admin and super user previlage ask user to input its password.
        """,
        show_tool_calls=True
    )