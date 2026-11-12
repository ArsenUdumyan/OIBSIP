import json
import queue
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "127.0.0.1"
PORT = 5555
APP_TITLE = "Chat App"


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("720x500")
        self.sock = None
        self.incoming = queue.Queue()   
        self.unread = 0
        self.username = None
        self.current_room = None
        self.rooms = []
        self.chat_area = None
        self.build_login()
        self.root.bind("<FocusIn>", self.on_focus)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.process_queue)

    def build_login(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(expand=True)
        tk.Label(self.login_frame, text="Chat App", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(self.login_frame, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_frame, width=25)
        self.username_entry.pack()
        tk.Label(self.login_frame, text="Password:").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self.login_frame, width=25, show="*")
        self.password_entry.pack()
        buttons = tk.Frame(self.login_frame)
        buttons.pack(pady=10)
        tk.Button(buttons, text="Login", command=lambda: self.authenticate("login")).pack(side="left", padx=5)
        tk.Button(buttons, text="Register", command=lambda: self.authenticate("register")).pack(side="left", padx=5)
        self.login_error = tk.Label(self.login_frame, text="", fg="red", wraplength=300)
        self.login_error.pack()
        self.password_entry.bind("<Return>", lambda event: self.authenticate("login"))
        self.username_entry.focus_set()

    def connect(self):
        if self.sock is not None:
            return True
        try:
            sock = socket.create_connection((HOST, PORT), timeout=5)
        except OSError:
            self.login_error.config(text="Could not connect to the server.")
            return False
        sock.settimeout(None)
        self.sock = sock
        threading.Thread(target=self.read_loop, daemon=True).start()
        return True

    def authenticate(self, kind):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if username == "" or password == "":
            self.login_error.config(text="Enter a username and a password.")
            return
        if not self.connect():
            return
        self.login_error.config(text="")
        self.send({"type": kind, "username": username, "password": password})


    def send(self, obj):
        if self.sock is None:
            return False
        try:
            self.sock.sendall((json.dumps(obj) + "\n").encode("utf-8"))
            return True
        except OSError:
            return False

    def read_loop(self):
        """Runs in a background thread. Never touches tkinter widgets."""
        try:
            for line in self.sock.makefile("r", encoding="utf-8"):
                try:
                    self.incoming.put(json.loads(line))
                except ValueError:
                    pass
        except OSError:
            pass
        self.incoming.put({"type": "disconnected"})

    def process_queue(self):
        while not self.incoming.empty():
            self.handle_message(self.incoming.get())
        self.root.after(100, self.process_queue)

    def handle_message(self, msg):
        kind = msg.get("type")
        if kind == "auth_ok":
            self.username = msg["username"]
            self.build_chat()
        elif kind == "auth_error":
            self.login_error.config(text=msg.get("text", "Login failed."))
        elif kind == "history":
            self.show_history(msg["room"], msg["messages"])
        elif kind == "msg":
            self.show_chat_message(msg)
        elif kind == "system":
            self.display(msg["text"], "system")
        elif kind == "rooms":
            self.update_rooms(msg["rooms"])
        elif kind == "disconnected":
            self.sock = None
            if self.chat_area is not None:
                self.display("Disconnected from the server.", "system")
            else:
                self.login_error.config(text="Disconnected from the server.")


    def build_chat(self):
        self.login_frame.destroy()
        side = tk.Frame(self.root)
        side.pack(side="left", fill="y", padx=5, pady=5)
        tk.Label(side, text="Rooms", font=("Arial", 12, "bold")).pack()
        self.room_list = tk.Listbox(side, height=12, exportselection=False)
        self.room_list.pack(fill="y", expand=True)
        self.room_list.bind("<<ListboxSelect>>", self.on_room_select)
        self.new_room_entry = tk.Entry(side, width=16)
        self.new_room_entry.pack(pady=(10, 2))
        self.new_room_entry.bind("<Return>", self.on_new_room)
        tk.Button(side, text="Create / Join", command=self.on_new_room).pack()

        main = tk.Frame(self.root)
        main.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.room_label = tk.Label(main, text="", font=("Arial", 12, "bold"))
        self.room_label.pack(anchor="w")
        self.chat_area = scrolledtext.ScrolledText(main, state="disabled", wrap="word")
        self.chat_area.pack(fill="both", expand=True)
        self.chat_area.tag_config("system", foreground="gray")
        self.chat_area.tag_config("me", foreground="blue")
        bottom = tk.Frame(main)
        bottom.pack(fill="x", pady=(5, 0))
        self.message_entry = tk.Entry(bottom)
        self.message_entry.pack(side="left", fill="x", expand=True)
        self.message_entry.bind("<Return>", self.on_send)
        tk.Button(bottom, text="Send", command=self.on_send).pack(side="left", padx=(5, 0))
        self.message_entry.focus_set()

    def display(self, text, tag=None):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, text + "\n", tag)
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    def show_history(self, room, messages):
        self.current_room = room
        self.room_label.config(text=f"Room: {room}")
        self.chat_area.config(state="normal")
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.config(state="disabled")
        if not messages:
            self.display("No messages yet. Say hello!", "system")
        for item in messages:
            self.display(f"[{item['time']}] {item['user']}: {item['text']}",
                         "me" if item["user"] == self.username else None)
        self.update_rooms(self.rooms)

    def show_chat_message(self, msg):
        mine = msg["user"] == self.username
        self.display(f"[{msg['time']}] {msg['user']}: {msg['text']}", "me" if mine else None)
        if not mine and self.root.focus_displayof() is None:
            self.unread += 1
            self.root.title(f"({self.unread}) New message - {APP_TITLE}")
            self.root.bell()

    def on_focus(self, event=None):
        if self.unread:
            self.unread = 0
            self.root.title(APP_TITLE)

    def update_rooms(self, rooms):
        self.rooms = rooms
        self.room_list.delete(0, tk.END)
        for room in rooms:
            self.room_list.insert(tk.END, room)
        if self.current_room in rooms:
            index = rooms.index(self.current_room)
            self.room_list.selection_set(index)


    def on_send(self, event=None):
        text = self.message_entry.get().strip()
        if text == "":
            return
        if self.send({"type": "msg", "text": text}):
            self.message_entry.delete(0, tk.END)
        else:
            self.display("Connection lost. Message not sent.", "system")

    def on_room_select(self, event=None):
        selection = self.room_list.curselection()
        if selection:
            room = self.room_list.get(selection[0])
            if room != self.current_room:
                self.send({"type": "join", "room": room})

    def on_new_room(self, event=None):
        name = self.new_room_entry.get().strip()
        if name:
            self.send({"type": "join", "room": name})
            self.new_room_entry.delete(0, tk.END)

    def on_close(self):
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    ChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
