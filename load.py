import sys
sys.path.append("")

from datetime import datetime
from config import CONVERSATION_FILE # type: ignore

# Utility functions for file handling
def load_from_file(filename, default=None):
    """Load content from a file, returning a default if not found."""
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return default
    
# Initialize conversation history from file
def load_conversation_history():
    try:
        with open(CONVERSATION_FILE, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""  # Start with an empty history if file doesn't exist