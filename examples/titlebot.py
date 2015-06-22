import JustIRC
import requests
import re

bot = JustIRC.IRCConnection()

def on_connect(bot):
    bot.set_nick("TitleBot")
    bot.send_user_packet("TitleBotTest")

def on_welcome(bot):
    bot.join_channel("#TitleBotTest")

def on_message(bot, channel, sender, message):
    for message_part in message.split():
        if message_part.startswith("http://") or message_part.startswith("https://"):
            html = requests.get(message_part).text
            title_match = re.search("<title>(.*?)</title>", html)
            if title_match:
                bot.send_message(channel, "Title of the URL by {}: {}".format(sender, title_match.group(1)))

bot.on_connect.append(on_connect)
bot.on_welcome.append(on_welcome)
bot.on_public_message.append(on_message)

bot.connect("irc.freenode.net")
bot.run_loop()
