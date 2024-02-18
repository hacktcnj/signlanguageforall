import uuid
import os
import json
from flask import Flask, request, jsonify, render_template, redirect, session, url_for

from werkzeug.utils import secure_filename
import speech_recognition as sr
import subprocess

from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

import openai

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
# Set the upload folder relative to the script location
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def translate_text(input_text, source_language, target_language):
    """
    Translates text from one language to another using OpenAI's translation model.

    :param input_text: The text to be translated.
    :param source_language: The source language of the text (e.g., 'English').
    :param target_language: The target language for translation (e.g., 'Spanish').
    :return: Translated text.
    """
    openai.api_key = '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'  # Replace with your OpenAI API key

    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Updated to the latest model
            prompt=f"Translate this from {source_language} to {target_language}: {input_text}",
            temperature=0.7,
            max_tokens=60
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload')
def upload_file():
    return render_template('upload.html')

@app.route('/greet')
def greet():
    name = request.args.get('name', 'World')
    return f'Hello, {name}!'

@app.route('/voice-recognition', methods=['POST'])
def recognize_speech():
    r = sr.Recognizer()
    audio_file = request.files['file']
    
     # Save the file to the uploads folder
    original_blob = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
    try:
        audio_file.save(original_blob)
        subprocess.run(['ffmpeg', '-i', original_blob, '-acodec', 'flac', '-ar', '16000', '-ac', '1','-y', original_blob+".flac"])
        
        flac_blob = original_blob +".flac"

        with sr.AudioFile(flac_blob) as source:
            # Adjust for ambient noise and record the audio
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = r.listen(source, timeout=5)  # Wait for up to 5 seconds for user to start speaking

        # Recognize speech using Google Web Speech API
        
        text = r.recognize_google(audio_data, language='en-US')
        return jsonify({'recognized_text': text})
    except sr.UnknownValueError:
        return jsonify({'error': "Could not understand audio"}), 400
    except sr.RequestError as e:
        return jsonify({'error': f"API unavailable; {e}"}), 500
    except sr.WaitTimeoutError:
        return jsonify({'error': "No speech was detected within the allowed time."}), 400
    finally:
        delete_file_if_exists(flac_blob)
        delete_file_if_exists(original_blob)

        #delete blob files    

def delete_file_if_exists(file_path):
    """Delete file if it exists."""
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    else:
        print(f"File {file_path} does not exist.")

if __name__ == '__main__':
    app.run(debug=True)
