# -*- coding: utf-8 -*-

'''Response Project - Handling Process ID files'''

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

from helpers import prepare_filepath

from logger import getModuleLog
log = getModuleLog(__name__)


PID_MIN = 2
PID_MAX = 32768 # Linux 2.6 (/proc/sys/kernel/pid_max)
                # XXX: Is there a portable way to get this value?

PID_MAX_WIDTH = len(str(PID_MAX))


class PidFile:
    '''Provide ways to read, write or delete a pid file'''

    def __init__(self, file=None):
        self._pid = None

        if file is None:
            self.file = os.path.abspath(globals.DEFAULT_PATH_PID_FILE)
        else:
            self.file = os.path.abspath(file)

        try:
            prepare_filepath(self.file, ignoreExisting=False)
        except exception.FilePathError, e:
            raise exception.PidFileError(e)

    def write(self, pid=None):
        if pid is None:
            # Default to current PID
            self._pid = os.getpid()
        else:
            if validate_pid(pid):
                self._pid = pid

        self.delete()

        log.debug('Writing pidfile %s with pid %d' % (self.file, self.pid))
        with open(self.file, 'w+') as pidfile:
            pidfile.write(str(self.pid))

    def read(self):
        with open(self.file, 'r') as pidfile:
            self._pid = int(pidfile.read(PID_MAX_WIDTH))

    def delete(self):
        if os.path.exists(self.file):
            log.debug('Deleting pidfile %s' % self.file)
            os.unlink(self.file)

    @property
    def pid(self):
        if self._pid is not None and validate_pid(self._pid):
            return int(self._pid)
        else:
            raise exception.Error('Invalid PID: %d' % self._pid)


def validate_pid(pid):
    '''Check if we've received a valid PID'''
    p = int(pid)

    if p >= PID_MIN and p <= PID_MAX:
        return True
    else:
        raise exception.Error('PID out of range %d-%d: %d'
                % (PID_MIN, PID_MAX, p))

