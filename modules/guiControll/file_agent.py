import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from agno.agent import Agent
from agno.tools.file import FileTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.google import Gemini

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") 

try:
    file_agent = Agent(
        model=Gemini(id="gemini-2.5-flash-lite", temperature=0, api_key=api_key), 
        name="File Agent",
        tools=[
            FileTools(
                base_dir=Path(os.getcwd()),
                save_files=True,
                read_files=True, 
                list_files=True, 
                search_files=True
            ),
            DuckDuckGoTools()
        ],
        instructions=[
            "You are a file management agent.",
            "You can read, write, list, and search files and folders in the current working directory.",
            "Always confirm the action performed and provide a brief summary.",
            "For file searches, use DuckDuckGo if needed to find relevant information.",
            "Do not repeat or retry actions; execute each command only once.",
            "Display results in Markdown format for clarity."
        ],
        description="This agent automates file management tasks using natural language commands. Powered by Google Gemini, it can read, write, list, and search files and folders in the current directory. The agent combines file tools and DuckDuckGo search to assist with file operations and information retrieval, providing clear feedback and results in Markdown format for easy readability.",
        show_tool_calls=True,
        markdown=True
    )
except Exception as e:
    print(f"Error running agent: {e}")
