import pyttsx3
import datetime
import speech_recognition as sr
import os

# Initialize the speech engine (kept for legacy but not used in web app)
try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
except:
    pass

def pspk(audio):
    """Makes the computer speak, as well as prints the statement."""
    print(audio)
    # speak(audio) # Disabled for Web App to prevent blocking

def speak(audio):
    """Makes the computer speak."""
    pass
    # engine.say(audio)
    # engine.runAndWait()

def wishMe():
    """Wishes you on starting of the program."""
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        pspk("Good Morning")
    elif hour >= 12 and hour < 18:
        pspk("Good Afternoon")
    else:
        pspk("Good Evening")

    pspk("I am Jarvis 1.0, How may I help you?")

def takeCommand():
    """Takes input from the microphone and converts it into Strings."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1.1)
        r.pause_threshold = 0.7
        audio = r.listen(source)
    
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        return "none"
    return query

def load_api_key():
    """Load the Google API key from environment variables.
    Raises an EnvironmentError if the variable is missing.
    """
    key = os.getenv('GOOGLE_API_KEY')
    if not key:
        raise EnvironmentError('GOOGLE_API_KEY environment variable not set.')
    return key