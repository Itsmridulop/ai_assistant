import os
from dotenv import load_dotenv
from modules.shellControll.shell_agent import shell_agent
from modules.shellControll.key_agent import keyboard_agent
from agno.team import Team
from agno.models.google import Gemini

load_dotenv()

shell_team = Team(
    name="Shell Team",
    model=Gemini(id="gemini-1.5-flash-latest", temperature=0, api_key=os.getenv("GOOGLE_API_KEY")),
    description="Specialized team for executing shell commands and system operations",
    role="Execute shell commands, file operations, system tasks, and terminal-based operations",
    instructions=[
        "You handle all shell commands and terminal operations",
        "You can execute system commands, file management, process control",
        "You work with command-line tools and system administration tasks",
        "You can also use keyboard shortcuts to perform actions",
        "You are also ablle to handle os level operations"
    ],
    mode="route",
    members=[shell_agent, keyboard_agent],
    add_datetime_to_instructions=True,
    enable_agentic_context=True,
    show_members_responses=True
)