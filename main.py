import os
import logging
from modules.guiControll.web_agent import web_agent
from modules.guiControll.app_agent import app_agent
from modules.shellControll.shell_agent import shell_agent
from modules.shellControll.key_agent import keyboard_agent
from modules.guiControll.gui_team import gui_team
from modules.shellControll.shell_team import shell_team
from output import voice_assistant
from dotenv import load_dotenv
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.team import Team
from agno.playground import Playground
from agno.models.google import Gemini

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

memory_db = SqliteMemoryDb(
    table_name="team_memories", 
    db_file="memory/team_memory.db"
)
memory = Memory(db=memory_db)

api_key = os.getenv("GOOGLE_API_KEY")

controller = Team(
    name="Cypher",
    team_id='Cypher_team',
    model=Gemini(id="gemini-2.0-flash", temperature=0, api_key=api_key),
    description="You are Cypher agent controller that routes tasks to appropriate specialized teams. You are create and Developed by Mridul.",
    instructions=[
        "You are a task router that assigns work to specialized teams based on task requirements",
        "ROUTING RULES:",
        "- For ANY command-line, terminal, shell, file operations, system commands, keyboard shortcuts, os level operations → use Shell Team",
        "- For GUI automation, desktop apps, window management, visual tasks, web searches → use GUI Team", 
        "- Shell Team handles: bash commands, file operations, process management, system tasks and keyboard shortcuts",
        "- GUI Team handles: desktop automation, clicking, window management, visual interfaces, web searches and web automation",
        "ALWAYS prioritize Shell Team for command-line tasks",
        "Only use GUI Team when the task specifically requires visual/desktop interaction",
        "Analyze the task carefully before routing to ensure correct team assignment",
        "If anyone ask you about your developer, creator or anything just like this you have to just say Mridul",
    ],
    members=[shell_team, gui_team],
    mode="route",
    memory=memory,
    enable_user_memories=True,
    add_history_to_messages=True,
    num_history_runs=3,
    enable_session_summaries=True,
    add_datetime_to_instructions=True,
    show_members_responses=True,
)

# playground_app = Playground(agents=[web_agent, app_agent, shell_agent, keyboard_agent], teams=[gui_team, shell_team, controller])
# app = playground_app.get_app()

# if __name__ == "__main__":
#     playground_app.serve("main:app", reload=True)

def main():
    final_content = None
    for chunk in controller.run(
        message=user_input,
        stream=True,
        stream_intermediate_steps=True,
        user_id='mridul'
    ):
        if hasattr(chunk, "event") and chunk.event == "TeamRunCompleted":
            if getattr(chunk, "content", None):
                final_content = chunk.content
    return final_content

if __name__ == "__main__":
    while True:
        user_input = input("You: ")    
        if user_input in ["exit", "quit", "q"]:
            break
        voice_assistant.speak(main())