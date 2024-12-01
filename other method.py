from gtts import gTTS
import pygame
import os
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from tkinter import Tk, Label, Button, Entry, Text, Scrollbar, END, StringVar
from g4f.client import Client


def record_audio(duration=5, samplerate=16000):
    try:
        print("Listening....")
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        return np.squeeze(audio_data)
    except Exception as e:
        print(f"Error recording audio: {e}")
        return None


def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        audio = record_audio()
        if audio is None:
            return None
        print("Processing your voice...")
        audio_data = sr.AudioData(audio.tobytes(), 16000, 2)
        query = recognizer.recognize_google(audio_data)
        print(f"You said: {query}")
        return query
    except Exception as e:
        print(f"Error during speech recognition: {e}")
        return None


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
    except Exception as e:
        print(f"Error during speech synthesis: {e}")


def detect_mood_online(sentence):
    query = f"Detect Mood: {sentence}"
    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}]
        )
        detected_mood = response.choices[0].message.content
        return detected_mood
    except Exception as e:
        print(f"Error with online mood detection: {e}")
        return "An error occurred. Please try again."


# GUI Functionality
def detect_text_mood():
    user_input = text_input.get("1.0", END).strip()
    if not user_input:
        result_label.config(text="Please enter some text.")
        return
    result_label.config(text="Detecting mood...")
    detected_mood = detect_mood_online(user_input)
    result_label.config(text=f"Detected Mood: {detected_mood}")
    speak(detected_mood)


def detect_voice_mood():
    result_label.config(text="Listening for your mood...")
    speech_text = recognize_speech()
    if speech_text is None:
        result_label.config(text="Could not process your voice.")
        return
    result_label.config(text="Detecting mood...")
    detected_mood = detect_mood_online(speech_text)
    result_label.config(text=f"Detected Mood: {detected_mood}")
    speak(detected_mood)


# GUI Setup
app = Tk()
app.title("Mood Detection App")
app.geometry("900x800")
app.resizable(False, False)

# Title Label
title_label = Label(app, text="Mood Detection App", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

# Text Detection Section
text_label = Label(app, text="Enter your text below:", font=("Arial", 14))
text_label.pack(pady=5)

text_input = Text(app, height=4, width=50, font=("Arial", 12))
text_input.pack(pady=5)

detect_text_button = Button(app, text="Detect Mood from Text", font=("Arial", 12), command=detect_text_mood)
detect_text_button.pack(pady=10)

# Voice Detection Section
voice_label = Label(app, text="Or click below to speak:", font=("Arial", 14))
voice_label.pack(pady=5)

detect_voice_button = Button(app, text="Detect Mood from Voice", font=("Arial", 12), command=detect_voice_mood)
detect_voice_button.pack(pady=10)

# Result Section
result_label = Label(app, text="", font=("Arial", 14), fg="blue")
result_label.pack(pady=30)

# Quit Button
quit_button = Button(app, text="Quit", font=("Arial", 12), command=app.quit)
quit_button.pack(pady=10)

app.mainloop()