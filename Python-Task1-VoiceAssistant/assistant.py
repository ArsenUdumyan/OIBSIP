import pyttsx3
import speech_recognition as sr
import  datetime
import webbrowser

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source,timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            speak("Sorry, I didn’t catch that. Please repeat.")
            return ""
        except sr.RequestError:
            speak("Can’t reach the speech service. Check your internet.")
            return ""
        except sr.WaitTimeoutError:
            speak("I didn't hear anything.")
            return ""

def process(command):
    command = command.lower()
    if "hello" in command:
        speak("Hello,how can I help you?")
    elif "search" in command:
        topic = command.replace("search","")
        topic = topic.strip()
        url = "https://www.google.com/search?q=" + topic.replace(" ", "+") 
        speak(f"Searching for {topic}")
        webbrowser.open(url)
    elif "time" in command:
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        speak(f"The time is {current_time}")
    elif "date" in command:
        now = datetime.datetime.now()
        current_date = now.strftime("%A, %d %B %Y")
        speak(f"The date is {current_date}")
    else:
        speak("Sorry, I don’t know how to do that yet.")

while True:
    command = listen()
    if command == "":
        continue
    if "bye" in command.lower():
        speak("Goodbye!")
        break
    process(command)