import tkinter as tk
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap
from datetime import datetime, timedelta

# Function to get weather information from OpenWeatherMap API
def get_weather(city):
    API_key = "1b2f8c4cbcbd0ee0ce628c4130e28dc2"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&lang=pt"
    res = requests.get(url)

    if res.status_code == 404:
        messagebox.showerror("Error", "City not found")
        return None
    
    # Parse the response JSON to get weather information
    weather = res.json()
    icon_id = weather['weather'][0]['icon']
    temperature = weather['main']['temp'] - 273.15
    description = weather['weather'][0]['description']
    city = weather['name']
    country = weather['sys']['country']
    timezone = weather['timezone']  # Get the time zone offset in seconds

    # Get the icon URL and return all the weather information
    icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
    return (icon_url, temperature, description, city, country, timezone)

# Function to search weather for a city
def search():
    city = city_entry.get()
    result = get_weather(city)
    if result is None:
        return
    
    # If the city is found, unpack the weather information
    icon_url, temperature, description, city, country, timezone = result

    # Calculate local time
    local_time = datetime.utcnow() + timedelta(seconds=timezone)
    local_time_str = local_time.strftime('%H:%M:%S')

    location_label.configure(text=f"{city}, {country}")
    temperature_label.configure(text=f"Temperatura: {temperature:.2f}°C")
    description_label.configure(text=f"Descrição: {description.capitalize()}")
    timecity_label.configure(text=f"Hora local: {local_time_str}")

    # Get the weather icon image from the URL and update the icon label
    image = Image.open(requests.get(icon_url, stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon

app = ttkbootstrap.Window(themename="morph")
app.title("APLICAÇÃO METEOROLÓGICA")
app.geometry("400x500")

# Create an entry widget -> to enter the city name
city_entry = ttkbootstrap.Entry(app, font="Helvetica, 18")
city_entry.pack(pady=10)

# Create a button widget -> to search for the weather information
search_button = ttkbootstrap.Button(app, text="Pesquisar", command=search, bootstyle="warning")
search_button.pack(pady=10)

# Create a label widget -> to show the city/country name
location_label = tk.Label(app, font="Helvetica, 25")
location_label.pack(pady=20)

# Create a label widget -> to show the weather icon
icon_label = tk.Label(app)
icon_label.pack()

# Create a label widget -> to show the temperature
temperature_label = tk.Label(app, font="Helvetica, 20")
temperature_label.pack()

# Create a label widget -> to show the weather description
description_label = tk.Label(app, font="Helvetica, 20")
description_label.pack()

# Create a label widget -> to show the time city user selected
timecity_label = tk.Label(app, font="Helvetica, 20")
timecity_label.pack()

app.mainloop()
