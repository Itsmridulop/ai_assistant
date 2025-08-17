import os
import logging
import time
import speech_recognition as sr
from modules.guiControll.web_agent import web_agent
from modules.guiControll.app_agent import app_agent
from modules.shellControll.shell_agent import shell_agent
from modules.shellControll.key_agent import keyboard_agent
from modules.guiControll.gui_team import gui_team
from modules.shellControll.shell_team import shell_team
from output import voice_assistant
from dotenv import load_dotenv
from agno.playground import Playground
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.team import Team
from agno.models.google import Gemini

load_dotenv()
logging.basicConfig(level=logging.INFO)

memory_db = SqliteMemoryDb(
    table_name="team_memories", 
    db_file="memory/team_memory.db"
)
memory = Memory(db=memory_db)

api_key = os.getenv("GOOGLE_API_KEY")

Cypher = Team(
    name="Cypher",
    team_id='Cypher_team',
    model=Gemini(id="gemini-2.0-flash", temperature=0, api_key=api_key),
    description="You are Cypher agent controller that routes tasks to appropriate specialized teams. You are created and developed by mridul.",
    instructions=[
        "You are a task router that assigns work to specialized teams based on task requirements",
        "If user is asking for any information first search in your memory for the answer",
        "ROUTING RULES:",
        "- For ANY command-line, terminal, shell, file operations, system commands, keyboard shortcuts, os level operations → use Shell Team",
        "- For GUI automation, desktop apps, window management, visual tasks, web searches → use GUI Team", 
        "ALWAYS prioritize Shell Team for command-line tasks",
        "Only use GUI Team when the task specifically requires visual/desktop interaction",
        "If anyone ask about your creator, developer or anything realed to this just say 'mridul' and be done with it"
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

# playground_app = Playground(agents=[web_agent, app_agent, shell_agent, keyboard_agent], teams=[gui_team, shell_team, Cypher])
# app = playground_app.get_app()

# if __name__ == "__main__":
#     playground_app.serve("main:app", reload=True)

recognizer = sr.Recognizer()
mic = sr.Microphone()

def run_agent(user_input: str) -> str:
    """Send user input to Cypher agent and return final response text."""
    final_content = None
    for chunk in Cypher.run(
        message=user_input,
        stream=True,
        stream_intermediate_steps=True,
        user_id="mridul"
    ):
        if getattr(chunk, "event", None) == "TeamRunCompleted":
            if getattr(chunk, "content", None):
                final_content = chunk.content
    return final_content or "I did not get any response."

def callback(recognizer, audio):
    try:
        user_input = recognizer.recognize_google(audio, language="en-IN").lower()

        if user_input in ["exit", "quit", "q", "stop"]:
            voice_assistant.speak("Byee Byee Have a nice day")
            os._exit(0)

        response = run_agent(user_input)
        voice_assistant.speak(response)
    except sr.UnknownValueError:
        logging.warning("Could not understand audio")
    except sr.RequestError as e:
        logging.error(f"API error: {e}")

if __name__ == "__main__":

    stop_listening = recognizer.listen_in_background(mic, callback)

    try:
        while True: 
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_listening(wait_for_stop=True)
