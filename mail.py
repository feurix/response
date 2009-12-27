# -*- coding: utf-8 -*-

'''Response Project - E-Mail Message Handling'''

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

import email.message
import email.feedparser


# RFC 2822
# Silently discard data (message payload) after we've matched this
# line. We are only interesed in message headers :-)
HEADER_BODY_SEPARATOR = '\r\n'


class Message(email.message.Message):

    def __init__(self):
        email.message.Message.__init__(self)
        self._unixto = None

    def set_unixto(self, address):
        self._unixto = address

    def get_unixto(self):
        return self._unixto


class BufferedInput(email.feedparser.BufferedSubFile):

    def __init__(self):
        email.feedparser.BufferedSubFile.__init__(self)
        self.headers_complete = False

    def push(self, data):
        data, self._partial = self._partial + data, ''
        parts = email.feedparser.NLCRE_crack.split(data)
        self._partial = parts.pop()
        lines = []
        for i in range(len(parts) // 2):
            line = parts[i*2]
            eol = parts[i*2+1]
            if not line:
                self.headers_complete = True
                self._partial = ''
                break
            lines.append(line + eol)
        self.pushlines(lines)


class Parser(object, email.feedparser.FeedParser):

    def __init__(self, _factory=Message):
        self._factory = _factory
        self._input = BufferedInput()
        self._msgstack = []
        self._parse = self._parsegen().next
        self._cur = None
        self._last = None
        self._headersonly = False

    def feed(self, data):
        if not self._input.headers_complete:
            self._input.push(data)
            self._call_parse()

