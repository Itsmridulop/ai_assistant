import pyautogui
import logging
import time
from typing import Any, List
from agno.tools import Toolkit

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  

class GuiTools(Toolkit):
    def __init__(self):
        self.tools: List[Any] = [self.press_key_combination, self.execute_type]
        super().__init__(name="gui_tools", tools=self.tools)

    def press_key_combination(self, target: str) -> str:
        """Presses a key combination using PyAutoGUI's hotkey function."""
        try:
            keys = [key.strip() for key in target.split('+')]
            pyautogui.hotkey(*keys)
            time.sleep(0.5)
            logger.info(f"Pressed key combination: {target}")
            return f"Pressed: {target}"
        except Exception as e:
            logger.error(f"Error in press_key_combination: {e}")
            return f"Error pressing {target}: {e}"

    def execute_type(self, target: str) -> str:
        """Type specified text."""
        try:
            pyautogui.typewrite(target)
            time.sleep(0.3)
            logger.info(f"Typed text: {target}")
            return f"Typed: {target}"
        except Exception as e:
            logger.error(f"Error in execute_type: {e}")
            return f"Error typing {target}: {e}"
