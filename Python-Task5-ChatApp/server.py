import socket
import threading
import sqlite3
import json
import hashlib
import hmac
import os
import re
import datetime

HOST = "127.0.0.1"
PORT = 5555
DB_FILE = "chat.db"

EMOJI = {
    ":smile:": "😄",
    ":laugh:": "😂",
    ":wink:": "😉",
    ":cool:": "😎",
    ":sad:": "😢",
    ":heart:": "❤️",
    ":thumbsup:": "👍",
    ":clap:": "👏",
    ":fire:": "🔥",
    ":party:": "🎉",
}

clients = {}      
rooms = set()     
db_lock = threading.Lock()



def run_query(sql, params=(), fetch=False):
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        try:
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall() if fetch else None
            conn.commit()
            return rows
        finally:
            conn.close()


def init_db():
    run_query(
        "CREATE TABLE IF NOT EXISTS users ("
        "username TEXT PRIMARY KEY, salt TEXT NOT NULL, password_hash TEXT NOT NULL)"
    )
    run_query(
        "CREATE TABLE IF NOT EXISTS messages ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL, "
        "username TEXT NOT NULL, text TEXT NOT NULL, created_at TEXT NOT NULL)"
    )


def load_rooms():
    rooms.add("general")
    rows = run_query("SELECT DISTINCT room FROM messages", fetch=True)
    for row in rows:
        rooms.add(row[0])



def hash_password(password, salt_hex):
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 200000
    )
    return digest.hex()


def register_user(username, password):
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
        return False, "Username must be 3-20 letters, numbers or underscores."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    salt = os.urandom(16).hex()
    try:
        run_query(
            "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
            (username, salt, hash_password(password, salt)),
        )
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    return True, ""


def check_login(username, password):
    rows = run_query(
        "SELECT salt, password_hash FROM users WHERE username = ?",
        (username,),
        fetch=True,
    )
    if not rows:
        return False
    salt, stored_hash = rows[0]
    return hmac.compare_digest(hash_password(password, salt), stored_hash)



def replace_emoji(text):
    for code, symbol in EMOJI.items():
        text = text.replace(code, symbol)
    return text


def save_message(room, username, text, created_at):
    run_query(
        "INSERT INTO messages (room, username, text, created_at) VALUES (?, ?, ?, ?)",
        (room, username, text, created_at),
    )


def get_history(room, limit=50):
    rows = run_query(
        "SELECT username, text, created_at FROM ("
        "SELECT id, username, text, created_at FROM messages "
        "WHERE room = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
        (room, limit),
        fetch=True,
    )
    return [{"user": r[0], "text": r[1], "time": r[2][11:16]} for r in rows]



def send(conn, state, obj):
    """Send one JSON message ending with a newline (one message per line)."""
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    with state["lock"]:
        conn.sendall(data)


def broadcast_room(room, obj):
    for conn, state in list(clients.items()):
        if state["room"] == room:
            try:
                send(conn, state, obj)
            except OSError:
                pass


def broadcast_all(obj):
    for conn, state in list(clients.items()):
        try:
            send(conn, state, obj)
        except OSError:
            pass


def system_message(text):
    return {"type": "system", "text": text}


def parse_line(line):
    try:
        request = json.loads(line)
    except ValueError:
        return None
    return request if isinstance(request, dict) else None



def authenticate(conn, state, reader):
    while True:
        line = reader.readline()
        if not line:
            return False
        request = parse_line(line)
        if request is None:
            continue
        kind = request.get("type")
        username = str(request.get("username", "")).strip()
        password = str(request.get("password", ""))
        if kind == "register":
            ok, message = register_user(username, password)
            if not ok:
                send(conn, state, {"type": "auth_error", "text": message})
                continue
        elif kind == "login":
            if not check_login(username, password):
                send(conn, state, {"type": "auth_error", "text": "Wrong username or password."})
                continue
        else:
            continue
        state["user"] = username
        send(conn, state, {"type": "auth_ok", "username": username})
        return True


def join_room(conn, state, room):
    room = room.strip().lower()
    if not re.fullmatch(r"[a-z0-9_-]{1,20}", room):
        send(conn, state, system_message("Room names: 1-20 letters, numbers, - or _."))
        return
    old_room = state["room"]
    if old_room == room:
        return
    user = state["user"]
    if old_room:
        state["room"] = None
        broadcast_room(old_room, system_message(f"{user} left the room"))
    history = get_history(room)
    state["room"] = room
    send(conn, state, {"type": "history", "room": room, "messages": history})
    if room not in rooms:
        rooms.add(room)
        broadcast_all({"type": "rooms", "rooms": sorted(rooms)})
    else:
        send(conn, state, {"type": "rooms", "rooms": sorted(rooms)})
    broadcast_room(room, system_message(f"{user} joined the room"))


def handle_request(conn, state, request):
    kind = request.get("type")
    if kind == "msg":
        text = str(request.get("text", "")).strip()[:500]
        if text == "":
            return
        text = replace_emoji(text)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        room = state["room"]
        try:
            save_message(room, state["user"], text, now)
        except sqlite3.Error:
            send(conn, state, system_message("Database error: message not saved."))
            return
        broadcast_room(room, {
            "type": "msg", "room": room, "time": now[11:16],
            "user": state["user"], "text": text,
        })
    elif kind == "join":
        join_room(conn, state, str(request.get("room", "")))
    elif kind == "rooms":
        send(conn, state, {"type": "rooms", "rooms": sorted(rooms)})


def handle_client(conn, addr):
    print(f"{addr} connected")
    state = {"user": None, "room": None, "lock": threading.Lock()}
    reader = conn.makefile("r", encoding="utf-8")
    try:
        if not authenticate(conn, state, reader):
            return
        clients[conn] = state
        print(f"{state['user']} logged in")
        join_room(conn, state, "general")
        for line in reader:
            request = parse_line(line)
            if request is not None:
                handle_request(conn, state, request)
    except (OSError, sqlite3.Error):
        pass
    finally:
        if conn in clients:
            del clients[conn]
            if state["room"]:
                broadcast_room(state["room"], system_message(f"{state['user']} left the chat"))
            print(f"{state['user']} disconnected")
        conn.close()


def main():
    init_db()
    load_rooms()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on {HOST}:{PORT} ... (Ctrl+C to stop)")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    main()