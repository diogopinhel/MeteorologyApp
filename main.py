import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from datetime import datetime, timedelta
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Configuration (move sensitive information to environment variables)
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', '1b2f8c4cbcbd0ee0ce628c4130e28dc2')
EMAIL_USER = os.getenv('EMAIL_USER', 'joao.lima04@outlook.pt')
EMAIL_PASS = os.getenv('EMAIL_PASS', 'Apagado2_')

# Function to get current weather information from OpenWeatherMap API
def get_weather_by_city(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Error", "City not found")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def get_weather_by_coordinates(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Error", "Coordinates not found")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def parse_weather_data(weather):
    icon_id = weather['weather'][0]['icon']
    temperature = weather['main']['temp'] - 273.15
    humidity = weather['main']['humidity']
    wind_speed = weather['wind']['speed']
    pressure = weather['main']['pressure']
    description = weather['weather'][0]['description']
    city = weather.get('name', 'Unknown Location')  # Fallback for locations without a city name
    country = weather['sys'].get('country', '')
    timezone = weather['timezone']
    icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
    return (icon_url, temperature, description, city, country, humidity, wind_speed, pressure, timezone)

# Function to get 5-day weather forecast from OpenWeatherMap API
def get_forecast_by_city(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Error", "City not found")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def get_forecast_by_coordinates(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Error", "Coordinates not found")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def parse_forecast_data(forecast):
    daily_forecast = {}
    for entry in forecast['list']:
        date = datetime.utcfromtimestamp(entry['dt'])
        day = date.date()
        temp = entry['main']['temp'] - 273.15
        description = entry['weather'][0]['description']
        icon_id = entry['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"

        if day not in daily_forecast:
            daily_forecast[day] = {
                'min_temp': temp,
                'max_temp': temp,
                'description': description,
                'icon_url': icon_url
            }
        else:
            daily_forecast[day]['min_temp'] = min(daily_forecast[day]['min_temp'], temp)
            daily_forecast[day]['max_temp'] = max(daily_forecast[day]['max_temp'], temp)

    sorted_daily_forecast = sorted(daily_forecast.items())
    return sorted_daily_forecast[:5]

# Function to send forecast email
def send_email():
    if email_var.get():
        try:
            from_email = EMAIL_USER
            from_password = EMAIL_PASS
            to_email = email_entry.get()

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = "Previsão do Tempo para a Semana"

            body = "Aqui está a previsão do tempo para a semana:\n\n"
            for day, data in forecast_data:
                day_str = day.strftime('%A')
                min_temp = data['min_temp']
                max_temp = data['max_temp']
                description = data['description']
                body += f"{day_str}: {min_temp:.1f}°C - {max_temp:.1f}°C, {description}\n"

            # Adicionando alertas de desastres naturais, se houver
            if alert_label.cget('text') != "Sem alertas de desastres naturais.":
                body += "\n\nAlerta de desastres naturais:\n"
                body += alert_label.cget('text')

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login(from_email, from_password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()

            messagebox.showinfo("Successo", "Email enviado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar o email: {e}")

# Function to check for weather alerts
def check_for_alerts(temperature, pressure, humidity, wind_speed):
    alert_messages = []

    if wind_speed > 33.5 and pressure < 980:
        alert_messages.append("Condições favoráveis para furacões.")
    if wind_speed > 11.2 and pressure < 1050:
        alert_messages.append("Condições favoráveis para tornados.")
    if humidity > 80 and temperature > 24:
        alert_messages.append("Condições favoráveis para inundações.")

    if alert_messages:
        alert_message = "\n".join(alert_messages)
        alert_label.configure(text=alert_message, fg="red")
    else:
        alert_label.configure(text="Sem alertas de desastres naturais.", fg="green")

# Function to search for weather and update UI
def search():
    global forecast_data
    city = city_entry.get()
    lat = lat_entry.get()
    lon = lon_entry.get()

    weather = None
    forecast = None

    if city:
        weather = get_weather_by_city(city)
        forecast = get_forecast_by_city(city)
    elif lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
            weather = get_weather_by_coordinates(lat, lon)
            forecast = get_forecast_by_coordinates(lat, lon)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric coordinates.")
            return
    else:
        messagebox.showerror("Error", "Please enter a city name or coordinates.")
        return

    if weather is None or forecast is None:
        return

    result = parse_weather_data(weather)
    icon_url, temperature, description, city, country, humidity, wind_speed, pressure, timezone = result
    local_time = datetime.utcnow() + timedelta(seconds=timezone)
    local_time_str = local_time.strftime('%H:%M:%S')

    location_label.configure(text=f"{city}, {country}")
    temperature_label.configure(text=f"Temperatura: {temperature:.2f}°C")
    humidity_label.configure(text=f"Umidade: {humidity}%")
    wind_speed_label.configure(text=f"Velocidade do vento: {wind_speed} m/s")
    pressure_label.configure(text=f"Pressão: {pressure} hPa")
    description_label.configure(text=f"Descrição: {description.capitalize()}")
    timecity_label.configure(text=f"Hora local: {local_time_str}")

    image = Image.open(requests.get(icon_url, stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    icon_label.configure(image=icon)
    icon_label.image = icon

    check_for_alerts(temperature, pressure, humidity, wind_speed)

    forecast_data = parse_forecast_data(forecast)
    for i in range(5):
        day, data = forecast_data[i]
        min_temp = data['min_temp']
        max_temp = data['max_temp']
        description = data['description']
        icon_url = data['icon_url']
        forecast_labels[i][0].configure(text=day.strftime('%A'))
        forecast_labels[i][1].configure(text=f"{min_temp:.1f}° / {max_temp:.1f}°")
        forecast_labels[i][2].configure(text=description.capitalize())
        forecast_image = Image.open(requests.get(icon_url, stream=True).raw)
        forecast_icon = ImageTk.PhotoImage(forecast_image)
        forecast_labels[i][3].configure(image=forecast_icon)
        forecast_labels[i][3].image = forecast_icon

    email_check.pack(pady=10)
    email_frame.pack(pady=10)
    send_email_button.pack(pady=10)

def exit_fullscreen(event=None):
    app.attributes('-fullscreen', False)

def add_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)
    entry.bind("<FocusIn>", lambda event: on_focus_in(event, placeholder_text))
    entry.bind("<FocusOut>", lambda event: on_focus_out(event, placeholder_text))

def on_focus_in(event, placeholder_text):
    entry = event.widget
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.config(foreground='black')

def on_focus_out(event, placeholder_text):
    entry = event.widget
    if entry.get() == "":
        entry.insert(0, placeholder_text)
        entry.config(foreground='grey')

app = ttk.Window(themename="morph")
app.title("APLICAÇÃO METEOROLÓGICA")
app.geometry("1500x700")

# Set the window to full screen
app.attributes('-fullscreen', True)
app.bind("<Escape>", exit_fullscreen)

city_entry = ttk.Entry(app, font="Helvetica, 18")
city_entry.pack(pady=10)
add_placeholder(city_entry, "Nome da Cidade")

lat_entry = ttk.Entry(app, font="Helvetica, 18")
lat_entry.pack(pady=10)
add_placeholder(lat_entry, "Latitude")

lon_entry = ttk.Entry(app, font="Helvetica, 18")
lon_entry.pack(pady=10)
add_placeholder(lon_entry, "Longitude")

search_button = ttk.Button(app, text="Pesquisar", command=search, bootstyle="warning")
search_button.pack(pady=10)

location_label = tk.Label(app, font="Helvetica, 25")
location_label.pack(pady=20, anchor="w", padx=30)
icon_label = tk.Label(app)
icon_label.pack(anchor="w", padx=30)
temperature_label = tk.Label(app, font="Helvetica, 20")
temperature_label.pack(anchor="w", padx=30)
description_label = tk.Label(app, font="Helvetica, 20")
description_label.pack(anchor="w", padx=30)
humidity_label = tk.Label(app, font="Helvetica, 20")
humidity_label.pack(anchor="w", padx=30)
wind_speed_label = tk.Label(app, font="Helvetica, 20")
wind_speed_label.pack(anchor="w", padx=30)
pressure_label = tk.Label(app, font="Helvetica, 20")
pressure_label.pack(anchor="w", padx=30)
timecity_label = tk.Label(app, font="Helvetica, 20")
timecity_label.pack(anchor="w", padx=30)

alert_label = tk.Label(app, font="Helvetica, 20")
alert_label.pack(anchor="w", padx=30, pady=10)

email_var = tk.BooleanVar()
email_check = ttk.Checkbutton(app, text="Receber previsões por email", variable=email_var, bootstyle="success")

email_frame = tk.Frame(app)
email_label = ttk.Label(email_frame, text="Endereço de email:")
email_label.pack(side="left", padx=(0, 10))
email_entry = ttk.Entry(email_frame, font="Helvetica, 18")
email_entry.pack(side="left")

send_email_button = ttk.Button(app, text="Enviar Email", command=send_email, bootstyle="info")

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
