import socket
from collections import defaultdict
from collections import namedtuple


_IRCPacket = namedtuple("IRCPacket", "prefix command arguments")


def _parse_irc_packet(packet):
    prefix = ""
    command = ""
    arguments = []

    if packet.startswith(":"):
        prefix = packet[1:].split(" ")[0]
        packet = packet.split(" ", 1)[1]

    if " " in packet:
        if " :" in packet:
            last_argument = packet.split(" :")[1]
            packet = packet.split(" :")[0]
            for splitted in packet.split(" "):
                if not command:
                    command = splitted
                else:
                    arguments.append(splitted)
            arguments.append(last_argument)
        else:
            for splitted in packet.split(" "):
                if not command:
                    command = splitted
                else:
                    arguments.append(splitted)
    else:
        command = packet

    return _IRCPacket(prefix, command, arguments)


_IRCPacket.parse = _parse_irc_packet


class EventEmitter:
    def __init__(self):
        self.handlers = defaultdict(lambda: [])

    def add_listener(self, name, handler):
        self.handlers[name].append(handler)

    def remove_listener(self, name, handler):
        self.handlers[name].remove(handler)

    def emit(self, name, data=None):
        """Emit an event

        This function emits an event to all listeners registered to it.

        Parameters
        ----------
        name : str
            Event name. Case sensitive.
        data
            Event data. Can be any type and passed directly to the event
            handlers.

        """
        for handler in list(self.handlers[name]):
            handler(data)

    def on(self, name):
        """
        Decorate a function as an event handler.

        Parameters
        ----------
        name : str
            The event name to handle
        """

        def inner(func):
            self.add_listener(name, func)
            return func

        return inner


# Event data types
_IRCEvent = namedtuple("IRCEvent", "bot")
_PacketEvent = namedtuple("PacketEvent", "bot packet")
_MessageEvent = namedtuple("MessageEvent", "bot channel sender message")
_JoinEvent = namedtuple("JoinEvent", "bot channel nick")
_PartEvent = namedtuple("PartEvent", "bot channel nick")


class IRCConnection(EventEmitter):
    def __init__(self):
        """Create an IRC connection

        After creating the object and adding all the event handlers, you need to
        call .connect on it to actually connect to a server.

        """
        super().__init__()
        self.socket = None

        self.nick = ""

    def run_once(self):
        """Run one iteration of the IRC client.

        This function is called in a loop by the run_loop function. It can be
        called separately, but most of the time there is no need to do this.

        """

        line = next(self.lines)
        packet = _IRCPacket.parse(line)
        sender = packet.prefix.split("!")[0]

        ev = _PacketEvent(self, packet)
        self.emit("packet", ev)
        self.emit(f"packet_{packet.command}", ev)

        if packet.command == "PRIVMSG":
            channel = packet.arguments[0]
            message = packet.arguments[1]
            ev = _MessageEvent(self, channel, sender, message)
            self.emit("message", ev)
            self.emit(f"message_{channel}", ev)
            self.emit(f"message_{sender}", ev)

            if channel[0] == "#":
                self.emit("message#", ev)
            else:
                self.emit("pm", ev)
        elif packet.command == "PING":
            # Handle a PING message
            self.send_line("PONG :{}".format(packet.arguments[0]))
            self.emit("ping", _IRCEvent(self))
        elif packet.command == "433" or packet.command == "437":
            # Command 433 is "Nick in use"
            # Add underscore to the nick

            self.set_nick("{}_".format(self.nick))
        elif packet.command == "001":
            self.emit("welcome", _IRCEvent(self))
        elif packet.command == "JOIN":
            ev = _JoinEvent(self, packet.arguments[0], sender)
            self.emit("join", ev)
        elif packet.command == "PART":
            ev = _PartEvent(self, packet.arguments[0], sender)
            self.emit("part", ev)

    def run_loop(self):
        """Runs the main loop of the client

        This function is usually called after you add all the callbacks and
        connect to the server. It will block until the connection to the server
        is broken.

        """
        while True:
            self.run_once()

    def _read_lines(self):
        buff = ""
        while True:
            buff += self.socket.recv(1024).decode("utf-8", "replace")
            while "\n" in buff:
                line, buff = buff.split("\n", 1)
                line = line.replace("\r", "")
                yield line

    def _create_connection(self, address, keepalive=False, force_ipv4=False, source_address=None):
        # based on socket.create_connection(), with support for keepalive and force_ipv4

        host, port = address
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            sock = None

            if force_ipv4 and af != socket.AF_INET:
                print("Skipping non-ipv4 address: %s" % (sa[0]))
                continue

            print("Trying address %s..." % (sa[0]))

            try:
                sock = socket.socket(af, socktype, proto)
                if keepalive:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    if len(set(vars(socket)) & set(["TCP_KEEPIDLE", "TCP_KEEPINTVL" ,"TCP_KEEPCNT"])) == 3:
                        print("setting aggressive keepalive")
                        # - be worried after 3min of idle time
                        # - send keepalive every 15s
                        # - abort after 12 keepalives (additional 3 minutes)
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 180)
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 15)
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 12)
                if source_address:
                    sock.bind(source_address)
                sock.connect(sa)
                return sock

            except Exception as e:
                print("ERROR:  %s" % (e))
                if sock is not None:
                    sock.close()

        raise Exception("getaddrinfo has no (further) addresses to try")

    def connect(self, server, port=6667, tls=False, keepalive=True, force_ipv4=False):
        """Connects to the IRC server

        Parameters
        ----------
        server : str
            The server IP or domain to connect to
        port : int
            The server port to connect to
        tls : bool
            Enable the use of TLS
        keepalive : bool
            Explicitly enable TCP Keepalive, with short timer values
        force_ipv4 : bool
            Try IPv4 addresses only

        """

        self.socket = self._create_connection((server, port), keepalive=keepalive, force_ipv4=force_ipv4)

        if tls:
            import ssl

            context = ssl.SSLContext()
            self.socket = context.wrap_socket(self.socket, server)

        self.lines = self._read_lines()
        self.emit("connect", _IRCEvent(self))

    def send_line(self, line):
        """Sends a line directly to the server.

        This is a low-level function that can be used to implement functionality
        that's not covered by this library. Almost all of the time, you should
        have no need to use this function.

        Parameters
        ----------
        line : str
            The line to send to the server

        """
        self.socket.send(f"{line}\r\n".encode("utf-8"))

    def send_message(self, to, message):
        """Sends a message to a user or a channel

        This is the main method of interaction as an IRC bot or client. This
        function results in a PRIVMSG packet to the server.

        Parameters
        ----------
        to : str
            The target of the message
        message : str
            The message content

        """
        self.send_line(f"PRIVMSG {to} :{message}")

    def send_notice(self, to, message):
        """Send a notice message

        Notice messages usually have special formatting on clients.

        Parameters
        ----------
        to : str
            The target of the message
        message : str
            The message content

        """
        self.send_line(f"NOTICE {to} :{message}")

    def send_action_message(self, to, action):
        """Send an action message to a channel or user.

        Action messages can have special formatting on clients and are usually
        send like /me is happy

        Parameters
        ----------
        to : str
            The target of the message. Can be a channel or a user.
        action : str
            The message content

        """
        self.send_message(to, f"\x01ACTION {action}\x01")

    def join_channel(self, channel):
        """Join a channel

        This function joins a given channel. After the channel is joined, the
        "join" event is emitted with your nick.

        Parameters
        ----------
        channel : str
            The channel to join

        """
        self.send_line(f"JOIN {channel}")

    def set_nick(self, nick):
        """Sets or changes your nick

        This should be called before joining channels, but can be called at any
        time afterwards. If the requested nick is not available, the library
        will keep adding underscores until an available nick is found.

        Parameters
        ----------
        nick : str
            The nickname to use

        """
        self.nick = nick
        self.send_line(f"NICK {nick}")

    def send_user_packet(self, username):
        """Send a user packet

        This should be sent after your nickname. It is displayed on the clients
        when they view your details and look at "Real Name".

        Parameters
        ----------
        username : str
            The name to set

        """
        self.send_line(f"USER {username} 0 * :{username}")
