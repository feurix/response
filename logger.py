# -*- coding: utf-8 -*-

'''Response Project - Logging'''

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

import logging
import logging.handlers

# Defaults
LOGNAME = 'response'
LOG_FORMAT_MSG = '%(asctime)s %(name)s[%(process)s]: %(message)s'
LOG_FORMAT_TIME = '%b %d %T'
LOG_FORMAT_MSG_DEBUG = '%(asctime)s %(name)s[%(process)s] ' \
        + '(%(filename)s:%(lineno)d) [%(levelname)s]: %(message)s'
LOG_FORMAT_TIME_DEBUG = '%T'
LOG_FORMAT_MSG_SYSLOG = '%(name)s[%(process)s]: %(message)s'
LOG_FORMAT_MSG_SYSLOG_DEBUG = '%(name)s[%(process)s] ' \
        + '(%(filename)s:%(lineno)d) [%(levelname)s]: %(message)s'


# Default handler used by submodules (so they may be used in other apps)
class _NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

def getLog(name=LOGNAME, debug=False, verbose=False, quiet=False,
        syslog=False, syslog_facility='MAIL', level=logging.WARNING):

    log = logging.getLogger(name)

    if syslog:
        log_format = logging.Formatter(
                LOG_FORMAT_MSG_SYSLOG_DEBUG if debug else \
                        LOG_FORMAT_MSG_SYSLOG
                )
        log_handler = logging.handlers.SysLogHandler('/dev/log',
                syslog_facility.lower())
    else:
        log_format = logging.Formatter(
                LOG_FORMAT_MSG_DEBUG if debug else LOG_FORMAT_MSG,
                LOG_FORMAT_TIME_DEBUG if debug else LOG_FORMAT_TIME,
                )
        log_handler = logging.StreamHandler()

    log_handler.setFormatter(log_format)
    log.addHandler(log_handler)

    if debug:
        log.setLevel(logging.DEBUG)
    elif verbose:
        log.setLevel(logging.INFO)
    elif quiet:
        log.setLevel(logging.ERROR)
    else:
        log.setLevel(level)

    return log

def getModuleLog(module):
    log = logging.getLogger('%s.%s' % (LOGNAME, module))
    log.addHandler(_NullLogHandler())
    return log

def getLogLevel(log):
    return log.getEffectiveLevel()

def getLogLevelName(log):
    return logging.getLevelName(getLogLevel(log))

