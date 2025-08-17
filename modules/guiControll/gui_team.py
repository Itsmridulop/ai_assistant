import os
from dotenv import load_dotenv
from modules.guiControll.web_agent import web_agent
from modules.guiControll.app_agent import app_agent
from agno.models.google import Gemini
from agno.team import Team

load_dotenv()

gui_team = Team(
    name="GUI Team",
    model=Gemini(id="gemini-2.5-flash-lite", temperature=0, api_key=os.getenv("GOOGLE_API_KEY")),
    description="Specialized team for GUI automation and visual interface interactions",
    instructions=[
        "You handle all GUI-related tasks and visual interface interactions",
        "You can automate desktop applications, manage windows, click buttons",
        "You work with visual elements and desktop automation",
        "You can search for any information which is available on the web",
    ],
    mode="route",
    members=[web_agent, app_agent],
    add_datetime_to_instructions=True,
    enable_agentic_context=True,
    show_members_responses=True
)