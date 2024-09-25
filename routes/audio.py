from flask import Blueprint, request, jsonify, Response,stream_with_context,current_app
from werkzeug.utils import secure_filename
from models import *
import time
import uuid
import os


audio_bp = Blueprint('audio',__name__)

# Upload Audio Endpoint
@audio_bp.route('/upload-audio', methods=['POST'])
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
        if not session.verify_token(current_app.mydb, user, token):
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
        transcription = current_app.slm.audio_model.get_transcript(file_path)
        
        # 9. Delete the file after processing
        os.remove(file_path)

        return jsonify({'transcription': transcription})
    
    except Exception:
        # Ensure the file is deleted if an error occurs during processing
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': 'Failed to process audio'}), 500

