# JustIRC Documentation

## 1. What is JustIRC
JustIRC is an event-driven IRC library written in pure Python. It doesn't depend
on any non-standard libraries.

## 2. Hello World
Here's a simple example, before explaining the API functions. This bot will
reply to anyone who says "Hello".

```python
import JustIRC

bot = JustIRC.IRCConnection()

def on_connect(bot):
    bot.set_nick("HelloWorldBot")
    bot.send_user_packet("HelloBot")

def on_welcome(bot):
    bot.join_channel("#HelloTest")

def on_message(bot, channel, sender, message):
    if "hello" in message.lower():
        bot.send_message(channel, "Hello there {}!".format(sender))

bot.on_connect.append(on_connect)
bot.on_welcome.append(on_welcome)
bot.on_public_message.append(on_message)

bot.connect("irc.freenode.net")
bot.run_loop()
```

## 3. More examples
You can find more example code in [the examples
directory](https://github.com/gkbrk/JustIRC/examples).

## 4. The IRCConnection Class
IRCConnection is the main class of this library. It handles the connection,
parses and creates the packets and handles the events.

### 4.1 IRCConnection.set\_nick(nick)
Sets the nick of the bot. If the nick isn't available, the bot automatically
adds an underscore to it and tries again.

### 4.2 IRCConnection.send\_user\_packet(name)
Should be called after set\_nick(), it's usually fine to use the same nick for
both commands.

### 4.3 IRCConnection.join\_channel(channel\_name)
Joins a channel. Can be used to join multiple, comma-seperated channels.

### 4.4 IRCConnection.send\_message(to, message)
Used to send an IRC message. The **to** argument can be a channel name or
another nick. The message is a string.

### 4.5 IRCConnection.send\_notice(to, message)
Sends a NOTICE message. The message is a string.

### 4.6 IRCConnection.send\_action\_message(channel, action)
Sends an action message (/me) to a channel.

## 5. Events
There are multiple events that can be used for different purposes. Here's a list
of events and their descriptions.

1. on\_connect: Called after the client connects to the server.
2. on\_welcome: Called after the server sends the welcome packet.
3. on\_public\_message: Called when someone sends a message to a channel.
4. on\_private\_message: Called when someone sends a private message to the bot.
5. on\_ping: Called when the bot gets a ping packet from the server.
6. on\_join: Called when someone joins a channel.
7. on\_leave: Called when someone leaves a channel.
8. on\_packet\_received: Called when ANY packet is received. Useful for implementing custom packets.
