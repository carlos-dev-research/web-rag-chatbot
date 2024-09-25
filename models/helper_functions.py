import uuid
from time import time
import os
import json

# Create chat history for new session
def create_sessionId():
    session_id = str(uuid.uuid4())
    if not os.path.exists('chat_history'):
        os.mkdir('chat_history')
    if not os.path.exists('uploaded_audios'):
        os.mkdir('uploaded_audios')
    with open(f'chat_history/{session_id}.txt','w') as f:
        f.write('[]')
    return session_id


# Get chat_history from session ID
def get_chat_history(session_id):
    with open(f'chat_history/{session_id}.txt','r') as f:
        chat_history = json.load(f)
    return chat_history

# Save chat history
def save_chat_history(session_id,chat_history):
    with open(f'chat_history/{session_id}.txt','w') as f:
            json.dump(chat_history,f,indent=4)

# Helper functions
def delete_old_sessions(directory):
    # Get the current time
    now = time()
    # Define the age threshold (24 hours)
    age_threshold = 24 * 60 * 60
    
    # Loop through all files in the specified directory
    for filename in os.listdir(directory):
        # Construct the file path
        file_path = os.path.join(directory, filename)
        
        # Check if the file is a text file
        if file_path.endswith('.txt'):
            # Get the last modified time of the file
            last_modified_time = os.path.getmtime(file_path)
            
            # Check if the file is older than the threshold
            if now - last_modified_time > age_threshold:
                # Delete the file
                os.remove(file_path)
                print(f"Deleted {filename} because it was older than 24 hours.")