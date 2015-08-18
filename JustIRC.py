import socket
import time

def parse_irc_packet(packet):
    irc_packet = IRCPacket()
    irc_packet.parse(packet)
    return irc_packet

class IRCPacket:
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
        packet = parse_irc_packet(next(self.lines)) #Get next line from generator

        for event_handler in list(self.on_packet_received):
            event_handler(self, packet)

        if packet.command == "PRIVMSG":
            if packet.arguments[0].startswith("#"):
                for event_handler in list(self.on_public_message):
                    event_handler(self, packet.arguments[0], packet.prefix.split("!")[0], packet.arguments[1])
            else:
                for event_handler in list(self.on_private_message):
                    event_handler(self, packet.arguments[0], packet.arguments[1])
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
        while True:
            self.run_once()

    def read_lines(self):
        buff = ""
        while True:
            buff += self.socket.recv(1024).decode("utf-8", "replace")
            while "\n" in buff:
                line, buff = buff.split("\n", 1)
                line = line.replace("\r", "")
                yield line

    def connect(self, server, port=6667):
        self.socket.connect((server, port))
        self.lines = self.read_lines()
        for event_handler in list(self.on_connect):
            event_handler(self)

    def send_line(self, line):
        self.socket.send("{}\r\n".format(line).encode("utf-8"))

    def send_message(self, to, message):
        self.send_line("PRIVMSG {} :{}".format(to, message))

    def send_action_message(self, to, action):
        self.send_message(to, "\x01ACTION {}\x01".format(action))

    def join_channel(self, channel_name):
        self.send_line("JOIN {}".format(channel_name))

    def set_nick(self, nick):
        self.nick = nick
        self.send_line("NICK {}".format(nick))

    def send_user_packet(self, username):
        self.send_line("USER {} 0 * :{}".format(username, username))
