# Python Voice Assistant

A Python voice assistant that listens to spoken commands through the microphone and answers out loud.

## Features

- Captures voice input from the microphone
- Replies with a greeting when you say "hello"
- Tells the current time and date
- Searches the web for a topic you name (opens your browser)
- Speaks every response using text-to-speech
- Asks you to repeat if it did not understand you

## Tech Stack

- Python 3.12
- speech_recognition
- pyttsx3
- datetime
- webbrowser

## How to Run

1. Create a virtual environment: `py -3.12 -m venv venv`
2. Activate it: `venv\Scripts\activate`
3. Install the libraries: `pip install -r requirements.txt`
4. Start the assistant: `python assistant.py`

A working microphone and an internet connection are required.

## Example Commands

- "hello"
- "what time is it"
- "what is the date"
- "search python tutorials"
- "bye" (stops the assistant)

## Privacy

Your voice is recorded from the microphone and sent to Google's speech recognition service to be turned into text, so an internet connection is needed. This program does not save any audio or text to disk. Text-to-speech runs locally on your computer.

