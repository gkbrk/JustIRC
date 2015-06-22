import JustIRC

bot = JustIRC.IRCConnection()

def on_connect(bot):
    bot.set_nick("ParrotBotGk")
    bot.send_user_packet("ParrotBotGk")

def on_welcome(bot):
    bot.join_channel("#TestParrotBotGk")

def on_message(bot, channel, sender, message):
    bot.send_message(channel, message)


bot.on_connect.append(on_connect)
bot.on_welcome.append(on_welcome)
bot.on_public_message.append(on_message)

bot.connect("irc.freenode.net")
bot.run_loop()
