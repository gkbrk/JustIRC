import JustIRC

bot = JustIRC.IRCConnection()

@bot.on("connect")
def connect(e):
    bot.set_nick("leo1234")
    bot.send_user_packet("leo1234")

@bot.on("welcome")
def welcome(e):
    bot.join_channel("#elitewarez")

@bot.on("message#")
def msg(e):
    print("[MSG]", e)

bot.connect("irc.rizon.net")
bot.run_loop()
    
