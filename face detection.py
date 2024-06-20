import numpy as np
import cv2
import tflite_runtime.interpreter as tflite
from openai import OpenAI
from dotenv import load_dotenv
import time
import speech_recognition as sr
import pyttsx3
import re
from gtts import gTTS
from playsound import playsound
from pygame import mixer

# Define the full path to the cascade classifier XML file
cascade_path = "haarcascade_frontalface_default.xml"

# Load face cascade using OpenCV
face_cascade = cv2.CascadeClassifier(cascade_path)

# Initialize OpenAI client
client = OpenAI(api_key='your api key')
load_dotenv()

# Initialize speech recognition and text-to-speech
r = sr.Recognizer()
engine = pyttsx3.init("dummy")
voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)

# Function to perform face emotion detection
def detect_emotion(frame, interpreter):
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        image=img_gray, scaleFactor=1.3, minNeighbors=5)
    for (x, y, w, h) in faces:
        roi_gray = img_gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
        if np.sum([roi_gray]) != 0:
            roi = roi_gray.astype('float32') / 255.0
            roi = np.expand_dims(roi, axis=-1)  # Expand dimensions to add a channel dimension
            roi = np.expand_dims(roi, axis=0)   # Expand dimensions to add a batch dimension
            interpreter.set_tensor(input_index, roi)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_index)
            maxindex = int(np.argmax(output_data))
            finalout = emotion_labels[maxindex]
            output = str(finalout)
        label_position = (x, y-10)
        cv2.putText(frame, output, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if(output == 'Sad'):
            prompt = "The person is feeling sad. What should I say?"
            with sr.Microphone() as source:
                listen_and_respond(source, prompt)
    return frame

# Function to capture video from webcam and perform emotion detection
def run_emotion_detection(interpreter):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        frame = detect_emotion(frame, interpreter)
        cv2.imshow('Face Emotion Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def listen_and_respond(source, prompt):
    print("Listening...")
    while True:
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
           
            if not text:
                continue

            # Send input to OpenAI API
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
                mixer.init()
                mixer.music.load('response.mp3')
                mixer.music.play()

                # Speak the response text
                engine.say(formatted_response_text)
                engine.runAndWait()
            else:
                print("The response text is empty.")
        except sr.UnknownValueError:
            time.sleep(2)
            print("Nothing detected. Listening again...")
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            engine.say(f"Could not request results: {e}")
            engine.runAndWait()

# Load TensorFlow Lite model
interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_index = interpreter.get_input_details()[0]['index']
output_index = interpreter.get_output_details()[0]['index']

# Define the emotions.
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

# Main function to run the application
def main():
    print("Starting Face Emotion Detection...")
    run_emotion_detection(interpreter)

if _name_ == "_main_":
    main()