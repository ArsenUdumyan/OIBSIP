import requests
from config import API_KEY
import tkinter as tk
from PIL import Image,ImageTk
import io
import datetime

def api_get(endpoint, city, api_key):
    city = city.strip()
    if city == "":
        raise ValueError("Please enter a city name.")
    url = "https://api.openweathermap.org/data/2.5/" + endpoint
    params = {
        "q":city,
        "appid":api_key,
        "units":"metric"
    }
    try:
        response = requests.get(url,params=params,timeout=10)
    except requests.exceptions.Timeout:
        raise ValueError("The request timed out.Try again.")
    except requests.ConnectionError:
        raise ValueError("No internet connection.")
    if response.status_code == 401: 
        raise ValueError ("Invalid API key. A new key can take a while to activate.")
    elif response.status_code == 404: 
        raise ValueError("City not found.")
    elif response.status_code != 200: 
        raise ValueError (f"Weather service error (code {response.status_code}).")
    return response.json()

def get_current_weather(city,api_key):
    return api_get("weather",city,api_key)
    
def get_forecast(city, api_key):
    return api_get("forecast", city, api_key)

def detect_city():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
    except requests.exceptions.Timeout:
        raise ValueError("Location request timed out.")
    except requests.exceptions.ConnectionError:
        raise ValueError("No internet connection.")
    if response.status_code != 200:
        raise ValueError("Could not detect your location.")
    city = response.json().get("city", "")
    if city == "":
        raise ValueError("Could not detect your city.")
    return city

def parse_weather(data):
    temp_c = data["main"]["temp"]
    temp_f = temp_c * 9 / 5 + 32
    result = {
        "city":data["name"],
        "country":data["sys"]["country"],
        "temp_c": round(temp_c,1),
        "temp_f":round(temp_f,1),
        "humidity" : data["main"]["humidity"],
        "wind" : data["wind"]["speed"],
        "description" : data["weather"][0]["description"].capitalize(),
        "icon":data["weather"][0]["icon"]
    }
    return result

def parse_forecast(data):
    offset = data["city"]["timezone"]
    hourly = []
    for item in data["list"][:6]:
        local = datetime.datetime.fromtimestamp(item["dt"] + offset,tz=datetime.timezone.utc)
        hourly.append({
                "time":local.strftime("%H:%M"),
                "temp_c":round(item["main"]["temp"], 1),
                "icon":item["weather"][0]["icon"]
            })
    days = {}
    for item in data["list"]:
        local = datetime.datetime.fromtimestamp(item["dt"] + offset,tz=datetime.timezone.utc)
        day = local.strftime("%Y-%m-%d")
        gap = abs(local.hour - 12)
        if day not in days:
            days[day] = {"label":local.strftime("%a"),"temps":[],"icon":item["weather"][0]["icon"],"gap":gap}
        days[day]["temps"].append(item["main"]["temp"])
        if gap < days[day]["gap"]:
            days[day]["icon"] = item["weather"][0]["icon"]
            days[day]["gap"] = gap
    daily = []
    for entry in list(days.values())[:5]:
        daily.append({"day": entry["label"], "min": round(min(entry["temps"]), 1), "max": round(max(entry["temps"]), 1), "icon": entry["icon"]})
    return {"hourly": hourly, "daily": daily}

icon_cache={}

def get_icon(icon_code,size=100):
    key = (icon_code,size)
    if key in icon_cache:
        return icon_cache[key]
    url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    try:
        response = requests.get(url,timeout = 10)
        image = Image.open(io.BytesIO(response.content))
        image = image.resize((size,size))
        photo = ImageTk.PhotoImage(image)
        icon_cache[key]=photo
        return photo
    except Exception:
        return None

def clear_forecast():
    for widget in hourly_frame.winfo_children():
        widget.destroy()
    for widget in daily_frame.winfo_children():
        widget.destroy()

def format_temp(temp_c):
    if unit.get() == "F":
        return f"{round(temp_c * 9 / 5 + 32, 1)}°F"
    else:
        return f"{round(temp_c, 1)}°C"

def show_forecast(forecast):
    clear_forecast()
    for item in forecast["hourly"]:
        box = tk.Frame(hourly_frame)
        box.pack(side="left",padx=8)
        tk.Label(box,text=item["time"]).pack()
        icon = get_icon(item["icon"],40)
        tk.Label(box,image=icon).pack()
        tk.Label(box,text=format_temp(item["temp_c"])).pack()
    for item in forecast["daily"]:
            box = tk.Frame(daily_frame)
            box.pack(side="left",padx=8)
            tk.Label(box,text=item["day"]).pack()
            icon = get_icon(item["icon"],40)
            tk.Label(box,image=icon).pack()
            tk.Label(box,text=f"{format_temp(item['max'])} / {format_temp(item['min'])}").pack()

last = {"weather": None, "forecast": None}

def show_weather(weather):
        city_label.config(text=f"{weather['city']}, {weather['country']}")
        temp_label.config(text=format_temp(weather["temp_c"]))
        desc_label.config(text=weather["description"])
        details_label.config(text=f"Humidity: {weather['humidity']}%   Wind: {weather['wind']} m/s")
        icon = get_icon(weather["icon"])
        if icon is None:
            icon_label.config(image="")
        else:
            icon_label.config(image=icon)
        icon_label.image = icon


def on_get_weather():
    city = city_entry.get()
    try:
        data = get_current_weather(city,API_KEY)
        weather = parse_weather(data)
        forecast = parse_forecast(get_forecast(city, API_KEY))
        last["weather"] = weather
        last["forecast"] = forecast
        show_weather(weather)
        show_forecast(forecast)
        error_label.config(text="")
    except ValueError as error:
        error_label.config(text=str(error))
        city_label.config(text=""), temp_label.config(text=""), desc_label.config(text=""),details_label.config(text=""),icon_label.config(image="")
        icon_label.image = None
        clear_forecast()

def on_detect():
    try:
        city = detect_city()
        city_entry.delete(0, tk.END)
        city_entry.insert(0, city)
        on_get_weather()
    except ValueError as error:
        error_label.config(text=str(error))

def on_toggle():
    if unit.get() == "C":
        unit.set("F")
        toggle_button.config(text="Switch to °C")  
    else:
        unit.set("C")
        toggle_button.config(text="Switch to °F")
    if last["weather"] is not None:
        show_weather(last["weather"])
        show_forecast(last["forecast"])  

root = tk.Tk()
unit = tk.StringVar(value="C")
root.title("Weather app")
root.geometry("600x780")
tk.Label(root,text="Enter the city name:").pack(pady=(15,5))
city_entry = tk.Entry(root,width=30)
city_entry.pack()
tk.Button(root, text="Use my location", command=on_detect).pack(pady=5)
tk.Button(root,text="Get Weather",command=on_get_weather).pack(pady=10)
toggle_button = tk.Button(root, text="Switch to °F", command=on_toggle)
toggle_button.pack()
icon_label = tk.Label(root)
icon_label.pack()
city_label = tk.Label(root,text="",font=("Arial", 18, "bold"))
city_label.pack()
temp_label = tk.Label(root,text="",font=("Arial", 16))
temp_label.pack()
desc_label = tk.Label(root,text="",font=("Arial", 12))
desc_label.pack()
details_label = tk.Label(root,text="",font=("Arial", 12))
details_label.pack()
error_label = tk.Label(root,text="",fg="red")
error_label.pack()
tk.Label(root,text="Next Hours (3-hour steps)",font=("Arial",11,"bold")).pack(pady=(15,5))
hourly_frame = tk.Frame(root)
hourly_frame.pack()
tk.Label(root, text="Next 5 days", font=("Arial", 11, "bold")).pack(pady=(15, 5))
daily_frame = tk.Frame(root)
daily_frame.pack()
root.after(500, on_detect)
root.mainloop()