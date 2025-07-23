# ================== BASIC WEATHER APP ==================
# Simple Tkinter GUI that fetches current weather via OpenWeather API.
# Loads API key from .env (OPENWEATHER_KEY). Weather condition maps to an icon.
# Author: Ayaan Nadeem | License: MIT

import os
import sys
import tkinter as tk
from tkinter import messagebox
import requests
from dotenv import load_dotenv

# === CONFIG / ENV ===
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_KEY")  # set in .env
URL = "https://api.openweathermap.org/data/2.5/weather"

# === PATH HELPERS ===
def resource_path(relative_path: str) -> str:
    """Return absolute path to bundled resource (works in dev + PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):  # PyInstaller temp dir
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, relative_path)

ASSETS_DIR = "assets"  # folder containing icons

# === ICON SELECTION ===
def get_icon_filename(desc: str) -> str:
    """Map weather description text to an icon filename (no path)."""
    d = desc.lower()
    if "clear" in d:
        return "sun.png"
    if "cloud" in d:
        return "cloud.png"
    if "rain" in d:
        return "rain.png"
    if "thunder" in d or "storm" in d:
        return "storm.png"
    if "snow" in d:
        return "snow.png"
    return "cloud.png"  # fallback

# === WEATHER FETCH ===
def getWeather():
    """Fetch weather for entered city and update UI + icon."""
    city_name = city_entry.get().strip()

    if not city_name:
        messagebox.showwarning("Input Error", "Please enter a city name!")
        return

    if not API_KEY:
        messagebox.showerror("Missing API Key", "OPENWEATHER_KEY not found in .env.")
        return

    params = {"q": city_name, "APPID": API_KEY, "units": "metric"}

    try:
        response = requests.get(URL, params=params, timeout=10)
    except Exception:
        result_label.config(text="Network error!", fg="red")
        weather_icon_label.config(image="")
        return

    if response.status_code == 200:
        data = response.json()
        try:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            city = data['name']
        except Exception:
            result_label.config(text="Bad API response.", fg="red")
            weather_icon_label.config(image="")
            return

        result_label.config(
            text=f" {city}\n {temp}°C\n {desc.capitalize()}",
            fg="white"
        )

        # Load & show weather icon (subsample to shrink)
        icon_name = get_icon_filename(desc)
        icon_path = resource_path(os.path.join(ASSETS_DIR, icon_name))
        try:
            new_icon = tk.PhotoImage(file=icon_path).subsample(4, 4)
            weather_icon_label.config(image=new_icon)
            weather_icon_label.image = new_icon  # keep ref
        except Exception:
            weather_icon_label.config(image="")

    elif response.status_code == 404:
        result_label.config(text="City not found. Try again.", fg="red")
        weather_icon_label.config(image="")
    else:
        result_label.config(text=f"Error {response.status_code}.", fg="red")
        weather_icon_label.config(image="")

# === GUI ===
root = tk.Tk()
root.title("Weather App")
root.geometry("420x580")
root.config(bg="#1e2a38")

# Window icon (.ico recommended)
ico_path = resource_path(os.path.join(ASSETS_DIR, "icon.ico"))
try:
    root.iconbitmap(ico_path)
except Exception:
    pass  # ignore if missing

# App logo (PNG; subsample to resize)
logo_path = resource_path(os.path.join(ASSETS_DIR, "logo.png"))
try:
    logo_img = tk.PhotoImage(file=logo_path).subsample(3, 3)
    tk.Label(root, image=logo_img, bg="#1e2a38").pack(pady=(15, 5))
except Exception:
    tk.Label(root, text="Weather", font=("Segoe UI", 20, "bold"),
             fg="white", bg="#1e2a38").pack(pady=(15, 5))

# Input label
tk.Label(root, text="Enter City Name", font=("Segoe UI", 14, "bold"),
         fg="white", bg="#1e2a38").pack()

# City entry
city_entry = tk.Entry(root, font=("Segoe UI", 13), fg="#333", bg="white",
                      justify="center", bd=2, relief="flat")
city_entry.pack(ipady=8, ipadx=5, pady=10)
city_entry.focus_set()

# Fetch button
tk.Button(root, text="Get Weather", font=("Segoe UI", 11, "bold"),
          command=getWeather, fg="white", bg="#0078D7",
          activebackground="#005A9E", relief="flat", padx=20, pady=5).pack(pady=10)

# Icon display
weather_icon_label = tk.Label(root, bg="#1e2a38")
weather_icon_label.pack(pady=10)

# Result display
result_label = tk.Label(root, text="", font=("Segoe UI", 13, "bold"),
                        bg="#1e2a38", fg="white", justify="center")
result_label.pack(pady=10)

# Enter key triggers weather fetch
root.bind("<Return>", lambda e: getWeather())

# === START ===
if __name__ == "__main__":
    root.mainloop()
