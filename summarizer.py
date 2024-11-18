import sys
sys.path.append("")

import requests
from datetime import datetime
from load import load_conversation_history # type: ignore
from save import save_summary_to_file, save_message_counter # type: ignore
from config import ENDPOINT, MESSAGE_INTERVAL, HISTORY_LIMIT # type: ignore
# Function to get the current date and time
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def summarize_history(history_text, randomless = 0):
    if randomless == 0:
        print("randomless==0")
        summary_prompt = f"Can you provide a comprehensive summary about 10000 symbols long of the given chat? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information. Be more focused on relations dynamics between characters. Provide your text with emotions and style from the dialog, be focused on how things said. Dont say that conversation ended, because it is still ongoing conversation:\n\n{history_text}\n\nSummary:"
        
        # Call KoboldCpp API to get summary
        response = requests.post(f"{ENDPOINT}/api/v1/generate", json={
            "prompt": summary_prompt,
            "max_length": 4000,  # Limit the summary length as needed
            "use_story": False,
            "use_memory": True,
            "use_authors_note": False,
            "use_world_info": False,
            "max_context_length": 32768,
            "rep_pen": 1.2,
            "rep_pen_range": 128,
            "rep_pen_slope": 0.7,
            "temperature": 0.8,
            "tfs": 0.97,
            "top_a": 0.8,
            "top_k": 0,
            "top_p": 0.5,
            "typical": 0.19,
            "sampler_order": [6, 0, 1, 3, 4, 2, 5],
            "singleline": False,
            "frmttriminc": False,
            "frmtrmblln": False,
            "stop_sequence": ["[END]", "<|endoftext|>"]
        })
        
        if response.status_code == 200:
            summary_text = response.json()['results'][0]['text'].strip()
            return summary_text
        else:
            print("Error: Could not retrieve summary from the model.")
            return None
    
    if randomless == 1:
        print("randomless==1")
        summary_prompt = f"Provide a comprehensive summary 10000 symbols long of the given chat histoy. The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. Be more focused on relations dynamics between characters.  Provide your text with emotions and style from the dialog, be focused on how things said. Dont say that conversation ended, because it is still ongoing conversation:\n\n{history_text}\n\nSummary:"
        
        # Call KoboldCpp API to get summary
        response = requests.post(f"{ENDPOINT}/api/v1/generate", json={
            "prompt": summary_prompt,
            "max_length": 4000,  # Limit the summary length as needed
            "use_story": False,
            "use_memory": True,
            "use_authors_note": False,
            "use_world_info": False,
            "max_context_length": 32768,
            "rep_pen": 1.02,
            "rep_pen_range": 512,
            "rep_pen_slope": 0.9,
            "temperature": 0.2,
            "tfs": 0.97,
            "top_a": 0.8,
            "top_k": 0,
            "top_p": 0.5,
            "typical": 0.19,
            "sampler_order": [6, 0, 1, 3, 4, 2, 5],
            "singleline": False,
            "frmttriminc": False,
            "frmtrmblln": False,
            "stop_sequence": ["<|endoftext|>"]
        })
        
        if response.status_code == 200:
            summary_text = response.json()['results'][0]['text'].strip()
            return summary_text
        else:
            print("Error: Could not retrieve summary from the model.")
            return None
        
# Function to summarize the conversation history if it exceeds the limit
def pre_summarize_history(conversation_history, message_counter):
    # Check if the interval is reached for summarization
    if message_counter >= MESSAGE_INTERVAL:
        # Only summarize if the history exceeds the character limit
        conversation_history = load_conversation_history()
        if should_summarize(conversation_history):
            old_history = conversation_history[:-HISTORY_LIMIT]
            recent_history = conversation_history[-HISTORY_LIMIT:]
            summary = summarize_history(old_history)
            if len(str(summary)) < 2000 :
                    summary_second_try = summarize_history(old_history, randomless=1)
                    if len(summary_second_try) > len(summary):
                        summary = summary_second_try

        if summary:
            conversation_history = f"{summary}\n\n{recent_history}"
            save_summary_to_file(summary)
            reset_message_counter(message_counter)
    return conversation_history

def should_summarize(conversation_history):
    if len(conversation_history) > HISTORY_LIMIT:
        return True
    return False

def reset_message_counter(message_counter):
    message_counter = 0
    save_message_counter(message_counter)  # Reset the counter in the file

    

