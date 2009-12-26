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

    # Where should we listen? Only TcpServerSockets supported.
    socket = TcpServerSocket(host='127.0.0.1', port=10024)

    # Who may connect? Single IPv4 addresses only for now.
    #
    # TODO: Is it worth adding support for networks and CIDR notations?
    # Python 3 ships the ipaddr module, but we are using Python 2, so we
    # would have yet another dependency...
    socket_acl = ['127.0.0.1',]

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
    hardfail = False

    # Ask the client to re-send a message if we have problems?
    # Note: This might cause a delivery-status-notification of type
    # delayed issued by the MTA back to the sender, so be careful
    # and configure your MTA accordingly!
    softfail = True

    # Never inform the client of problems and silently discard/drop a
    # message if we have problems processing it.
    #
    # Warning: Most importantly, this option will silently drop a message
    # if the backend is unavailable (and hence will - if all validation
    # would have been successful - result in a missing autoresponse).
    # Use softfail if you want the MTA to try again later instead.
    failsafe = False


    # Define a function that will return the real recipient address,
    # depending heavily on your MTA setup and how it delivers to us.
    #
    # Assume the original recipient is john@mydomain.tld:
    #
    # In case of Postfix, we silently create a copy of each message
    # whose original recipient has configured and enabled an autoresponse.
    # The internal recipient of this message is, for example:
    #
    #   john#mydomain.tld@response.internal
    #
    # The original @ was replaced by # and the new target domain is
    # response.internal.  Describing the above line: The mail is finally
    # delivered to the original recipient with whatever transport is configured
    # for the original target domain. In addition, the copy of the mail is
    # delivered to the internal only response.internal domain, which has a
    # transport map entry:
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

    # Instructions for the backend adapter on how to connect.
    # Possible sockets: TcpClientSocket, UnixClientSocket
    socket = TcpClientSocket(host='mysql.db.mydomain.local', port=3306)
    #socket = UnixClientSocket(path='/var/run/mysql/socket.sock')

    # Credentials
    username = 'response'
    password = 'FIXME'

    # Database
    #
    # Note: this is currently used nowhere else in the code, only as a
    # substitution in the following query definitions. If you want to use
    # different databases for different queries, be free and do so. (If
    # your RDBMS can handle ForeignKeys across databases..., or you use
    # custom table schemas)
    database = 'response'


    #
    # PostgreSQL backend adapter
    #

    # TODO: Implement backend adapter and write queries.

    #adapter = PostgreSQL()
    #query_validate_recipient_enabled = False
    #query_validate_recipient = ''
    #query_record_response = ''


    #
    # MySQL backend adapter
    #

    adapter = MySQL

    # Should we do local recipient response address validation?
    # Note: For better performance this should be performed directly by
    #       the MTA, so it can evaluate if we are a suitable transport
    #       in the first place and save the whole overhead.
    #       (sending the message to us, additional db connection...)
    query_validate_recipient_enabled = False

    # Must return 1 if receipient is valid and has an enabled autoresponse
    # configuration. Only needed if query_validate_enabled = True.
    #
    # Parameters:
    #
    #   address = E-Mail address of the local recipient
    #
    query_validate_recipient = \
            "SELECT 1 FROM `%(database)s`.`autoresponse_config` " \
            "WHERE `address` = '%%(address)s' AND `enabled` = 1" \
            % {'database': database}

    # Query to insert a new or update an existing response record.
    #
    # Parameters:
    #
    #   address = E-Mail address of the remote receipient
    #   sender = E-Mail address of the local sender
    #
    query_record_response = \
            "INSERT INTO `%(database)s`.`autoresponse_record` " \
            "(`sender_id`, `recipient`, `hit`) " \
                "SELECT " \
                "`id` AS `sender_id`, '%%(recipient)s' AS `recipient`, " \
                "'%%(date)s' AS `hit` " \
                "FROM `%(database)s`.`autoresponse_config` " \
                "WHERE `address` = '%%(sender)s' " \
            "ON DUPLICATE KEY UPDATE `hit` = '%%(date)s'" \
            % {'database': database}

    # Query to get pending responses.
    #
    # Parameters:
    #
    #   date = The latest sent-date back in history we require to send
    #          another response. See NotifyConfig.required_timedelta.
    #  limit = Upper limit of rows returned.
    #
    query_pending_responses = \
            "SELECT `record`.`id` AS `id`, " \
                   "`config`.`address` AS `sender`, " \
                   "`record`.`recipient` AS `recipient`, " \
                   "`config`.`subject` AS `subject`, " \
                   "`config`.`message` AS `message`, " \
                   "`record`.`sent` AS `sent` " \
              "FROM `%(database)s`.`autoresponse_config` `config`, " \
                   "`%(database)s`.`autoresponse_record` `record` " \
             "WHERE `config`.`id` = `record`.`sender_id` " \
               "AND `config`.`enabled` = 1 " \
               "AND ( " \
                        "`record`.`sent` = 0 " \
                     "OR `record`.`sent` < '%%(date)s' " \
                    ") " \
              "LIMIT %%(limit)d" \
            % {'database': database}

    # Query to update the sent timestamp of successfully sent responses.
    #
    # Parameters:
    #
    #     id = The id of the record.
    #   date = The current date.
    #
    query_update_sent_timestamp = \
            "UPDATE `%(database)s`.`autoresponse_record` `record` " \
               "SET `sent` = '%%(date)s' " \
             "WHERE `record`.`id` = %%(id)d" \
            % {'database': database}

    # Query to disable autoresponders if they have expired.
    #
    # Parameters:
    #
    #   date = The current date.
    #
    query_disable_expired_configs = \
            "UPDATE `%(database)s`.`autoresponse_config` `config` " \
               "SET `enabled` = 0 " \
             "WHERE `config`.`enabled` = 1 " \
               "AND `config`.`expires` < '%%(date)s'" \
            % {'database': database}

    # Query to delete old response records with no activity after the
    # given date.
    #
    # Parameters:
    #
    #   date = The earliest hit-date back in history when we consider a
    #          record to be deleted.
    #
    query_delete_old_response_records = \
            "DELETE `%(database)s`.`record` " \
              "FROM `%(database)s`.`autoresponse_record` `record` " \
             "WHERE `record`.`hit` < '%%(date)s'" \
            % {'database': database}

    # Query to delete records of disabled response configs.
    #
    # Parameters:
    #
    #   None
    #
    query_delete_records_of_disabled_configs = \
            "DELETE `%(database)s`.`record` " \
              "FROM `%(database)s`.`autoresponse_record` `record` " \
         "LEFT JOIN `%(database)s`.`autoresponse_config` `config` " \
                "ON `record`.`sender_id` = `config`.`id` " \
             "WHERE `config`.`enabled` = 0" \
            % {'database': database}


class NotifyConfig(object):

    # How many seconds must pass before we send a successive response
    # from the same sender to the same recipient?
    required_timedelta = 60 * 60 * 24 * 7  # 1 week

    #
    # Using a local sendmail binary
    #

    # TODO: Not implemented yet. Is it worth the effort?
    # Let's use some (E)SMTP relay!
    # Use local sendmail command, if yes, which?
    # sendmail_command = ['/usr/bin/sendmail', 'arg1', 'arg2', ...]


    #
    # Using a SMTP relay
    #
    smtp_host = 'localhost'
    smtp_port = 25
    smtp_timeout = 20

    smtp_auth = False
    smtp_username = None
    smtp_password = None

    starttls = False

    # http://en.wikipedia.org/wiki/Envelope_sender
    # This is the sender address given in the command channel of the SMTP
    # protocol using "MAIL FROM". The null sender is *strongly* suggested
    # to avoid loops and other bad stuff!
    smtp_envelope_from = '<>'


    #
    # Configuration of autoresponse message creation
    #

    # Message charset
    message_charset = 'utf-8'

    # Insert special headers to prevent other systems responding to our
    # autoresponses? This is *strongly* suggested!
    message_insert_special_headers = True

    # Set a realname to use in the "From" header.
    message_header_from_name = 'Autoresponder'

    # Override the address in the "From" header of the response?  (The
    # default is to use the e-mail address of the original local recipient)
    message_header_from_address = None

    # Prepend something to all subjects of all response messages?
    message_header_subject_prefix = None



class CleanupConfig(object):

    # Delete response records after the last hit is at least this old,
    # in seconds. Used with -O, --delete-old-response-records.
    # Note: This should be at least NofifyConfig.timedelta_required
    delete_records_with_last_hit_before = 60 * 60 * 24 * 7  # 1 week


class Config(object):

    # TODO: Parse file...
    backend = BackendConfig()
    lmtpd = LMTPConfig()
    cleanup = CleanupConfig()
    notify = NotifyConfig()

    def __init__(self, file):
        pass

