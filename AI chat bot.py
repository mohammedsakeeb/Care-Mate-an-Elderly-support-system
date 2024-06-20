import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import speech_recognition as sr
import pyttsx3
import numpy as np
import re
from gtts import gTTS
from playsound import playsound
from pygame import mixer
import time

language = 'en'
client = OpenAI(api_key='your api key ')
load_dotenv()

r = sr.Recognizer()
engine = pyttsx3.init("dummy")
voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)

def listen_and_respond(source):
    print("Listening...")
    while True:
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
            
            if not text:
                continue

            # Send input to OpenAI API
            prompt = text
            
            response = client.completions.create(prompt=prompt,model="gpt-3.5-turbo-instruct",top_p=0.5, max_tokens=50,stream=True)
            # Create one continuous string
            concatenated_string = ""
            for part in response:
                concatenated_string += part.choices[0].text.strip()

            response_text = concatenated_string

            # Ensure proper spacing between words
            formatted_response_text = re.sub(r'(?<=[.,!?])(?=[^\s])', ' ', response_text)
            
            print(f"Original Response Text: {response_text}")
            print(f"Formatted Response Text: {formatted_response_text}")

            if formatted_response_text.strip():
                print("generating audio")
                myobj = gTTS(text=formatted_response_text, lang=language, slow=False)
                print("Audio generated. Now saving as response.mp3...")

                myobj.save("response.mp3")
                print("File successfully saved. Now playing...")

                # Play the audio file
                audio_file_path = "response.mp3"
                #playsound(audio_file_path)
                mixer.init()
                mixer.music.load('response.mp3')
                mixer.music.play()
                # Speak the response text
                engine.say(formatted_response_text)
                engine.runAndWait()
                time.sleep(10)
            else:
                print("The response text is empty.")
        except sr.UnknownValueError:
            time.sleep(2)
            print("Nothing detected. Listening again...")
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            engine.say(f"Could not request results: {e}")
            engine.runAndWait()

with sr.Microphone() as source:
    listen_and_respond(source)