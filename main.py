import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from PIL import Image, ImageTk
import ttkbootstrap as ttkb
from datetime import datetime, timedelta
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import sqlite3
import matplotlib.pyplot as plt

# Environment Variables
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', '1b2f8c4cbcbd0ee0ce628c4130e28dc2')
EMAIL_USER = os.getenv('EMAIL_USER', 'ClimaAlert@outlook.pt') #Put your email
EMAIL_PASS = os.getenv('EMAIL_PASS', 'Alertaclimatica1234') #Put your password

def create_db():
    with sqlite3.connect('weather_data.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY,
                city TEXT,
                country TEXT,
                temperature REAL,
                description TEXT,
                humidity INTEGER,
                wind_speed REAL,
                pressure INTEGER,
                precipitation REAL,
                date TIMESTAMP
            )
        ''')
        conn.commit()

def convert_to_local_time(utc_time, timezone_offset):
    return utc_time + timedelta(seconds=timezone_offset)

def save_to_db(city, country, temperature, description, humidity, wind_speed, pressure, precipitation, timezone_offset):
    utc_time = datetime.utcnow()
    local_time = convert_to_local_time(utc_time, timezone_offset)
    with sqlite3.connect('weather_data.db') as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO weather_history (city, country, temperature, description, humidity, wind_speed, pressure, precipitation, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (city, country, temperature, description, humidity, wind_speed, pressure, precipitation, local_time))
        conn.commit()

def get_icon(icon_id):
    try:
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        response = requests.get(icon_url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error fetching icon {icon_id}: {e}")
        return None

def get_weather_by_city(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Erro", "Cidade não encontrada")
        return None
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        return None

def get_weather_by_coordinates(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Erro", "Coordenadas não encontradas")
        return None
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        return None

def parse_weather_data(weather):
    if not weather:
        return None
    icon_id = weather['weather'][0]['icon']
    temperature = weather['main']['temp'] - 273.15
    humidity = weather['main']['humidity']
    wind_speed = weather['wind']['speed']
    pressure = weather['main']['pressure']
    description = weather['weather'][0]['description']
    precipitation = weather.get('rain', {}).get('1h', 0) or weather.get('snow', {}).get('1h', 0)
    city = weather.get('name', 'Localização Desconhecida')
    country = weather['sys'].get('country', '')
    timezone_offset = weather['timezone']
    icon = get_icon(icon_id)
    return (icon, temperature, description, city, country, humidity, wind_speed, pressure, precipitation, timezone_offset)

def get_forecast_by_city(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Erro", "Cidade não encontrada")
        return None
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        return None

def get_forecast_by_coordinates(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Erro", "Coordenadas não encontradas")
        return None
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        return None

def parse_forecast_data(forecast):
    if not forecast:
        return None
    daily_forecast = {}
    for entry in forecast['list']:
        date = datetime.utcfromtimestamp(entry['dt'])
        day = date.date()
        temp = entry['main']['temp'] - 273.15
        description = entry['weather'][0]['description']
        icon_id = entry['weather'][0]['icon']
        icon = get_icon(icon_id)

        if day not in daily_forecast:
            daily_forecast[day] = {
                'min_temp': temp,
                'max_temp': temp,
                'description': description,
                'icon': icon
            }
        else:
            daily_forecast[day]['min_temp'] = min(daily_forecast[day]['min_temp'], temp)
            daily_forecast[day]['max_temp'] = max(daily_forecast[day]['max_temp'], temp)

    sorted_daily_forecast = sorted(daily_forecast.items())
    next_day_forecast = [item for item in sorted_daily_forecast if item[0] > datetime.utcnow().date()]
    return next_day_forecast[:5]

def send_critical_alert_email(alert_message):
    try:
        from_email = EMAIL_USER
        from_password = EMAIL_PASS
        to_email = email_entry.get()

        # Define um assunto chamativo com base no alerta
        subject = "⚠️ ALERTA CRÍTICO: Desastre Natural Imediato ⚠️"

        if "furacões" in alert_message.lower():
            subject = "🌪️ ALERTA CRÍTICO: Condições Favoráveis para Furacões 🌪️"
        elif "tornados" in alert_message.lower():
            subject = "🌪️ ALERTA CRÍTICO: Condições Favoráveis para Tornados 🌪️"
        elif "inundações" in alert_message.lower():
            subject = "🌧️ ALERTA CRÍTICO: Condições Favoráveis para Inundações 🌧️"
        elif "tempestades severas" in alert_message.lower():
            subject = "⛈️ ALERTA CRÍTICO: Condições Favoráveis para Tempestades Severas ⛈️"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        body = f"Alerta Crítico:\n\n{alert_message}\n\nFique seguro e tome as devidas precauções."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()

        messagebox.showinfo("Sucesso", "Email de alerta crítico enviado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao enviar o email de alerta crítico: {e}")

def check_for_alerts(temperature, pressure, humidity, wind_speed, precipitation):
    alert_messages = []

    # Furacões
    if wind_speed > 33.5 and pressure < 980 and humidity > 75 and temperature > 26:
        alert_messages.append("Condições favoráveis para furacões.")
    
    # Tornados (ajustado)
    if wind_speed > 20.0 and pressure < 1000 and humidity > 70:
        alert_messages.append("Condições favoráveis para tornados.")
    
    # Inundações (atualizado)
    if humidity > 80 and temperature > 24 and precipitation > 10:
        alert_messages.append("Condições favoráveis para inundações.")
    
    # Tempestades Severas
    if wind_speed > 25 and precipitation > 15:
        alert_messages.append("Condições favoráveis para tempestades severas.")

    if alert_messages:
        alert_message = "\n".join(alert_messages)
        alert_label.configure(text=alert_message, fg="red")
        if email_var.get() and email_entry.get():
            send_critical_alert_email(alert_message)
    else:
        alert_label.configure(text="Sem alertas de desastres naturais.", fg="green")

def send_email():
    if email_var.get():
        try:
            from_email = EMAIL_USER
            from_password = EMAIL_PASS
            to_email = email_entry.get()

            # Default subject
            subject = "Previsão do Tempo para os próximos 5 dias"
            alert_text = alert_label.cget('text')

            # Check if there are critical alerts
            if alert_text != "Sem alertas de desastres naturais.":
                if "furacões" in alert_text.lower():
                    subject = "🌪️ ALERTA CRÍTICO: Condições Favoráveis para Furacões 🌪️"
                elif "tornados" in alert_text.lower():
                    subject = "🌪️ ALERTA CRÍTICO: Condições Favoráveis para Tornados 🌪️"
                elif "inundações" in alert_text.lower():
                    subject = "🌧️ ALERTA CRÍTICO: Condições Favoráveis para Inundações 🌧️"
                elif "tempestades severas" in alert_text.lower():
                    subject = "⛈️ ALERTA CRÍTICO: Condições Favoráveis para Tempestades Severas ⛈️"

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            city = city_entry.get()

            body = f"Aqui está a previsão do tempo de para os próximos 5 dias:\n\n"
            for day, data in forecast_data:
                day_str = day.strftime('%A')
                min_temp = data['min_temp']
                max_temp = data['max_temp']
                description = data['description']
                body += f"{day_str}: {min_temp:.1f}°C - {max_temp:.1f}°C, {description}\n"

            if alert_text != "Sem alertas de desastres naturais.":
                body += "\n\nAlerta de desastres naturais:\n"
                body += alert_text

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login(from_email, from_password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()

            messagebox.showinfo("Sucesso", "Email enviado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar o email: {e}")

def get_hourly_forecast_by_city(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Erro", "Cidade não encontrada")
        return None
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        return None

def get_hourly_forecast_by_coordinates(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.HTTPError:
        messagebox.showerror("Erro", "Coordenadas não encontradas")
        return None
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        return None

def plot_hourly_forecast(forecast):
    hours = []
    temps = []
    rain = []
    clouds = []
    wind_speed = []
    descriptions = []

    for entry in forecast['list'][:8]:
        dt = datetime.utcfromtimestamp(entry['dt'])
        hours.append(dt.strftime('%H:%M'))
        temps.append(entry['main']['temp'])
        rain.append(entry['rain']['3h'] if 'rain' in entry else 0)
        clouds.append(entry['clouds']['all'])
        wind_speed.append(entry['wind']['speed'])
        descriptions.append(entry['weather'][0]['description'])

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(hours, temps, 'r-', label='Temperatura (°C)')
    ax1.set_xlabel('Hora')
    ax1.set_ylabel('Temperatura (°C)', color='r')
    ax1.tick_params(axis='y', labelcolor='r')
    ax1.set_ylim([0, 30])
    
    ax2 = ax1.twinx()
    ax2.bar(hours, rain, alpha=0.3, color='b', label='Chuva (mm)')
    ax2.set_ylabel('Chuva (mm)', color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2.set_ylim([0, 10])
    
    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("axes", 1.1))
    ax3.plot(hours, clouds, 'g-', label='Nebulosidade (%)')
    ax3.set_ylabel('Nebulosidade (%)', color='g')
    ax3.tick_params(axis='y', labelcolor='g')
    ax3.set_ylim([0, 100])

    for i in range(len(hours)):
        plt.text(hours[i], temps[i], f'{temps[i]:.1f}°C\n{descriptions[i]}', ha='center', va='bottom', fontsize=8)

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax3.legend(loc='upper center')
    
    plt.subplots_adjust(right=0.853)
    plt.title('Previsão Horária')
    plt.show()

def search():
    global forecast_data
    city = city_entry.get()
    lat = lat_entry.get()
    lon = lon_entry.get()

    weather = None
    forecast = None

    if city and city.lower() != "nome da cidade":
        weather = get_weather_by_city(city)
        forecast = get_forecast_by_city(city)
    elif lat and lon and lat.lower() != "latitude" and lon.lower() != "longitude":
        try:
            lat = float(lat)
            lon = float(lon)
            weather = get_weather_by_coordinates(lat, lon)
            forecast = get_forecast_by_coordinates(lat, lon)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira coordenadas numéricas válidas.")
            return
    else:
        messagebox.showerror("Erro", "Por favor, insira o nome de uma cidade ou coordenadas.")
        return

    if not weather or not forecast:
        return

    result = parse_weather_data(weather)
    forecast_data = parse_forecast_data(forecast)
    if not result or not forecast_data:
        return

    icon, temperature, description, city, country, humidity, wind_speed, pressure, precipitation, timezone_offset = result
    save_to_db(city, country, temperature, description, humidity, wind_speed, pressure, precipitation, timezone_offset)
    update_weather_ui(result, forecast_data)
    email_options_frame.pack(pady=10)  # Ensure the email options are displayed

def update_weather_ui(result, forecast_data):
    icon, temperature, description, city, country, humidity, wind_speed, pressure, precipitation, timezone_offset = result
    local_time = datetime.utcnow() + timedelta(seconds=timezone_offset)
    local_time_str = local_time.strftime('%H:%M')

    location_label.configure(text=f"{city}, {country}")
    temperature_label.configure(text=f"Temperatura: {temperature:.1f}°C")
    humidity_label.configure(text=f"Humidade: {humidity}%")
    wind_speed_label.configure(text=f"Velocidade do vento: {wind_speed} m/s")
    pressure_label.configure(text=f"Pressão: {pressure} hPa")
    precipitation_label.configure(text=f"Precipitação: {precipitation} mm")
    description_label.configure(text=f"Descrição: {description.capitalize()}")
    timecity_label.configure(text=f"Hora local: {local_time_str}")

    if icon:
        icon_label.configure(image=icon)
        icon_label.image = icon

    check_for_alerts(temperature, pressure, humidity, wind_speed, precipitation)

    for i in range(5):
        day, data = forecast_data[i]
        min_temp = data['min_temp']
        max_temp = data['max_temp']
        description = data['description']
        icon = data['icon']

        forecast_labels[i][0].configure(text=day.strftime('%A'))
        forecast_labels[i][1].configure(text=f"{min_temp:.1f}°C - {max_temp:.1f}°C")
        forecast_labels[i][2].configure(text=description.capitalize())  # Ensure the description is displayed

        if icon:
            forecast_labels[i][3].configure(image=icon)
            forecast_labels[i][3].image = icon

def search_and_plot():
    city = city_entry.get()
    lat = lat_entry.get()
    lon = lon_entry.get()

    forecast = None

    if city and city.lower() != "nome da cidade":
        forecast = get_hourly_forecast_by_city(city)
    elif lat and lon and lat.lower() != "latitude" and lon.lower() != "longitude":
        try:
            lat = float(lat)
            lon = float(lon)
            forecast = get_hourly_forecast_by_coordinates(lat, lon)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira coordenadas numéricas válidas.")
            return
    else:
        messagebox.showerror("Erro", "Por favor, insira o nome de uma cidade ou coordenadas.")
        return

    if forecast:
        plot_hourly_forecast(forecast)

def exit_fullscreen(event=None):
    app.attributes('-fullscreen', False)

def add_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)
    entry.bind("<FocusIn>", lambda event: on_focus_in(event, placeholder_text))
    entry.bind("<FocusOut>", lambda event: on_focus_out(event, placeholder_text))
    entry.config(foreground='grey')

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

def fetch_history(start_date=None, end_date=None):
    with sqlite3.connect('weather_data.db') as conn:
        c = conn.cursor()
        query = "SELECT * FROM weather_history"
        params = []
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params.append(start_date)
            params.append(end_date)
        query += " ORDER BY date DESC"
        c.execute(query, params)
        rows = c.fetchall()
    return rows

def display_history():
    history_window = Toplevel(app)
    history_window.title("Histórico de Dados")
    history_window.geometry("1850x900")

    # Date range selection
    start_date_label = ttkb.Label(history_window, text="Data Inicial (YYYY-MM-DD):")
    start_date_label.pack(padx=10, pady=5)
    start_date_entry = ttkb.Entry(history_window)
    start_date_entry.pack(padx=10, pady=5)

    end_date_label = ttkb.Label(history_window, text="Data Final (YYYY-MM-DD):")
    end_date_label.pack(padx=10, pady=5)
    end_date_entry = ttkb.Entry(history_window)
    end_date_entry.pack(padx=10, pady=5)

    def clear_treeview():
        for item in tree.get_children():
            tree.delete(item)

    def fetch_and_display():
        clear_treeview()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        history = fetch_history(start_date, end_date)

        for row in history:
            id_, city, country, temperature, description, humidity, wind_speed, pressure, precipitation, date = row

            # Handling None values and ensuring proper formatting
            temperature_str = f"{temperature:.1f}°C" if isinstance(temperature, (float, int)) else "N/A"
            humidity_str = f"{humidity}%" if isinstance(humidity, (float, int)) else "N/A"
            wind_speed_str = f"{wind_speed:.1f} m/s" if isinstance(wind_speed, (float, int)) else "N/A"
            pressure_str = f"{pressure} hPa" if isinstance(pressure, (float, int)) else "N/A"
            precipitation_str = f"{precipitation:.1f} mm" if isinstance(precipitation, (float, int)) else "N/A"

            # Try parsing with and without microseconds
            try:
                local_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                local_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            formatted_date = local_time.strftime("%Y-%m-%d %H:%M:%S")  # Format without microseconds

            formatted_row = (
                id_, city, country, temperature_str, description, humidity_str, wind_speed_str, pressure_str, precipitation_str, formatted_date
            )
            tree.insert('', 'end', values=formatted_row)

    fetch_button = ttkb.Button(history_window, text="Buscar Histórico", command=fetch_and_display)
    fetch_button.pack(padx=10, pady=10)

    # Treeview for displaying history
    columns = ("ID", "Cidade", "País", "Temperatura", "Descrição", "Humidade", "Velocidade do Vento", "Pressão", "Precipitação", "Data")
    tree = ttk.Treeview(history_window, columns=columns, show='headings')

    # Adjusting column widths and alignment
    column_widths = {
        "ID": 30,
        "Cidade": 100,
        "País": 50,
        "Temperatura": 80,
        "Descrição": 150,
        "Humidade": 80,
        "Velocidade do Vento": 130,
        "Pressão": 80,
        "Precipitação": 100,
        "Data": 180
    }

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=column_widths[col], anchor='center')  # Adjusting the width and aligning text in the center

    tree.pack(padx=10, pady=10, fill='both', expand=True)

# Main Application Setup (previous setup code remains the same)
app = ttkb.Window(themename="morph")
app.title("APLICAÇÃO METEOROLÓGICA")
app.geometry("1800x900")  # Increased main window size

app.attributes('-fullscreen', True)
app.bind("<Escape>", exit_fullscreen)

entry_frame = tk.Frame(app)
entry_frame.pack(pady=10)

city_entry = ttkb.Entry(entry_frame, font="Helvetica, 18")
city_entry.pack(side="left", padx=10)
add_placeholder(city_entry, "Nome da Cidade")

lat_entry = ttkb.Entry(entry_frame, font="Helvetica, 18")
lat_entry.pack(side="left", padx=10)
add_placeholder(lat_entry, "Latitude")

lon_entry = ttkb.Entry(entry_frame, font="Helvetica, 18")
lon_entry.pack(side="left", padx=10)
add_placeholder(lon_entry, "Longitude")

search_button = ttkb.Button(entry_frame, text="Pesquisar", command=search, bootstyle="warning")
search_button.pack(side="left", padx=10)

plot_button = ttkb.Button(entry_frame, text="Gráfico Meteorológico", command=search_and_plot, bootstyle="primary")
plot_button.pack(side="left", padx=10)

history_button = ttkb.Button(entry_frame, text="Ver Histórico", command=display_history, bootstyle="secondary")
history_button.pack(side="left", padx=10)

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
precipitation_label = tk.Label(app, font="Helvetica, 20")
precipitation_label.pack(anchor="w", padx=30)
timecity_label = tk.Label(app, font="Helvetica, 20")
timecity_label.pack(anchor="w", padx=30)

alert_label = tk.Label(app, font="Helvetica, 20")
alert_label.pack(anchor="w", padx=30, pady=10)

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

email_options_frame = tk.Frame(app)

email_var = tk.BooleanVar()
email_check = ttkb.Checkbutton(email_options_frame, text="Receber previsões por email", variable=email_var, bootstyle="success")
email_check.pack(side="left", padx=10)

email_frame = tk.Frame(email_options_frame)
email_frame.pack(side="left")

email_label = ttkb.Label(email_frame, text="Endereço de email:")
email_label.pack(side="left", padx=(0, 10))
email_entry = ttkb.Entry(email_frame, font="Helvetica, 18")
email_entry.pack(side="left")

send_email_button = ttkb.Button(email_options_frame, text="Enviar Email", command=send_email, bootstyle="info")
send_email_button.pack(side="left", padx=10)

# Ensure the database is created
create_db()

app.mainloop()
