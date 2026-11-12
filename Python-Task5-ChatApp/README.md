# Chat App

A real-time chat application built with Python sockets, threading, tkinter and SQLite. Users register and log in, join named rooms, see the message history of a room, and chat with timestamps.

## Features

- Server that accepts many clients at the same time (one thread per client)
- GUI client built with tkinter
- User registration and login (stored in SQLite, passwords hashed with a salt)
- Multiple chat rooms: type a name to create or join a room
- Message history: the last 50 messages of a room are loaded when you join it
- Messages shown with a timestamp, e.g. `[14:35] Anna: Hello`
- Join, leave and disconnect notifications for the other users in the room
- In-app notification when a message arrives while the window is not focused (window title counter and a sound)
- Emoji shortcodes such as `:smile:` are turned into emoji (`:smile:` `:laugh:` `:wink:` `:cool:` `:sad:` `:heart:` `:thumbsup:` `:clap:` `:fire:` `:party:`)
- Database errors are caught and reported instead of crashing the server

## Tech Stack

- Python 3.12
- socket and threading (networking)
- tkinter (GUI)
- sqlite3 (users and message history)
- hashlib, hmac and os (password hashing)

No extra libraries need to be installed.

## How to Run

1. Start the server: `python server.py`
2. In another terminal, start a client: `python client.py`
3. Start more clients (one per terminal) to chat between users
4. Click **Register** the first time, then **Login**

The server and the clients run on `localhost` (127.0.0.1), port 5555. Run everything from the same folder, because the database file `chat.db` is created next to `server.py`.

## How Messages and Data Are Stored (Security Transparency)

- **Messages are stored in plain text** in the file `chat.db` (SQLite), together with the room, the username and the time. Anyone who can read that file can read all messages.
- **Messages are not encrypted when sent.** The connection is plain TCP, so anyone who can watch the network traffic could read messages and passwords. This project is meant for localhost. A real deployment would need TLS.
- **Passwords are not stored as text.** Each one is hashed with PBKDF2-SHA256 and a random salt, and only the salt and the hash are saved.
- The password itself is sent to the server in plain form during login (no TLS), which is another reason not to use this over the open internet.
- There is **no end-to-end encryption**: the server can read every message.
- There is no limit on login attempts, so passwords could be guessed by repeated tries.
- `chat.db` is listed in `.gitignore`, so it is never uploaded to GitHub.

## Project Structure

- `server.py` - the server (accounts, rooms, history, relaying messages)
- `client.py` - the tkinter chat window
- `README.md` - this file

