import JustIRC
import random

bot = JustIRC.IRCConnection()

greetings = [
    "Hello {}!",
    "Hi {}!",
    "Hello there {}!",
    "Hi there {}!",
    "Hey {}!"
]

def on_connect(bot):
    bot.set_nick("HelloBot")
    bot.send_user_packet("HelloBot")

def on_welcome(bot):
    bot.join_channel("#HelloBotTest")

def on_message(bot, channel, sender, message):
    if "hi" in message.lower() or "hello" in message.lower():
        greeting_message = random.choice(greetings).format(sender)
        bot.send_message(channel, greeting_message)

bot.on_connect.append(on_connect)
bot.on_welcome.append(on_welcome)
bot.on_public_message.append(on_message)

bot.connect("irc.freenode.net")
bot.run_loop()
