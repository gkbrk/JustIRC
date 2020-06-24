JustIRC is a Python IRC library that can be used to create IRC bots and
clients. It is an event-based library, you can read more about which events are
available from the Events page.

The library recently had a major version update, which changed the API. If you
don't want to migrate your code to the new API, please use version `0.3`.

Quick Start
===========

Before going into detail on how the library works, here's a quick example to see
how to use it::

  import JustIRC

  bot = JustIRC.IRCConnection()

  @bot.on("connect")
  def connect(e):
    bot.set_nick("TestBot")
    bot.send_user_packet("TestBot")

  @bot.on("welcome")
  def welcome(e):
    bot.join_channel("#HelloBotTest")

  @bot.on("message")
  def message(e):
    message = e.message.lower()
    if "hello" in message:
      message = f"Hello, {e.sender}"
      bot.send_message(e.channel, message)

  bot.connect("irc.freenode.net")
  bot.run_loop()


Event Emitter
=============

JustIRC contains a simple Event Emitter. It provides a mechanism to listen and
emit arbitrary events. This is useful for building clients that react to
incoming messages, such as bots.

The design of the event system is similar to those found in web browsers or JS
runtimes, so it should be familiar to JS developers.

Emitting events
---------------

In order to emit events, you can call the _emit_ method on an EventEmitter
instance. Here's an example::

  emitter.emit("lucky-number", random.randint(1, 100))

For real-life use cases, the event data will probably be an object with multiple
properties instead of a single number.

The library uses this mechanism to emit events for IRC messages, but your bot
can emit custom events for its own behaviour.

If there are no listeners for an event, it doesn't consume resources.

Handling events with decorators
-------------------------------

The easiest way to handle an event is by putting a decorator on a handler
function. Let's make a handler for the `lucky-number` event above. ::

  @emitter.on("lucky-number")
  def number_handler(num):
    print("Your lucky number is", num)

Events
======

JustIRC emits certain events regularly. Below is a list of them. Some other
events are emitted too, but they are not listed below since they are not
guaranteed to be kept around.

'connected'
-----------

This event is emitted when the client connects to the server.

'welcome'
---------

After the client connects to the server and receives the welcome message, the
'welcome' event is emitted.

'message'
---------

This event is emitted when a message is received. It does not discriminate
between private messages and channel messages.

The event data includes

- sender (str): The nickname of the sender.
- channel (str): The channel that the message was sent to
- message (str): The message contents

'message#'
----------

This event is only emitted for messages sent to a channel. The event data is the
same as the message event.

'pm'
----

This is emitted for private messages. The event data is the same as the message
event.

'ping'
------

Every time the client receives a PING from the server, a ping event is
emitted. There is no need to handle this explicitly, as the library replies to
pings automatically.

'packet'
--------

On every received packet, a 'packet' event is emitted. This is generally not
very useful to simple bots. It can be used for debugging, or for implementing
functionality that's not part of JustIRC.

The event data includes

- **packet:** The received packet
-  - **prefix:** Message prefix
-  - **command:** Message command
-  - **arguments:** Message arguments

Full API
======================

.. automodule:: JustIRC

.. autoclass:: EventEmitter
   :members:

.. autoclass:: IRCConnection
   :members:
