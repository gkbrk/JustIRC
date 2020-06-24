#!/usr/bin/env python3

import sys
sys.path.append('.')
import JustIRC

from testsimple import *

parse = JustIRC._parse_irc_packet

packet = parse('NICK leo')

ok(packet)
ok(packet.command == 'NICK')
ok(packet.arguments == ['leo'])
ok(not packet.prefix)

packet = parse('PRIVMSG #testroom :Test message')

ok(packet)
ok(packet.command == 'PRIVMSG')
ok(len(packet.arguments) == 2)
ok(packet.arguments[0] == '#testroom')
ok(packet.arguments[1] == 'Test message')
ok(not packet.prefix)

packet = parse('COMMANDONLY')

ok(packet)
ok(packet.command == 'COMMANDONLY')
ok(not packet.arguments)
ok(not packet.prefix)

packet = parse(':tepper.freenode.net 376 leo :End of /MOTD command.')

ok(packet)
ok(packet.command == '376')
ok(packet.arguments == ['leo', 'End of /MOTD command.'])
ok(packet.prefix == 'tepper.freenode.net')

done_testing()
