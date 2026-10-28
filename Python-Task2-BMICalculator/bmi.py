import tkinter as tk
import sqlite3
import datetime
import matplotlib.pyplot as plt

def open_db():
    conn = sqlite3.connect("bmi_data.db")
    cursor = conn.cursor()

    return conn, cursor

def create_table():
    conn,cursor = open_db()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        weight REAL NOT NULL,
        height REAL NOT NULL,
        bmi REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL
        )
    """)

        conn.commit()
    finally:
        conn.close()

def save_record(name,weight,height,bmi,category):
    conn,cursor = open_db()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        cursor.execute(
        "Insert Into records (name,weight,height,bmi,category,date) Values (?,?,?,?,?,?)",
        (name,weight,height,bmi,category,date)
        )
        conn.commit()
    finally:
        conn.close()

def get_records(name):
    conn,cursor = open_db()
    try:
        cursor.execute(
        "Select * From records Where (name) = (?) Order By id",
        (name,)
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({
                "name": row[1],
                "weight":row[2],
                "height":row[3],
                "bmi":row[4],
                "category":row[5],
                "date":row[6]
            })
        return result
    finally:
        conn.close()

def calculate_bmi(weight,height):
    bmi = weight / height ** 2
    bmi = round(bmi,2)
    return bmi

def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def validate_inputs(weight_text, height_text):
    try:
        weight = float(weight_text)
        height = float(height_text)
    except ValueError:
        raise ValueError("Please enter numbers only")
    if weight <= 0 or height <=0:
        raise ValueError("Weight and Height must be greater than zero")
    if height > 3:
        raise ValueError("Height must be in metres,for example 1.75")
    return weight,height

colors = {
    "Underweight":"blue",
    "Normal":"green",
    "Overweight":"darkorange",
    "Obese":"red"
}

def on_calculate():
    try:
        weight,height = validate_inputs(weight_entry.get(),height_entry.get())
        bmi = calculate_bmi(weight,height)
        category = get_category(bmi)
        result_label.config(text=f"BMI: {bmi} ({category})",fg=colors[category])
    except ValueError as error:
        result_label.config(text=str(error),fg="black")

def on_save():
    name = name_entry.get().strip()
    if name == "":
        result_label.config(text="Please enter a name",fg="black")
        return
    try:
        weight,height = validate_inputs(weight_entry.get(),height_entry.get())
        bmi = calculate_bmi(weight,height)
        category = get_category(bmi)
        save_record(name, weight, height, bmi, category)
        result_label.config(text=f"Saved! BMI {bmi} ({category})",fg=colors[category])
    except ValueError as error:
        result_label.config(text=str(error),fg="black")
    except sqlite3.Error:
        result_label.config(text="Database error: could not save the record",fg="red")
        

def on_show_graph():
    name = name_entry.get().strip()
    if name == "":
        result_label.config(text="Please enter name:",fg="black")
        return
    try:
        records = get_records(name)
    except sqlite3.Error:
            result_label.config(text="Database error: could not read the records",fg="red")
            return
    if len(records) < 2:
        result_label.config(text="Save at least 2 records for this name to see a trend",fg="black")
        return
    dates = [row["date"] for row in records]
    bmis = [row["bmi"] for row in records]
    positions = list(range(len(records)))
    plt.plot(positions,bmis,marker="o")
    plt.xticks(positions,dates,rotation=45)
    plt.title(f"BMI trend for {name}")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.tight_layout()
    plt.axhline(18.5, color="blue", linestyle="--")
    plt.axhline(25, color="green", linestyle="--")
    plt.axhline(30, color="red", linestyle="--")
    plt.show()
    


create_table()
root = tk.Tk()
root.title("BMI Calculator")
name_label = tk.Label(root,text="Name:")
name_label.pack(pady=5)
name_entry = tk.Entry(root)
name_entry.pack()
weight_label = tk.Label(root, text = "Weight (kg):")
weight_label.pack(pady=5)
weight_entry = tk.Entry(root)
weight_entry.pack()
height_label = tk.Label(root, text = "Height (m):")
height_label.pack(pady=5)
height_entry = tk.Entry(root)
height_entry.pack()
result_label = tk.Label(root, text="", font=("Arial",14))
result_label.pack(pady=10)
calculate_button = tk.Button(root, text= "Calculate",command=on_calculate)
calculate_button.pack(pady=10)
graph_button = tk.Button(root,text="Show Trend Graph",command=on_show_graph)
graph_button.pack(pady=5)
save_button = tk.Button(root,text="Save Result",command=on_save)
save_button.pack(pady=5)
root.geometry("400x600")
root.mainloop()
