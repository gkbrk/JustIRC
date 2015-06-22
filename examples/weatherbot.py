import JustIRC
import requests

bot = JustIRC.IRCConnection()

def on_connect(bot):
    bot.set_nick("WeatherBot")
    bot.send_user_packet("WeatherBot")

def on_welcome(bot):
    bot.join_channel("#WeatherBotTest")

def on_message(bot, channel, sender, message):
    if len(message.split()) == 0:
        message = "." #For people who try to crash bots with just spaces

    if message.split()[0] == "!weather":
        if len(message.split()) > 1:
            weather_data = requests.get("http://api.openweathermap.org/data/2.5/weather", params={"q": message.split(" ", 1), "units": "metric"}).json()
            if weather_data["cod"] == 200:
                bot.send_message(channel, "The weather in {} is {} and {} degrees.".format(weather_data["name"], weather_data["weather"][0]["description"], weather_data["main"]["temp"]))
        else:
            bot.send_message(channel, "Usage: !weather Istanbul")
    elif message.split()[0] == "!test":
        bot.send_message(channel, "Test successful!")

bot.on_connect.append(on_connect)
bot.on_welcome.append(on_welcome)
bot.on_public_message.append(on_message)

bot.connect("irc.freenode.net")
bot.run_loop()
