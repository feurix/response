# -*- coding: utf-8 -*-

'''Response Project - Header Validation'''

# Copyright (C) 2009 John Feuerstein <john@feurix.com>
#
# This file is part of the response project.
#
# Repsonse is free software; you can redistribute it and/or modify
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
log = getModuleLog('validate')


def validate_headers(message):
    '''Header validation:

    Given a parsed message object, validate if this message may trigger
    an autoresponse.

    Return: True if yes, False if not'''

    log.debug('Validating headers')

    # TODO
    result = True

    if result:
        log.debug('Header validation successful!')
    else:
        log.debug('Header validation failed!')
        raise exception.InvalidHeaderError('Invalid header found!')

    return result


def validate_recipient(manager, message):
    '''Recipient validation:

    Given a parsed message object, validate if the local recipient has
    configured and enabled an auto-response.

    Return: True if yes, False if not'''

    recipient = message.get_unixto()

    log.debug('Validating recipient: %s' % recipient)

    try:
        manager.validate_recipient(recipient)
        log.debug('Recipient validation successful!')
    except Exception, e:
        log.debug('Recipient validation failed!')
        raise exception.InvalidRecipientError('Invalid recipient %s - %s'
                % (recipient, e))


def validate_sender(message):
    '''Sender validation:

    Given a parsed message object, validate if the sender may receive
    an auto-response.

    Return True if yes, False if not'''

    sender = message.get_unixfrom()

    log.debug('Validating sender: %s' % sender)

    # TODO
    result = True

    if result:
        log.debug('Sender validation successful!')
    else:
        log.debug('Sender validation failed!')
        raise exception.InvalidSenderError('Invalid sender %s' % sender)

    return result


def validate(manager, message):
    '''Message validation using the above defined functions'''

    log.debug('Validating message...')

    try:
        # Local parsing only:
        validate_sender(message)
        validate_headers(message)
        # Involves backend:
        validate_recipient(manager, message)
    except exception.ValidationError, e:
        log.info('Message validation (%s -> %s) failed: %s'
                % (message.get_unixfrom(), message.get_unixto(), e))
        raise

