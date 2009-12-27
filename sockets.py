# -*- coding: utf-8 -*-

'''Response Project - Sockets'''

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
import exception


class Socket(object):

    def __init__(self):
        self.type = None

    def close(self):
        raise exception.NotImplemented


class UnixServerSocket(Socket):

    def __init__(self, path):
        self.type = 'UNIX'
        self.path = str(path)

    def close(self):
        os.unlink(self.path)


class TcpServerSocket(Socket):

    def __init__(self, host, port):
        self.type = 'TCP'
        self.host = str(host)
        self.port = int(port)

    def close(self):
        pass


class UnixClientSocket(Socket):

    def __init__(self, path):
        self.type = 'UNIX'
        self.path = str(path)


class TcpClientSocket(Socket):

    def __init__(self, host, port):
        self.type = 'TCP'
        self.host = str(host)
        self.port = int(port)

