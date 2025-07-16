import os
from modules.background_service import cypher

try:
    if hasattr(os, 'nice'):
        os.nice(10)
    cypher.start()
except Exception as e:
    print(f"Error starting background service: {e}")