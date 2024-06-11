import discord
from discord.ext import commands
import requests
import datetime
import json

# Insert your OpenWeatherMap API key here
WEATHER_API_KEY = 'YOUR WEATHERMAP API KEY'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store users' default locations
user_locations = {}

# Function to fetch current weather
def get_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data.get('cod') != 200:
        error_message = data.get('message', 'Invalid location')
        return f"Invalid location: {error_message}. Please try again."
    weather = data['weather'][0]['description']
    temperature = data['main']['temp']
    return f"The current weather in {location} is {weather} with a temperature of {temperature}°C."

# Function to fetch weather forecast
def get_forecast(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data.get('cod') != 200:
        error_message = data.get('message', 'Invalid location')
        return f"Invalid location: {error_message}. Please try again."

    lat = data['coord']['lat']
    lon = data['coord']['lon']
    one_call_url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={WEATHER_API_KEY}&units=metric"
    one_call_response = requests.get(one_call_url)
    one_call_data = one_call_response.json()

    if 'daily' not in one_call_data:
        return "Could not retrieve forecast data. Please try again later."

    forecast = f"7-day forecast for {location}:\n"
    for day in one_call_data['daily']:
        date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
        weather = day['weather'][0]['description']
        temperature = day['temp']['day']
        forecast += f"{date}: {weather}, {temperature}°C\n"
    return forecast

@bot.command(name='weather')
async def weather(ctx, *, location):
    weather_info = get_weather(location)
    await ctx.send(weather_info)

@bot.command(name='forecast')
async def forecast(ctx, *, location):
    forecast_info = get_forecast(location)
    await ctx.send(forecast_info)

@bot.command(name='sethome')
async def sethome(ctx, *, location):
    user_locations[ctx.author.id] = location
    await ctx.send(f"Default location set to {location}")

@bot.command(name='homeweather')
async def homeweather(ctx):
    location = user_locations.get(ctx.author.id)
    if not location:
        await ctx.send("You haven't set a default location. Use !sethome [location] to set one.")
    else:
        weather_info = get_weather(location)
        await ctx.send(weather_info)

# Run the bot with your token
bot.run('YOUR DISCORD BOT TOKEN')
