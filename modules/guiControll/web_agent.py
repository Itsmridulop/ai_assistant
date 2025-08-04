import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.webbrowser import WebBrowserTools

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

web_agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=api_key),
    name="Web Agent",
    tools=[WebBrowserTools(), DuckDuckGoTools()],
    instructions=[
        "Find related websites and pages using DuckDuckGo",
        "Use web browser to open the site"
    ],
    description="This agent enables intelligent web automation using natural language commands. Powered by Google Gemini, it can search for relevant websites and pages via DuckDuckGo, and open them directly in your web browser. The agent combines search and browsing tools to streamline online tasks, providing clear, actionable responses and immediate feedback. Designed for ease of use, it executes each command efficiently and displays results in Markdown format for enhanced readability.",
    show_tool_calls=True,
    markdown=True,
)
