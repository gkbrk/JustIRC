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

@bot.on("connect")
def connect(e):
    bot.set_nick("ghast")
    bot.send_user_packet("HelloBot")

@bot.on("welcome")
def welcome(e):
    bot.join_channel("#HelloBotTest")

@bot.on("message")
def message(e):
    msg = e.message.lower()
    if "hi" in msg or "hello" in msg:
        greeting = random.choice(greetings).format(e.sender)
        bot.send_message(e.channel, greeting)

@bot.on("packet")
def dbg(e):
    print(e.packet)

bot.connect("irc.freenode.net")
bot.run_loop()
