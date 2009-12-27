# -*- coding: utf-8 -*-

'''Response Project - Daemonizing'''

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
#
# ---
#
# Python implementation of the magic UNIX double-fork :-)
# Based on Richard Stevens' suggestions for the "proper" way of daemonizing a
# process, as laid out in his book "UNIX Network Programming: The Sockets
# Networking API" (O'Reilly).
#
# The module will ensure that all additional, TTY-bound file descriptors
# get closed. STDIN, STDOUT and STDERR are redirected to /dev/null per
# default. If STDERR's destination is given, output to it is unbuffered.
# For more details, have a look at daemonize().

from globals import __author__, __copyright__, __license__, __version__

import os
import sys
import exception

from logger import getModuleLog
log = getModuleLog(__name__)


# Initial configuration
CWD = '/'
UMASK = 0

try:
    MAXFD = os.sysconf('SC_OPEN_MAX')
except:
    MAXFD = 256

if hasattr(os, 'devnull'):
    NULL_DEVICE = os.devnull
else:
    NULL_DEVICE = '/dev/null'



# The daemonizer }:-)
def daemonize(umask=UMASK, cwd=CWD, close_fds=True, redirect=True,
        stdin=NULL_DEVICE, stdout=NULL_DEVICE, stderr=NULL_DEVICE):
    '''Convert the calling process into a daemon.

    Argument description:
        umask:      The global umask of the daemon process. (Default: %d)
        cwd:        Change working directory prior daemonizing. (Default: %s)
        close_fds:  Boolean. Close additional file descriptors? (Default: %s)
        redirect:   Boolean. Redirect file descriptors? (Default: %s)
        stdin:      Target of file descriptor 0. (Default: %s)
        stdout:     Target of file descriptor 1. (Default: %s)
        stderr:     Target of file descriptor 2. (Default: %s)
    ''' % (UMASK, CWD, True, True, NULL_DEVICE, NULL_DEVICE, NULL_DEVICE)

    global log

    try:
        # Fork #1:
        # - Create a new session
        # - Become the process group and session leader
        log.debug('Forking first child')
        pid = _fork()
        if pid != 0:
            os._exit(0)

        log.debug('Creating new session')
        os.setsid()

        # Fork #2:
        # - Drop the session leader status, thus:
        # - Ensure that the daemon never reacquires a control terminal
        log.debug('Forking second child')
        pid = _fork()
        if pid != 0:
            os._exit(0)

        log.debug('Setting umask to %d' % umask)
        os.umask(umask)

        log.debug('Changing working directory to %s' % cwd)
        os.chdir(cwd)

        if close_fds:
            log.debug('Closing additional file descriptors')
            _closeFileDescriptors()

        if redirect:
            log.debug('Redirecting standard file descriptors')
            _redirectFileDescriptors(stdin, stdout, stderr)

    except exception.DaemonError:
        raise

    except OSError, e:
        raise exception.DaemonError('Error during daemonizing: %s [%d]'
                % (e.strerror, e.errno))


# Some helpers
def _fork():
    try:
        return os.fork()
    except OSError, e:
        raise exception.DaemonError('Unable to fork(): %s [%d]'
                % (e.strerror, e.errno))


def _closeFileDescriptors():
    global log

    # Load POSIX resource information
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = MAXFD

    # Close all additional file descriptors bound to a TTY
    for fd in range(3, maxfd):
        try:
            os.ttyname(fd)
        except:
            continue

        try:
            os.close(fd)
            log.debug('Closed file descriptor %d' % fd)
        except OSError:
            pass


def _redirectFileDescriptors(stdin, stdout, stderr):
    global log

    # A final flush to the old location :-)
    sys.stdout.flush()
    sys.stderr.flush()

    # Redirect stdin, stdout and stderr (unbuffered)
    si = open(stdin, 'rb')
    so = open(stdout, 'a+b')
    se = open(stderr, 'a+b', 0)

    log.debug('Redirecting stdin from "%s"' % stdin)
    os.dup2(si.fileno(), sys.stdin.fileno())
    log.debug('Redirecting stdout to "%s"' % stdout)
    os.dup2(so.fileno(), sys.stdout.fileno())
    log.debug('Redirecting stderr to "%s"' % stderr)
    os.dup2(se.fileno(), sys.stderr.fileno())

