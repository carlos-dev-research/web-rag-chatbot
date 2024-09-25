from models import *
from flask import Flask, render_template, jsonify, request, Response,stream_with_context, send_from_directory, url_for,redirect
from werkzeug.utils import secure_filename
import json
import uuid
import os
import time
from datetime import datetime

# Load models
slm = SLM(model_name='llama3.1')

# Create Web App
app = Flask(__name__)

with open('config.json','r') as f:
    config = json.load(f)
    mydb = db(config)



# Main Endpoint
@app.route('/')
def index():
    return redirect(url_for('send_static',path='main.html'))

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Upload Audio Endpoint
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    """
    Endpoint to transcribe user audio and save it temporarily in user-specific folders.
    Applies token verification, file cleanup, and error handling.
    """

    # 1. Extract request arguments
    user = request.form.get('user')
    token = request.form.get('token')

    # 2. Check for bad input
    if user is None or token is None:
        return jsonify({'error': 'Bad input arguments'}), 400

    # 3. Verify the token
    try:
        if not session.verify_token(mydb, user, token):
            return jsonify({'error': 'Unauthorized access, invalid token'}), 401
    except Exception:
        return jsonify({'error': 'Token verification failed'}), 500

    # 4. Get Audio from the request
    if 'audioFile' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['audioFile']

    # 5. Create user-specific folder in uploaded_audios/
    user_folder = os.path.join('uploaded_audios', secure_filename(user))
    os.makedirs(user_folder, exist_ok=True)

    # 6. Clean up files older than 1 hour
    now = time.time()
    for f in os.listdir(user_folder):
        file_path = os.path.join(user_folder, f)
        if os.path.isfile(file_path):
            file_creation_time = os.path.getctime(file_path)
            if now - file_creation_time > 3600:  # Older than 1 hour
                os.remove(file_path)

    # 7. Generate unique filename and save the file
    unique_filename = f"{uuid.uuid4()}.wav"
    file_path = os.path.join(user_folder, unique_filename)
    file.save(file_path)

    try:
        # 8. Process the audio (e.g., transcribe it)
        transcription = slm.audio_model.get_transcript(file_path)
        
        # 9. Delete the file after processing
        os.remove(file_path)

        return jsonify({'transcription': transcription})
    
    except Exception:
        # Ensure the file is deleted if an error occurs during processing
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': 'Failed to process audio'}), 500


@app.route('/get-auth',methods=['GET'])
def get_auth():
    """
    Endpoint to get authorization token to interact with user data
    """
    user = request.args.get('user')
    password = request.args.get('password')
    token_duration = 3

    # Check for bad input
    if user is None or password is None:
        return jsonify({'error':'Bad input arguments'}),400
    
    # Create new token
    try:
        print(user)
        print(password)
        token = session.create_token(mydb, user, password, token_duration)
    except:
        return jsonify({'error': 'Unable to get authorization'}), 401
    
    return jsonify({'token':token})

@app.route('/register',methods=['GET'])
def register():
    """
    Endpoint to get authorization token to interact with user data
    """
    user = request.args.get('user')
    password = request.args.get('password')
    token_duration = 3

    # Check for bad input
    if user is None or password is None:
        return jsonify({'error':'Bad input arguments'}),400
    
    # Create new token
    try:
        session.create_user(mydb, user, password)
        token = session.create_token(mydb, user, password, token_duration)
    except:
        return jsonify({'error': 'Unable to Create User'}), 401
    
    return jsonify({'token':token})

@app.route('/get-chat-history', methods=['GET'])
def get_chat_history():
    """
    Endpoint to get chat_history to be displayed in the user interface
    """
    # Extract request arguments
    user = request.args.get('user')
    token = request.args.get('token')

    # Check for bad input
    if user is None or token is None:
        return jsonify({'error':'Bad input arguments'}),400
    
    # Create session
    try:
        ss = session(mydb,user,token)
    except:
        return jsonify({'error': 'Unable to get authorization'}), 401
    
    try:
        chat_history = ss.read_chat_history()

    except:
        return jsonify({'error':'Internal server error'}),500

    return jsonify({'chat_history':chat_history})

@app.route('/get-conversation', methods=['GET'])
def get_conversation():
    """
    Endpoint to retrieve Conversation using conversation_id
    """
    # Extract arguments
    user = request.args.get('user')
    token = request.args.get('token')
    conversation_id = request.args.get('conversation_id')

    # Check for bad input
    if user is None or token is None or conversation_id is None:
        return jsonify({'error': 'Bad input arguments'}), 400
    
    # Create session instance
    try:
        ss = session(mydb,user,token)
    except:
        return jsonify({'error': 'Unable to get authorization'}), 401
    
    try:
        conversation = ss.read_conversation(conversation_id)
    except:
        return jsonify({'error':'Internal server error'}),500

    return jsonify({'conversation_id':conversation_id, 'conversation':conversation})

@app.route('/delete-conversation', methods=['DELETE'])
def delete_conversation():
    """
    Endpoint to delete Conversation using conversation_id
    """
    # Extract arguments
    user = request.args.get('user')
    token = request.args.get('token')
    conversation_id = request.args.get('conversation_id')

    # Check for missing input
    if user is None or token is None or conversation_id is None:
        return jsonify({'error': 'Bad input arguments'}), 400

    # Create session instance for authorization
    try:
        ss = session(mydb, user, token)  # Assuming session handles authorization
    except:
        return jsonify({'error': 'Unable to get authorization'}), 401

    # Delete the conversation
    try:
        ss.delete_conversation(conversation_id)  # Assuming ss has delete_conversation method
    except:
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'message': f'Conversation deleted successfully'}), 200


@app.route('/stream-send', methods=['GET'])
def stream_send():
    """
    Endpoint to talk to the LM on Stream
    """
    # Extract arguments
    user = request.args.get('user')
    token = request.args.get('token')
    conversation_id = request.args.get('conversation_id')
    message = request.args.get('message')
    
    # Check for bad input
    if user is None or token is None or message is None:
        return jsonify({'error': 'Bad input arguments', 'status':400}), 400
    
    # Create session instance
    try:
        ss = session(mydb,user,token)
    except:
        return jsonify({'error': 'Unable to get authorization','status':401}), 401
    
    # Handle conversation creation or updating
    try:
        if conversation_id is None:
            conversation = [{'role': 'user', 'content': message}]
            print(conversation)
            title = slm.create_title(message)
            print(title)
            conversation_id = ss.create_conversation(title,conversation)
            print(conversation_id)
        else:
            conversation = ss.read_conversation(conversation_id)
            conversation.append({'role': 'user', 'content': message})
            ss.update_conversation(conversation_id,conversation)
    except:
        return jsonify({'error':'Internal server error', 'status':500}),500


    # Streaming response
    def generate():
        # Send the conversation_id as an event for the stream
        yield f"event: conversation_id\ndata: {conversation_id}\n\n"

        try:
            # Call Ollama with streaming enabled and stream chat response
            stream = slm.chat(chat_history=conversation, data_folder=os.path.join(os.getcwd(),'data'), is_stream=True)
            out=""
            for chunk in stream.response_gen:
                out+= chunk
                data = json.dumps({"response": chunk, "endOfMessage": False})
                yield f"event: chat\ndata: {data}\n\n"   
            
            # Add response from the model to conversation and save it
            conversation.append({'role': 'assistant', 'content': out})
            ss.update_conversation(conversation_id,conversation)

            # Send last message
            end_message = json.dumps({"endOfMessage": True})
            yield f"event: chat\ndata: {end_message}\n\n"
        
        except Exception as e:
            error = json.dumps({'error':'Internal server error', 'status':500})
            yield f"event: error\ndata: {error}\n\n"
            return # Close conection
        
    return Response(stream_with_context(generate()), content_type='text/event-stream')

@app.route('/logout', methods=['DELETE'])
def logout():
    """
    Endpoint to logout the user by deleting the token
    """
    # Extract arguments
    user = request.args.get('user')
    token = request.args.get('token')

    # Check for bad input
    if user is None or token is None:
        return jsonify({'error': 'Bad input arguments'}), 400

    # Create session instance for authorization
    try:
        ss = session(mydb, user, token)
    except:
        return jsonify({'error': 'Unable to get authorization'}), 401

    # Delete the token (logging out the user)
    try:
        ss.delete_token()  # This should handle token deletion
    except:
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'message': 'Logout successful'}), 200

@app.route('/delete-user', methods=['DELETE'])
def delete_user():
    """
    Endpoint to delete the user by verifying password and token
    """
    # Extract arguments
    user = request.args.get('user')
    token = request.args.get('token')
    password = request.args.get('password')

    # Check for bad input
    if user is None or token is None or password is None:
        return jsonify({'error': 'Bad input arguments'}), 400

    # Create session instance for authorization
    try:
        ss = session(mydb, user, token)
    except:
        return jsonify({'error': 'Unable to get authorization'}), 401

    # Delete the user after verifying password and token
    try:
        ss.delete_user(password, token)
    except:
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'message': 'User deleted successfully'}), 200


# Start the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)  # Enable debug mode for development purposes