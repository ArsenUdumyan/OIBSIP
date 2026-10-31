# Random Password Generator

A desktop password generator built with Python and tkinter. It creates strong random passwords from the options you choose, rates their strength, and copies them to the clipboard.

## Features

- Password length from 8 to 64 characters (spinbox)
- Choose character types: uppercase, lowercase, numbers, symbols (at least 2 required)
- Uses the `secrets` module for cryptographically secure randomness
- Guarantees at least one character from every selected type
- Option to exclude ambiguous characters (0, O, 1, l, I)
- Strength indicator: Weak, Medium or Strong, based on length and character variety
- Password is copied to the clipboard automatically, plus a Copy button
- History of the last 5 passwords from the current session
- Input validation with clear error messages

## Tech Stack

- Python 3.12
- tkinter (GUI)
- secrets and string (generation)
- pyperclip (clipboard)

## How to Run

1. Create a virtual environment: `py -3.12 -m venv venv`
2. Activate it: `venv\Scripts\activate`
3. Install the libraries: `pip install -r requirements.txt`
4. Start the app: `python password_gen.py`

## How the Strength Rating Works

Points are added for length (12 or more, and 16 or more) and for each character type beyond the first. 0 to 2 points is Weak, 3 is Medium, and 4 or more is Strong.

## Security and Privacy

- Passwords are generated locally on your computer and are never sent anywhere.
- Nothing is saved to disk. The history of the last 5 passwords lives only in memory and disappears when you close the program.
- Windows can keep its own clipboard history (Win+V), so clear it after copying a real password.

