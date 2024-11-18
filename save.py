import sys
sys.path.append("")

from datetime import datetime
from config import MESSAGE_COUNTER_FILE, SUMMARY_FILE, CONVERSATION_FILE, USERNAME, BOTNAME # type: ignore

def save_to_file(filename, content):
    """Save content to a file."""
    with open(filename, 'w') as file:
        file.write(str(content))

# Save the message counter to file
def save_message_counter(counter):
    with open(MESSAGE_COUNTER_FILE, "w") as file:
        file.write(str(counter))

# Function to save summaries to a file
def save_summary_to_file(summary):
    timestamp = get_current_time()
    with open(SUMMARY_FILE, "w") as file:
        file.write(f"[{timestamp}] Summary:\n{summary}\n\n")

# Save updated conversation history to file with timestamps
def save_conversation_history(user_message, bot_response):
    timestamp = get_current_time()
    with open(CONVERSATION_FILE, "a") as file:
        file.write(f"[{timestamp}] {USERNAME}: {user_message}\n")
        file.write(f"[{timestamp}] {BOTNAME}: {bot_response}\n")

# Function to get the current date and time
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")