# -*- coding: utf-8 -*-

'''Response Project - Configuration Module'''

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

from sockets import TcpClientSocket, TcpServerSocket, UnixClientSocket
from backend import MySQL, PostgreSQL


class LMTPConfig(object):
    def __init__(self):

        # Where should we listen? Only TcpServerSockets supported.
        self.socket = TcpServerSocket(host='localhost', port=10024)

        # Who may connect? Single IPv4 addresses only for now.
        #
        # TODO: Is it worth adding support for networks and CIDR notations?
        # Python 3 ships the ipaddr module, but we are using Python 2, so we
        # would have yet another dependency...
        self.socket_acl = ['127.0.0.1',]

        # Error Handling / Informing the client of problems
        #
        # Note: If all of the following options hardfail, softfail and failsafe
        # are False the default behaviour if softfail.
        #
        # Hint: In the following comments, the "client" is the application
        # speaking to us. This is most probably your MTA.

        # Indicate an error to the client if we're unable to process the message.
        # This will most probably result in a non-delivery status-notification
        # issued by the MTA back to the sender!
        # Note: Protocol-level errors (trying to use SMTP or unknown commands)
        # will always cause a hard 5xx error-code pushed back to the client.
        # Configure your client to connect to us using LMTP and run response-lmtp
        # in debug mode to see protocol errors.
        self.hardfail = False

        # Ask the client to re-send a message if we have problems?
        # Note: This might cause a delivery-status-notification of type
        # delayed issued by the MTA back to the sender, so be careful
        # and configure your MTA accordingly!
        self.softfail = True

        # Never inform the client of problems and silently discard/drop a
        # message if we have problems processing it.
        #
        # Warning: Most importantly, this option will silently drop a message
        # if the backend is unavailable (and hence will - if all validation
        # would have been successful - result in a missing autoresponse).
        # Use softfail if you want the MTA to try again later instead.
        self.failsafe = False


    # Define a function that will return the real recipient address,
    # depending heavily on your MTA setup and how it delivers to us.
    #
    # Assume the original recipient is john@mydomain.tld:
    #
    # In case of Postfix, we use a mysql virtual alias table to alias the
    # original recipient to (using a special SELECT):
    #
    #   john@mydomain.tld, john#mydomain.tld@response.internal
    #
    # The original @ was replaced by # and the new target domain is
    # response.internal.  Describing the above line: The mail is finally
    # delivered to the original recipient with whatever transport is configured
    # for the original target domain. In addition, the mail is delivered to the
    # internal only response.internal domain, which has a transport map entry:
    #
    #   repsonse.internal  response:[127.0.0.1]:10024
    #
    # Ok, so now all internally rewritten mail targeted at *@response.internal
    # uses the response transport :-) (Note: The response transport has to be
    # defined in master.cf, see the configuration examples for this)
    #
    # Finally, we end up with a problem. The recipient address that
    # response-lmtp receives is john#mydomain.tld@response.internal.
    #
    # This function has to reverse the rewriting, ie. we must return the
    # original john@mydomain.tld!
    #
    # Since this depends heavily on the used MTA and it's configuration
    # this function is part of the response-lmtp configuration:
    def parse_recipient(self, address):
        address = address.split('@', 1)[0]
        address = address.replace('#', '@')
        return address


class BackendConfig(object):
    def __init__(self):

        # Instructions for the backend adapter on how to connect.
        # Possible sockets: TcpClientSocket, UnixClientSocket
        self.socket = TcpClientSocket(host='mysql.db.mydomain.local', port=3306)
        #self.socket = UnixClientSocket(path='/var/run/mysql/socket.sock')

        # Credentials
        self.username = 'response'
        self.password = 'FIXME'

        # Database
        #
        # Note: this is currently used nowhere else in the code, only as a
        # substitution in the following query definitions. If you want to use
        # different databases for different queries, be free and do so. (If
        # your RDBMS can handle ForeignKeys across databases..., or you use
        # custom table schemas)
        self.database = 'response'


        #
        # PostgreSQL backend adapter
        #

        # TODO: Implement backend adapter and write queries.

        #self.adapter = PostgreSQL(config=self)
        #self.query_validate_recipient_enabled = False
        #self.query_validate_recipient = ''
        #self.query_record_response = ''


        #
        # MySQL backend adapter
        #

        self.adapter = MySQL(config=self)

        # Should we do local recipient response address validation?
        # Note: For better performance this should be performed directly by
        #       the MTA, so it can evaluate if we are a suitable transport
        #       in the first place and save the whole overhead.
        #       (sending the message to us, additional db connection...)
        self.query_validate_recipient_enabled = False

        # Must return 1 if receipient is valid and has an enabled autoresponse
        # configuration. Only needed if query_validate_enabled = True.
        #
        # Parameters:
        #
        #   address = E-Mail address of the local recipient
        #
        self.query_validate_recipient = \
                "SELECT 1 FROM `%(database)s`.`autoresponse_config` " \
                "WHERE `address` = '%%(address)s' AND `enabled` = 1" \
                % {'database': self.database}

        # Query to insert a new or update an existing response record.
        #
        # Parameters:
        #
        #   address = E-Mail address of the remote receipient
        #   sender = E-Mail address of the local sender
        #
        self.query_record_response = \
                "INSERT INTO `%(database)s`.`autoresponse_record` " \
                "(`sender_id`, `recipient`, `last`) " \
                    "SELECT " \
                    "`id` AS `sender_id`, '%%(recipient)s' AS `recipient`, " \
                    "'%%(date)s' AS `last` " \
                    "FROM `%(database)s`.`autoresponse_config` " \
                    "WHERE `address` = '%%(sender)s' " \
                "ON DUPLICATE KEY UPDATE `last` = '%%(date)s'" \
                % {'database': self.database}


class Config(object):
    def __init__(self, file):
        # TODO: Parse file...
        self.backend = BackendConfig()
        self.lmtp = LMTPConfig()


