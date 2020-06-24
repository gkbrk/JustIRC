import socket
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

class _IRCPacket:
    def __init__(self):
        self.prefix = ""
        self.command = ""
        self.arguments = []

    def parse(self, packet):
        if packet.startswith(":"):
            self.prefix = packet[1:].split(" ")[0]
            packet = packet.split(" ", 1)[1]

        if " " in packet:
            if " :" in packet:
                last_argument = packet.split(" :")[1]
                packet = packet.split(" :")[0]
                for splitted in packet.split(" "):
                    if not self.command:
                        self.command = splitted
                    else:
                        self.arguments.append(splitted)
                self.arguments.append(last_argument)
            else:
                for splitted in packet.split(" "):
                    if not self.command:
                        self.command = splitted
                    else:
                        self.arguments.append(splitted)
        else:
            self.command = packet

class IRCConnection:
    def __init__(self):
        """Creates a new IRC Connection. You need to call .connect on it to actually
        connect to a server.

        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.nick = ""

        self.on_connect = []
        self.on_public_message = []
        self.on_private_message = []
        self.on_ping = []
        self.on_welcome = []
        self.on_packet_received = []
        self.on_join = []
        self.on_leave = []

    def run_once(self):
        """This function runs one iteration of the IRC client. This is called in a loop
        by the run_loop function. It can be called separately, but most of the
        time there is no need to do this.

        """
        packet = _parse_irc_packet(next(self.lines)) #Get next line from generator

        for event_handler in list(self.on_packet_received):
            event_handler(self, packet)

        if packet.command == "PRIVMSG":
            if packet.arguments[0].startswith("#"):
                for event_handler in list(self.on_public_message):
                    event_handler(self, packet.arguments[0], packet.prefix.split("!")[0], packet.arguments[1])
            else:
                for event_handler in list(self.on_private_message):
                    event_handler(self, packet.prefix.split("!")[0], packet.arguments[1])
        elif packet.command == "PING":
            self.send_line("PONG :{}".format(packet.arguments[0]))

            for event_handler in list(self.on_ping):
                event_handler(self)
        elif packet.command == "433" or packet.command == "437":
            #Command 433 is "Nick in use"
            #Add underscore to the nick

            self.set_nick("{}_".format(self.nick))
        elif packet.command == "001":
            for event_handler in list(self.on_welcome):
                event_handler(self)
        elif packet.command == "JOIN":
            for event_handler in list(self.on_join):
                event_handler(self, packet.arguments[0], packet.prefix.split("!")[0])
        elif packet.command == "PART":
            for event_handler in list(self.on_leave):
                event_handler(self, packet.arguments[0], packet.prefix.split("!")[0])

    def run_loop(self):
        """Runs the main loop of the client. This function is usually called after you
        add all the callbacks and connect to the server.

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

    def connect(self, server, port=6667, tls=False):
        """Connects to the IRC server

        Parameters
        ----------
        server : str
            The server IP or domain to connect to
        port : int
            The server port to connect to
        tls : bool
            Enable the use of TLS

        """

        self.socket = socket.create_connection((server, port))

        if tls:
            import ssl

            context = ssl.SSLContext()
            self.socket = context.wrap_socket(self.socket, server)

        self.lines = self._read_lines()
        for event_handler in list(self.on_connect):
            event_handler(self)

    def send_line(self, line):
        """Sends a line directly to the server. This is a low-level function that can be
        used to implement functionality that's not covered by this
        library. Almost all of the time, you should have no need to use this
        function.

        """
        self.socket.send("{}\r\n".format(line).encode("utf-8"))

    def send_message(self, to, message):
        """Sends a message to a user or a channel. This is the main way of interaction
        as an IRC bot or client.

        """
        self.send_line("PRIVMSG {} :{}".format(to, message))

    def send_notice(self, to, message):
        """Sends a notice message. Notice messages ususally have special formatting on
        clients.

        """
        self.send_line("NOTICE {} :{}".format(to, message))

    def send_action_message(self, to, action):
        """Sends an action message to a channel or user. Action messages have special
        formatting on clients and are usually sent like /me is happy

        """
        self.send_message(to, "\x01ACTION {}\x01".format(action))

    def join_channel(self, channel_name):
        """Joins a given channel. After the channel is joined, the on_join callback is
        called.

        """
        self.send_line("JOIN {}".format(channel_name))

    def set_nick(self, nick):
        """Sets or changes your link. This should be called before joining channels, but
        can be called at any time afterwards. If the requested nickname is not
        available, the library will keep adding an underscore until a suitable
        nick is found.

        """
        self.nick = nick
        self.send_line("NICK {}".format(nick))

    def send_user_packet(self, username):
        """Sends a user packet. This should be sent after your nickname. It is
        displayed on clients when they view your details and look at "Real
        Name".

        """
        self.send_line("USER {} 0 * :{}".format(username, username))
