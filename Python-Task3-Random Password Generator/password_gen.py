import secrets
import string
import tkinter as tk
import pyperclip
AMBIGUOUS = "0O1lI"

def build_pools(use_upper,use_lower,use_digits,use_symbols,exclude_ambiguous):
    pools = []
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_lower:
            pools.append(string.ascii_lowercase)
    if use_digits:
            pools.append(string.digits) 
    if use_symbols:
            pools.append(string.punctuation)
    if exclude_ambiguous:
            cleaned = []
            for pool in pools:
                   new_pool = ""
                   for char in pool:
                        if char not in AMBIGUOUS:
                                new_pool = new_pool + char
                   cleaned.append(new_pool)
            pools = cleaned
    return pools

def generate_password(length,pools):
    chars = []
    for pool in pools:
            chars.append(secrets.choice(pool))
    all_chars = "".join(pools)
    while len(chars) < length:
            chars.append(secrets.choice(all_chars))
    for i in range(len(chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chars[i],chars[j] = chars[j], chars[i]
    return "".join(chars)

def validate_settings(length_text,use_upper,use_lower,use_digits,use_symbols):
        try:
              length = int(length_text)
        except ValueError:
               raise ValueError("Length must be a whole number.")
        if length < 8:
               raise ValueError("Length must be at least 8.")
        if length > 64:
               raise ValueError("Length must be 64 or less.")
        selected = [use_upper,use_lower,use_digits,use_symbols].count(True)
        if selected < 2:
               raise ValueError("Select at least 2 character types.")
        return length

def get_strength(password):
        score = 0
        if len(password) >= 12:
              score = score + 1
        if len(password) >= 16:
                      score = score + 1
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        types = [has_upper,has_lower,has_digit,has_symbol].count(True)
        score = score + (types - 1)
        if score < 3:
               return "Weak"
        elif score == 3:
               return "Medium"
        else:
               return "Strong"

strength_colors = {"Weak": "red",
                   "Medium": "darkorange",
                   "Strong": "green"
                }

history = []

def on_generate():
    try:
        length = validate_settings(length_var.get(),upper_var.get(),lower_var.get(),digits_var.get(),symbols_var.get())
        pools = build_pools(upper_var.get(),lower_var.get(),digits_var.get(),symbols_var.get(),ambiguous_var.get())
        password = generate_password(length,pools)
        password_label.config(text=password)
        pyperclip.copy(password)
        strength = get_strength(password)
        strength_label.config(text=f"Strength: {strength}",fg=strength_colors[strength])
        history.insert(0,password)
        if len(history) > 5:
               history.pop()
        history_label.config(text="\n".join(history))
        message_label.config(text="Copied to Clipboard",fg="green")
    except ValueError as error:
           message_label.config(text=str(error),fg="red")
           password_label.config(text="")
           strength_label.config(text="")

def on_copy():
       password = password_label.cget("text")
       if password == "" :
              message_label.config(text="Generate a password first",fg="red")
              return
       pyperclip.copy(password)
       message_label.config(text="Copied to Clipboard",fg="green")


              
       
root = tk.Tk()
root.title("Password Generator")
root.geometry("420x700")
length_var = tk.StringVar(value="12")
tk.Label(root,text="Password length:").pack(pady=5)
length_spin = tk.Spinbox(root,from_=8,to=64,textvariable=length_var,width=5)
length_spin.pack()
upper_var = tk.BooleanVar(value=True)
lower_var = tk.BooleanVar(value=True)
digits_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=False)
ambiguous_var = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Uppercase (A-Z)", variable=upper_var).pack(anchor="w", padx=100)
tk.Checkbutton(root, text="Lowercase (a-z)", variable=lower_var).pack(anchor="w", padx=100)
tk.Checkbutton(root, text="Numbers (0-9)", variable=digits_var).pack(anchor="w", padx=100)
tk.Checkbutton(root, text="Symbols (!@#...)", variable=symbols_var).pack(anchor="w", padx=100)
tk.Checkbutton(root, text="Exclude ambiguous (0, O, l, 1, I)", variable=ambiguous_var).pack(anchor="w", padx=100)
tk.Label(root,text="Last 5 passwords:").pack(pady=(15,0))
history_label = tk.Label(root,text = "",font=("Courier",11),justify="left")
history_label.pack()
password_label = tk.Label(root,text = "",font=("Courier",16))
password_label.pack(pady=15)
strength_label = tk.Label(root,text="",font=("Arial",12,"bold"))
strength_label.pack()
message_label = tk.Label(root,text = "",fg="red")
message_label.pack()
tk.Button(root, text="Generate Password", command=on_generate).pack(pady=10)
tk.Button(root,text="Copy to Clipboard",command=on_copy).pack(pady=5)
root.mainloop()


