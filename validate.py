# -*- coding: utf-8 -*-

'''Response Project - Message Validation'''

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

import re
import exception

from logger import getModuleLog
log = getModuleLog(__name__)


# Note for all regexps: We match _after_ parsing the message headers.
# No need to test for None, match space or a trailing colon in header names.


# The following lists of address matching regular expressions can be re-used
# later in different validation contexts:

#
# List of administrative e-mail address-regexps
#
MATCH_ADMIN_ADDRESS_RE = [

        # Mailer daemons
        re.compile('MAILER[-_]?(?:DAEMON)?@', re.IGNORECASE),

        # Administrative
        re.compile(
        '''
        (?:
            (?:
                (?:
                    dns
                |   ssl
                )?
                -?
                admin
            )
        |   abuse
        |   daemon
        |   server
        |   httpd?
        |   www-?(?:data)?
        |   root
        |   nobody
        |   (?:
                (?:
                    host
                |   post
                |   web
                )
                master
            )
        )
        @
        ''', re.VERBOSE | re.IGNORECASE),

        # Relays
        re.compile('.*-?(?:OUTGOING|RELAY)@', re.IGNORECASE),

] # end of admin address regexps

#
# List of mailinglist e-mail address-regexps
#
MATCH_LIST_ADDRESS_RE = [

        # Bugzillas and the like
        re.compile(
        '''
        (?:
            bugzilla
        |   trac
        )
        @
        ''', re.VERBOSE | re.IGNORECASE),

        # Mailinglists
        re.compile(
        '''
        (?:
            listserv
        |   mailman
        |   majordomo?
        )
        @
        ''', re.VERBOSE | re.IGNORECASE),

        # Mailinglist commands
        re.compile(
        r'''
        .*-         # start of suffix
        (?:
            admin
        |   bounces?
        |   confirm
        |   join
        |   leave
        |   owners?
        |   requests?
        |   (?:un)?subscribe
        )
        (?:\+.*)?   # optional address extension
        @
        ''', re.VERBOSE | re.IGNORECASE),

] # end of mailing list regexps


#
# List of obvious "do-not-reply" e-mail address-regexps
#
MATCH_NOREPLY_ADDRESS_RE = [

        # ...@
        re.compile(
        '''
        (:?do)?
        .*
        not?
        .*
        (?:
            reply
        |   return
        |   answere?s?
        )
        .*
        @
        ''', re.VERBOSE | re.IGNORECASE),

] # end of noreply address regexps


#
# List of e-mail address-regexps for other automated services
#
MATCH_AUTOMATED_ADDRESS_RE = [

        # Newsletters
        re.compile('.*news.*', re.IGNORECASE),

        # Automated mail
        re.compile(
        '''
        .*
        (?:
            info(?:rmation)?
        |   bounce
        |   cron
        |   robot
        |   report
        |   error
        |   counter
        |   sms
        |   reminder
        |   system
        |   status
        )
        .*
        ''', re.VERBOSE | re.IGNORECASE),

] # end of other automated address regexps


#
# List of business e-mail address-regexps
#
MATCH_BUSINESS_ADDRESS_RE = [

       # Non-personal / Business mail
        re.compile(
        '''
        .*
        (?:
            shop
        |   invoice
        |   sales
        |   legal
        |   support
        |   service
        |   ticket
        )
        .*
        ''', re.VERBOSE | re.IGNORECASE),

        # German variants
        re.compile(
        '''
        .*
        (?:
            rechnung
        |   bestell
        |   (?:be)?zahl
        |   (?:ver)?warnung
        |   versend
        |   versand
        |   bestaetig
        )
        .*
        ''', re.VERBOSE | re.IGNORECASE),

] # end of business address regexps


#
# List of community e-mail address-regexps
#
MATCH_COMMUNITY_ADDRESS_RE = [

        # Password / Account stuff
        re.compile(
        '''
        .*
        (?:
            password
        |   account
        |   reset
        )
        .*
        ''', re.VERBOSE | re.IGNORECASE),

        re.compile(
        '''
        .*
        (?:
            community
        |   board
        |   blog
        |   forum
        |   picture
        |   upload
        )
        .*
        ''', re.VERBOSE | re.IGNORECASE),

] # end of community address regexps


#
# List of INVALID SENDER regular expressions, matched against the sender
# address as given in the protocol command channel, using "MAIL FROM".
#
INVALID_SENDER_RE = [

        # The null sender, used for automated warnings, errors, notifications
        # and other stuff that should not be replied to.
        re.compile('<>'),

        # Sender domains
        re.compile(
        '''
        .*
        @
        .*
        (?:
        # Huge online stores
            ebay
        |   paypal
        |   amazon

        # Huge social networking sites
        # http://en.wikipedia.org/wiki/List_of_social_networking_websites
        |   facebook
        |   myspace
        |   twitter
        |   linkedin
        |   last.fm
        |   live.com
        |   xing
        |   badoo
        |   bebo
        |   buzznet
        |   classmates
        |   dating
        |   hi5
        |   hyves
        |   imeem
        |   kaixin001
        |   meetup
        |   qzone
        |   renren
        |   studivz
        |   schuelervz
        |   meinvz

        # Gaming sites
        |   steam
        |   gamespy
        |   fileplanet
        |   filefront
        )
        .*
        ''', re.VERBOSE | re.IGNORECASE),

] # end of sender regexps

# Add unwanted addresses to the list
INVALID_SENDER_RE.extend(MATCH_ADMIN_ADDRESS_RE)
INVALID_SENDER_RE.extend(MATCH_LIST_ADDRESS_RE)
INVALID_SENDER_RE.extend(MATCH_NOREPLY_ADDRESS_RE)
INVALID_SENDER_RE.extend(MATCH_AUTOMATED_ADDRESS_RE)
INVALID_SENDER_RE.extend(MATCH_BUSINESS_ADDRESS_RE)
INVALID_SENDER_RE.extend(MATCH_COMMUNITY_ADDRESS_RE)


#
# List of INVALID RECIPIENT regular expressions, matched against the recipient
# address as given in the protocol command channel, using "RCPT TO".
#
# Add all of your local addresses here that you don't want anyone to configure
# an autoresponse for. The best way to do this is to disallow configuring them
# for certain mailboxes in the configuration front-end (webmailer, etc.).
# Use this as a hardcoded exception list...
INVALID_RECIPIENT_RE = [

        # Temporarily disable auto-responses for @example.com,
        # even if some of the mailboxes have them configured already.
        # Note that this will only stop us from recording new responses,
        # not from delivering already queued responses.
        #re.compile('.*@example.com', re.IGNORECASE),

] # end of recipient regexps

# Add unwanted addresses to the list
INVALID_RECIPIENT_RE.extend(MATCH_ADMIN_ADDRESS_RE)
INVALID_RECIPIENT_RE.extend(MATCH_LIST_ADDRESS_RE)
INVALID_RECIPIENT_RE.extend(MATCH_NOREPLY_ADDRESS_RE)
INVALID_RECIPIENT_RE.extend(MATCH_AUTOMATED_ADDRESS_RE)
INVALID_RECIPIENT_RE.extend(MATCH_BUSINESS_ADDRESS_RE)
INVALID_RECIPIENT_RE.extend(MATCH_COMMUNITY_ADDRESS_RE)


#
# List of INVALID HEADER NAME regular expressions, matched against all headers
# of a parsed message. Note that this only matches the header name, not the
# value. Configure INVALID_HEADER_VALUE_RE if you want to do that.
#
INVALID_HEADER_NAME_RE = [

        # Mailing lists
        re.compile('(?:X-)?(:?Mailing)?-?List', re.IGNORECASE),
        re.compile(
        '''
        X-
        (?:
            Sent-To
        |   (?:
                List-?processor
            |   Mailman
            )
            -
            Version
        )
        ''', re.VERBOSE | re.IGNORECASE),

        # Resent
        re.compile('Resent-(?:Message-ID|Sender)', re.IGNORECASE),

        # Misc
        re.compile('Auto-Submit', re.IGNORECASE),
        re.compile(
        '''
        X-
        (?:
            Loop
        |   Cron
        |   Autore(?:sponse|ply)
        |   Auto-.+
        |   Bugzilla
        )
        ''', re.VERBOSE | re.IGNORECASE),

        re.compile(
        '''
        (?:
            Approved-By
        |   BestServHost
        )
        ''', re.VERBOSE | re.IGNORECASE),

] # end of invalid header name regexps


#
# List of INVALID HEADER VALUE regular expressions, matched against all headers
# of a parsed message. Note that this is always a pair of the regexp for the
# name and a list of regexps for the possible header values:
#
#   [
#       (HEADER_NAME_1_RE, [HEADER_1_VALUE_RE_1, HEADER_1_VALUE_RE_2, ...]),
#       (HEADER_NAME_2_RE, [HEADER_2_VALUE_RE_1, HEADER_2_VALUE_RE_2, ...]),
#       (..., [...]),
#   ]
#
INVALID_HEADER_VALUE_RE = [

        #
        # The magic precedence header :-)
        #
        (   # Header-Name RE
            re.compile('.*Precedence.*', re.IGNORECASE),

            [   # Header-Value REs
                re.compile('.*(?:bulk|junk|list).*', re.IGNORECASE),
            ]
        ),

        #
        # MimeOLE
        #
        (   # Header-Name RE
            re.compile('MimeOLE', re.IGNORECASE),

            [   # Header-Value REs
                re.compile('.*by.*php.*', re.IGNORECASE),
            ]
        ),

        #
        # Marked as spam
        #
        (   # Header-Name RE
            re.compile('X-Spam(?:-?Flag)', re.IGNORECASE),

            [   # Header-Value REs
                re.compile('.*Yes.*', re.IGNORECASE),
            ]
        ),

        #
        # Calendar, iCal, Meeting, etc.
        #
        (   # Header-Name RE
            re.compile('Content-Class', re.IGNORECASE),

            [   # Header-Value REs
                re.compile('.*calendar.*', re.IGNORECASE),
            ]
        ),

        #
        # Subjects
        #
        (   # Header-Name RE
            re.compile('Subject', re.IGNORECASE),

            [   # Header-Value REs
                re.compile('.*Out.*of.*office.*', re.IGNORECASE),
                re.compile('Auto[ -_]?Re(?:sponse|ply)$', re.IGNORECASE),

                # Subject starts with...
                re.compile(
                '''
                (?:
                    Cron
                |   News(?:letter)?
                )
                ''', re.VERBOSE | re.IGNORECASE),
            ]
        ),

] # end of invalid header value regexps


def validate_headers(message):
    '''Header validation:

    Given a parsed message object, validate if this message may trigger
    an autoresponse.'''

    invalid_header = (None, None)
    valid = True

    log.debug('Validating headers')

    # Validate header *NAMES*
    for header_name in message.keys():
        for regexp in INVALID_HEADER_NAME_RE:
            if regexp.match(header_name):
                invalid_header = (header_name, message.get(header_name))
                valid = False
                break
        if not valid:
            break

    # Validate header *VALUES*
    if valid:
        for header_name, header_value in message.items():
            for name_regexp, value_regexps in INVALID_HEADER_VALUE_RE:
                if name_regexp.match(header_name):
                    for value_regexp in value_regexps:
                        if value_regexp.match(header_value):
                            invalid_header = (header_name, header_value)
                            valid = False
                            break
                if not valid:
                    break
            if not valid:
                break

    if valid:
        log.debug('Header validation successful!')
    else:
        log.debug('Header validation failed!')
        raise exception.InvalidHeaderError('Invalid header: %s: %s'
                % invalid_header)


def validate_recipient(manager, message):
    '''Recipient validation:

    Given a parsed message object, validate if the local recipient has
    configured and enabled an auto-response.'''

    recipient = message.get_unixto()
    valid = True

    log.debug('Validating recipient: %s' % recipient)

    # First of all, don't respond to messages that don't list us as one
    # of the primary recipients. This can happen with address rewriting
    # due to virtual aliases.
    if not (recipient in message.get('To', failobj='')
        or  recipient in message.get('Cc', failobj='')):
        valid = False

    # Validate against the list of invalid recipient regexps before
    # involving the backend in any way
    if valid:
        for regexp in INVALID_RECIPIENT_RE:
            if regexp.match(recipient):
                valid = False
                break

    if valid:
        try:
            manager.validate_recipient(recipient)
            log.debug('Recipient validation successful!')
        except Exception, e:
            log.debug('Recipient validation failed!')
            raise exception.InvalidRecipientError('Invalid recipient %s - %s'
                    % (recipient, e))
    else:
        log.debug('Recipient validation failed!')
        raise exception.InvalidRecipientError('Invalid recipient %s' % recipient)


def validate_sender(message):
    '''Sender validation:

    Given a parsed message object, validate if the sender may receive
    an auto-response.'''

    sender = message.get_unixfrom()
    valid = True

    log.debug('Validating sender: %s' % sender)

    # Don't loop on our own...
    if sender == message.get_unixto():
        valid = False

    # Validate against the huge list of invalid sender regexps
    if valid:
        for regexp in INVALID_SENDER_RE:
            if regexp.match(sender):
                valid = False
                break

    if valid:
        log.debug('Sender validation successful!')
    else:
        log.debug('Sender validation failed!')
        raise exception.InvalidSenderError('Invalid sender %s' % sender)


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

