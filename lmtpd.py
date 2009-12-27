# -*- coding: utf-8 -*-

'''Response Project - LMTP Daemon Implementation'''

# Copyright (C) 2009 John Feuerstein <john@feurix.com>
#
# This file is part of the response project.
#
# Response is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Response is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from globals import __author__, __copyright__, __license__, __version__

import os
import re
import sys
import socket
import asyncore
import asynchat
import time
import select
import exception

from smtpd import SMTPServer
from mail import Message, Parser
from backend import Manager
from validate import validate
from record import record

from logger import getModuleLog
log = getModuleLog(__name__)


class LMTPChannel(asynchat.async_chat):

    # State
    COMMAND = 0
    DATA = 1

    # RFC 2822
    COMMAND_TERMINATOR = '\r\n'
    DATA_TERMINATOR = '\r\n.\r\n'

    def __init__(self, server, conn, addr):
        log.debug('>>> OPEN <LMTPChannel at %#x>' % id(self))
        asynchat.async_chat.__init__(self, conn)
        self.__server = server
        self.__conn = conn
        self.__addr = addr
        self.__greeting = 0
        self.__fqdn = socket.getfqdn()
        self.__peer = conn.getpeername()

        try:
            self.__backend_manager = Manager(server.backend)
            self.__backend_manager.connect()
        except exception.DatabaseError, e:
            # We handle this later (smtp_RCPT) where the protocol
            # allows us to send the necessary status code.
            log.error('Backend failure while initializing channel: %s' % e)
        except Exception, e:
            log.error('Unhandled backend failure while initializing ' \
                      'channel: %s' % e)

        self.reset()
        self.push('220 %s %s' % (self.__fqdn, __version__))

    def reset(self):
        # Make us ready for the next message
        self.__mailfrom = None
        self.__rcptto = None
        self.__command = []
        self.__parser = Parser(Message)

        self.__state = self.COMMAND
        self.set_terminator(self.COMMAND_TERMINATOR)

    def push(self, msg):
        asynchat.async_chat.push(self, msg + self.COMMAND_TERMINATOR)

    def collect_incoming_data(self, data):
        if self.__state == self.COMMAND:
            self.__command.append(data)
        elif self.__state == self.DATA:
            self.__parser.feed(data)

    def handle_close(self):
        log.debug('<<< CLOSE <LMTPChannel at %#x>' % id(self))
        self.__backend_manager.close()
        self.close()

    def found_terminator(self):
        line = ''.join(self.__command)
        self.__command = []
        if self.__state == self.COMMAND:
            if not line:
                self.push('500 5.5.1 Error: bad syntax')
                return
            method = None
            i = line.find(' ')
            if i < 0:
                command = line.upper()
                arg = None
            else:
                command = line[:i].upper()
                arg = line[i+1:].strip()
            method = getattr(self, 'smtp_' + command, None)
            if not method:
                self.push('502 5.5.1 Error: command not implemented')
                return
            method(arg)
            return
        else:
            if self.__state != self.DATA:
                self.push('451 5.5.1 Internal server error')
                return

            # Message complete
            message = self.__parser.close()
            message.set_unixfrom(self.__mailfrom)
            message.set_unixto(self.__rcptto)

            # Notify the MTA of an error only if configured to do so
            if self.__backend_manager:
                try:
                    self.__server.process_message(
                        self.__backend_manager,
                        message,
                        )
                except exception.ProcessError, e:
                    # Note: A softfail doesn't make sense here.
                    if not self.__server.config.failsafe:
                        if self.__server.config.hardfail:
                            self.push('552 5.5.1 Error processing message')
                            return

            # Ready for the next message
            self.reset()
            self.push('250 Ok')

    #
    # Internal helpers
    #

    def __getaddr(self, keyword, arg):
        address = None
        keylen = len(keyword)
        if arg[:keylen].upper() == keyword:
            address = arg[keylen:].strip()
            if not address:
                pass
            elif address[0] == '<' and address[-1] == '>' and address != '<>':
                address = address[1:-1]
        return address

    def __parse_recipient(self, address):
        match = re.match(self.__server.config.RECIPIENT_ADDRESS_REWRITE_RE,
                address)

        if not match:
            self.push('501 5.5.2 Unknown recipient address format: %s'
                    % address)
            return

        return '%s@%s' % (match.group('user'), match.group('domain'))


    #
    # Protocol Commands
    #

    def smtp_HELO(self, arg):
        self.push('500 5.5.1 SMTP command not supported')

    def smtp_LHLO(self, arg):
        if not arg:
            self.push('501 5.5.2 Syntax: LHLO hostname')
            return

        if self.__greeting:
            self.push('503 5.5.1 Duplicate LHLO')
        else:
            self.__greeting = arg
            self.push('250 %s' % self.__fqdn)

    def smtp_NOOP(self, arg):
        self.push('250 2.0.0 Ok')

    def smtp_QUIT(self, arg):
        self.push('221 2.0.0 Bye')
        self.close_when_done()

    def smtp_MAIL(self, arg):
        address = self.__getaddr('FROM:', arg)
        if not address:
            self.push('501 5.5.4 Syntax: MAIL FROM:<address>')
            return
        if self.__mailfrom:
            self.push('503 5.5.1 Error: nested MAIL command')
            return
        self.__mailfrom = address
        self.push('250 2.1.0 Sender Ok')

    def smtp_RCPT(self, arg):
        if self.__rcptto:
            #
            # Note: We don't support mulpitle recipients per message!
            # You may send multiple messages per recipient, though.
            #
            # Hint for Postfix: response_destination_recipient_limit = 1
            #
            #   Setting this parameter to a value of 1 changes the meaning
            #   of the corresponding per-destination concurrency limit from
            #   concurrency per domain into concurrency per recipient.
            #
            self.push('503 5.5.1 Duplicate RCPT TO')
            return
        if not self.__mailfrom:
            self.push('503 5.5.1 Error: need MAIL command')
            return

        # Normalize recipient address
        address = self.__getaddr('TO:', arg)
        address = self.__parse_recipient(address)

        if not address:
            return

        # Bail out if configured to do so...
        if not self.__backend_manager and not self.__server.config.failsafe:
            if self.__server.config.hardfail:
                self.push('550 5.5.1 Backend failure')
                return
            else:
                self.push('451 4.3.1 Backend failure, try again later')
                return

        self.__rcptto = address
        self.push('250 2.1.0 Recipient OK')

    def smtp_RSET(self, arg):
        self.reset()
        self.push('250 2.0.0 Ok')

    def smtp_DATA(self, arg):
        if not self.__rcptto:
            self.push('503 5.0.1 Error: need RCPT command')
            return
        if arg:
            self.push('501 5.0.2 Syntax: DATA')
            return
        self.__state = self.DATA
        self.set_terminator(self.DATA_TERMINATOR)
        self.push('354 End data with <CR><LF>.<CR><LF>')


class LMTPServer(SMTPServer):

    @property
    def _socket(self):
        return self.config.socket

    @property
    def _socket_acl(self):
        return self.config.socket_acl

    def __init__(self, config):
        asyncore.dispatcher.__init__(self)

        self.config = config.lmtpd
        self.backend = config.backend.adapter(config.backend)

        if self._socket.type == 'TCP':
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind((self._socket.host, self._socket.port))
        elif self._socket.type == 'UNIX':
            self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind(self._socket.path)
        else:
            raise exception.ConfigError(
                    'invalid socket: %s' % self.socket)

        self.listen(5)
        log.info('Listening for network connections')

    def process_message(self, manager, message):
        log.debug('Processing message: %s -> %s' \
                % (message.get_unixfrom(), message.get_unixto()))
        try:
            validate(manager=manager, message=message)
            record(manager=manager, message=message)
        except exception.ProcessError, e:
            log.debug('Error processing message')
            raise

    def shutdown(self):
        try:
            self._socket.close()
            self.backend.close()
        except:
            pass
        log.warning('Shutting down.')

    def handle_accept(self):
        conn, addr = self.accept()
        if not addr[0] in self._socket_acl:
            log.warning('Unknown connection from %s denied.' % addr[0])
            return
        log.debug('Accepted new connection from %s' % addr[0])
        channel = LMTPChannel(self, conn, addr)

