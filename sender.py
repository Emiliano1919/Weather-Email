import requests
from email.message import EmailMessage
import smtplib
import datetime
from dotenv import load_dotenv
import os

load_dotenv() 

SENDER = os.getenv("SENDER")
RECEIVER = os.getenv("RECEIVER")
LOG =os.getenv("LOG")


# Fetch current weather, hourly rain probability, and daily temperature
def get_weather_and_rain_forecast(latitude, longitude):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=precipitation_probability,apparent_temperature,temperature_2m&daily=apparent_temperature_max,apparent_temperature_min,temperature_2m_max,temperature_2m_min&current_weather=true&timezone=auto"

    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    current_temp = weather_data['current_weather']['temperature']

    daily_data = weather_data['daily']
    min_temp = daily_data['apparent_temperature_min'][0]  # First entry corresponds to today
    max_temp = daily_data['apparent_temperature_max'][0]  

    hourly_data = weather_data['hourly']
    rain_probabilities = hourly_data['precipitation_probability']
    time_data = hourly_data['time']

    # Filter rain probabilities for the current day only
    today = datetime.date.today().isoformat()
    hourly_rain_today = {time: prob for time, prob in zip(time_data, rain_probabilities) if today in time}

    return current_temp,min_temp, max_temp, hourly_rain_today


def send_email(body,current_time):
    msg = EmailMessage()
    msg['Subject'] = f'{current_time} Weather and Rain Forecast'
    me = SENDER
    to = RECEIVER
    password = LOG
    msg['From'] = me
    msg['To'] = to
    msg.set_content(body)


    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(me, password)  
        server.sendmail(me, to, msg.as_string())

# Main function
def main():
    # Latitude and longitude for Ottawa
    latitude = 45.4112
    longitude = -75.6981

    current_temp,min_temp, max_temp, hourly_rain_today = get_weather_and_rain_forecast(latitude, longitude)

    now = datetime.datetime.now()
    current_time = now.strftime("%A, %B %d, %Y %I:%M %p") 

    weather_info = f"Good morning :)\n"
    weather_info += f"Current Date and Time: {current_time}\n"
    weather_info += f"Current Temperature: {current_temp} °C\n"
    weather_info += f"Perceived Minimum Temperature Today: {min_temp}°C\n"
    weather_info += f"Perceived Maximum Temperature Today. {max_temp}°C\n"
    weather_info += "Hourly Rain Probabilities for Today:\n"

    # Display the hourly rain probability for today (only showing hours)
    for time, rain_prob in hourly_rain_today.items():
        hour = time.split("T")[1][:2]  # Extract the hour part (HH from HH:MM:SS)
        weather_info += f"{hour}:00: {rain_prob}% chance of rain\n"
    send_email(weather_info,current_time)

# Call the main function
if __name__ == "__main__":
    main()
