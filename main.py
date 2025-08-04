import os
import asyncio
from modules.guiControll.web_agent import web_agent
from modules.guiControll.file_agent import file_agent
from modules.guiControll.app_agent import app_agent
from dotenv import load_dotenv
from agno.team import Team
from agno.playground import Playground
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini

load_dotenv()

memory_db = SqliteMemoryDb(table_name="memory", db_file="memory/memory.db")
memory = Memory(db=memory_db)

gui_team = Team(
    name="GUI Team",
    model=Gemini(id="gemini-2.5-flash-lite", temperature=0, api_key=os.getenv("GOOGLE_API_KEY")),
    description="This team manages GUI-related agents for file management, web browsing, and application control.",
    mode="route",
    members=[web_agent, file_agent, app_agent],
    add_datetime_to_instructions=True,
    enable_agentic_context=True,
    memory=memory,
    enable_agentic_memory=True,
    add_memory_references=True,
    enable_session_summaries=True,
    show_members_responses=True
)

playground_app = Playground(agents=[web_agent, file_agent, app_agent], teams=[gui_team])
app = playground_app.get_app()

if __name__ == "__main__":
    playground_app.serve("main:app", reload=True)

# if __name__ == "__main__":
#     asyncio.run(    
#         gui_team.aprint_response(
#             message="Hello! I am your GUI assistant. How can I help you today?",
#             stream=True,
#             stream_intermediate_steps=True
#         )
#     )