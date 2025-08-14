import os
from dotenv import load_dotenv
from modules.guiControll.gui_toolkit import GuiTools
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.reasoning import ReasoningTools

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

keyboard_agent = Agent(
        tools=[GuiTools(), ReasoningTools()],
        model =OpenRouter(id="google/gemini-2.5-flash", temperature=0, api_key=openrouter_api_key),
        name="Keyboard Agent",
        description="You are keyboard controll agent. Which can press any keys based on user input.",
        instructions="""
            You have full control over keyboard. You can press any keys based on user input.
            You can also use keyboard shortcuts to perform actions.
            You have to plan best key combinations to perform actions given by user. You can plan multiple key combinations to perform multiple actions like to copy all text and then paste it.
            After planing key combinations, you have to execute them.
        """,
        show_tool_calls=True
    )