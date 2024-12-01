from flask import Flask, request, jsonify, render_template
from gtts import gTTS
import pygame
import os
import sounddevice as sd
import numpy as np
import speech_recognition as sr

# Placeholder for online client (replace with actual implementation if necessary)
from g4f.client import Client

app = Flask(__name__)

# Helper functions
def record_audio(duration=5, samplerate=16000):
    try:
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        return np.squeeze(audio_data)
    except Exception as e:
        return None


def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        audio = record_audio()
        if audio is None:
            return None
        audio_data = sr.AudioData(audio.tobytes(), 16000, 2)
        return recognizer.recognize_google(audio_data)
    except Exception as e:
        return None


def detect_mood(sentence):
    sentence = sentence.lower()
    mood_keywords = {
        "happy": "Happy",
        "good": "Happy",
        "sad": "Sad",
        "bad": "Sad",
        "angry": "Angry",
        "wow": "Surprised",
        "excited": "Excited",
        "bored": "Bored",
        "thank you": "Happy"
    }
    for keyword, mood in mood_keywords.items():
        if keyword in sentence:
            return f"Your mood is {mood}."
    return "Your mood is Neutral."


def speak(text):
    try:
        tts = gTTS(text)
        tts.save('temp.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        os.remove("temp.mp3")
    except Exception:
        pass


# Flask Routes
@app.route('/')
def index():
    return render_template('main.html')  # HTML file for the frontend interface


@app.route('/text-to-mood-offline', methods=['POST'])
def text_to_mood_offline():
    data = request.get_json()
    sentence = data.get('sentence', '')
    if not sentence:
        return jsonify({'error': "No input provided."})
    mood = detect_mood(sentence)
    return jsonify({'mood': mood})


@app.route('/text-to-mood-online', methods=['POST'])
def text_to_mood_online():
    data = request.get_json()
    sentence = data.get('sentence', '')
    if not sentence:
        return jsonify({'error': "No input provided."})
    query = f"Detect Mood: {sentence} ,reply in english"
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}]
        )
        detected_mood = response.choices[0].message.content
        return jsonify({'mood': detected_mood})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/voice-to-mood-offline', methods=['POST'])
def voice_to_mood_offline():
    speech_text = recognize_speech()
    if not speech_text:
        return jsonify({'error': "Could not process your voice. Try again."})
    mood = detect_mood(speech_text)
    return jsonify({'speech': speech_text, 'mood': mood})


@app.route('/voice-to-mood-online', methods=['POST'])
def voice_to_mood_online():
    speech_text = recognize_speech()
    if not speech_text:
        return jsonify({'error': "Could not process your voice. Try again."})
    query = f"Detect Mood: {speech_text} ,reply in english"
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}]
        )
        detected_mood = response.choices[0].message.content
        return jsonify({'speech': speech_text, 'mood': detected_mood})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)