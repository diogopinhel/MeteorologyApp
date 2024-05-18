import tkinter as tk
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap
from datetime import datetime, timedelta

# Function to get current weather information from OpenWeatherMap API
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
    humidity = weather['main']['humidity']
    wind_speed = weather['wind']['speed']
    description = weather['weather'][0]['description']
    city = weather['name']
    country = weather['sys']['country']
    timezone = weather['timezone']  # Get the time zone offset in seconds

    # Get the icon URL and return all the weather information
    icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
    return (icon_url, temperature, description, city, country, humidity, wind_speed, timezone)

# Function to get 5-day weather forecast from OpenWeatherMap API
def get_forecast(city):
    API_key = "1b2f8c4cbcbd0ee0ce628c4130e28dc2"
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_key}&lang=pt"
    res = requests.get(url)

    if res.status_code == 404:
        messagebox.showerror("Error", "City not found")
        return None
    
    forecast = res.json()
    daily_forecast = []

    for i in range(0, len(forecast['list']), 8):  # Get the weather for every 24 hours
        day = forecast['list'][i]
        date = datetime.utcfromtimestamp(day['dt'])
        icon_id = day['weather'][0]['icon']
        min_temp = day['main']['temp_min'] - 273.15
        max_temp = day['main']['temp_max'] - 273.15
        description = day['weather'][0]['description']
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        daily_forecast.append((date, min_temp, max_temp, description, icon_url))

    return daily_forecast

# Function to search weather for a city
def search():
    city = city_entry.get()
    result = get_weather(city)
    if result is None:
        return
    
    # If the city is found, unpack the weather information
    icon_url, temperature, description, city, country, humidity, wind_speed, timezone = result

    # Calculate local time
    local_time = datetime.utcnow() + timedelta(seconds=timezone)
    local_time_str = local_time.strftime('%H:%M:%S')

    location_label.configure(text=f"{city}, {country}")
    temperature_label.configure(text=f"Temperatura: {temperature:.2f}°C")
    humidity_label.configure(text=f"Umidade: {humidity}%")
    wind_speed_label.configure(text=f"Velocidade do vento: {wind_speed} m/s")
    description_label.configure(text=f"Descrição: {description.capitalize()}")
    timecity_label.configure(text=f"Hora local: {local_time_str}")

    # Get the weather icon image from the URL and update the icon label
    image = Image.open(requests.get(icon_url, stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon

    # Get 5-day forecast and update forecast labels
    forecast_result = get_forecast(city)
    if forecast_result:
        for i in range(5):
            date, min_temp, max_temp, description, icon_url = forecast_result[i]
            forecast_labels[i][0].configure(text=date.strftime('%A'))
            forecast_labels[i][1].configure(text=f"{min_temp:.1f}° / {max_temp:.1f}°")
            forecast_labels[i][2].configure(text=description.capitalize())
            forecast_image = Image.open(requests.get(icon_url, stream=True).raw)
            forecast_icon = ImageTk.PhotoImage(forecast_image)
            forecast_labels[i][3].configure(image=forecast_icon)
            forecast_labels[i][3].image = forecast_icon

app = ttkbootstrap.Window(themename="morph")
app.title("APLICAÇÃO METEOROLÓGICA")
app.geometry("1500x700")

# Create an entry widget -> to enter the city name
city_entry = ttkbootstrap.Entry(app, font="Helvetica, 18")
city_entry.pack(pady=10)

# Create a button widget -> to search for the weather information
search_button = ttkbootstrap.Button(app, text="Pesquisar", command=search, bootstyle="warning")
search_button.pack(pady=10)

# Create a label widget -> to show the city/country name
location_label = tk.Label(app, font="Helvetica, 25")
location_label.pack(pady=20, anchor="w", padx=30)
# Create a label widget -> to show the weather icon
icon_label = tk.Label(app)
icon_label.pack(anchor="w", padx=30)

# Create a label widget -> to show the temperature
temperature_label = tk.Label(app, font="Helvetica, 20")
temperature_label.pack(anchor="w", padx=30)

# Create a label widget -> to show the weather description
description_label = tk.Label(app, font="Helvetica, 20")
description_label.pack(anchor="w", padx=30)

# Create a label widget -> to show the humidity description
humidity_label = tk.Label(app, font="Helvetica, 20")
humidity_label.pack(anchor="w", padx=30)

# Create a label widget -> to show the wind speed description
wind_speed_label = tk.Label(app, font="Helvetica, 20")
wind_speed_label.pack(anchor="w", padx=30)

# Create a label widget -> to show the time city user selected
timecity_label = tk.Label(app, font="Helvetica, 20")
timecity_label.pack(anchor="w", padx=30)

# Create widgets to display 5-day forecast
forecast_frame = tk.Frame(app)
forecast_frame.pack(pady=20)

forecast_labels = []
for i in range(5):
    day_frame = tk.Frame(forecast_frame, padx=10, pady=-40)
    day_frame.pack(side="left")
    
    day_label = tk.Label(day_frame, font="Helvetica, 15")
    day_label.pack()

    icon_label = tk.Label(day_frame)
    icon_label.pack()

    temp_label = tk.Label(day_frame, font="Helvetica, 15")
    temp_label.pack()

    desc_label = tk.Label(day_frame, font="Helvetica, 15")
    desc_label.pack()


    forecast_labels.append((day_label, temp_label, desc_label, icon_label))

app.mainloop()
