# -*- coding: utf-8 -*-

'''Response Project - Record Autoresponses'''

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

import exception

from logger import getModuleLog
log = getModuleLog(__name__)


def record_response(manager, message):
    '''Response recording / queuing:

    Given a validated message, record a new autoresponse record in the
    backend. If the record is already existing, update the timestamp of
    the last incoming message hitting this autoresponder.

    Return: True if success, False if failure'''

    # Swap sender and recipient
    sender = message.get_unixto()
    recipient = message.get_unixfrom()

    log.info('Recording response: %s -> %s' % (sender, recipient))

    try:
        manager.record_response(sender, recipient)
        log.debug('Response record successful!')
    except Exception, e:
        log.debug('Response record failed!')
        raise exception.RecordResponseError(
                'Unable to record response: %s -> %s - %s'
                % (sender, recipient, e))


def record(manager, message):
    '''Record or update an autoresponse'''

    log.debug('Adding/updating autoresponse record')

    try:
        record_response(manager, message)
    except exception.RecordError, e:
        log.info('Response record (%s -> %s) failed: %s'
                % (message.get_unixfrom(), message.get_unixto(), e))
        raise

