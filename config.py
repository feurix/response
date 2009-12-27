# -*- coding: utf-8 -*-

'''Response Project - Configuration Module'''

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
import backend

from ConfigParser import SafeConfigParser
from sockets import TcpServerSocket, UnixServerSocket
from sockets import TcpClientSocket, UnixClientSocket

SPACE = ' '

#
# Provide some defaults
#
class LMTPDConfig(object):
    socket = TcpServerSocket(host='127.0.0.1', port=10024)
    socket_acl = ['127.0.0.1',]
    hardfail = False
    softfail = True
    failsafe = False

    RECIPIENT_ADDRESS_REWRITE_RE = '(?P<user>\S+)#(?P<domain>\S+)@'

class BackendConfig(object):
    socket = TcpClientSocket(host='127.0.0.1', port=3306)
    username = 'response'
    password = 'FIXME'
    database = 'response'
    adapter = backend.MySQL
    query_validate_recipient_enabled = False
    query_validate_recipient = ''
    query_record_response = ''
    query_pending_responses = ''
    query_update_sent_timestamp = ''
    query_disable_expired_configs = ''
    query_delete_old_response_records = ''
    query_delete_records_of_disabled_configs = ''

class NotifyConfig(object):
    required_timedelta = 60 * 60 * 24 * 7  # 1 week
    smtp_host = '127.0.0.1'
    smtp_port = 25
    smtp_timeout = 20
    smtp_auth = False
    smtp_username = None
    smtp_password = None
    smtp_starttls = False
    smtp_envelope_from = '<>'
    message_charset = 'utf-8'
    message_insert_special_headers = True
    message_header_from_name = 'Autoresponder'
    message_header_from_address = None
    message_header_subject_prefix = None

class CleanupConfig(object):
    delete_records_with_last_hit_before = 60 * 60 * 24 * 7  # 1 week


class Config(object):

    backend = BackendConfig()
    lmtpd = LMTPDConfig()
    cleanup = CleanupConfig()
    notify = NotifyConfig()

    def __init__(self, file):
        self.config = SafeConfigParser()
        self.config.read(file)
        self.parse_lmtpd_config()
        self.parse_backend_config()
        self.parse_notify_config()
        self.parse_cleanup_config()

    def parse_lmtpd_config(self):
        section = 'LMTPD'
        config = self.lmtpd
        config_file = self.config

        config.socket = TcpServerSocket(
                host=config_file.get(section, 'SOCKET_ADDR'),
                port=config_file.getint(section, 'SOCKET_PORT'),
        )
        config.socket_acl = config_file.get(section, 'SOCKET_ACL').split()
        config.hardfail = config_file.getboolean(section, 'HARDFAIL')
        config.softfail = config_file.getboolean(section, 'SOFTFAIL')
        config.failsafe = config_file.getboolean(section, 'FAILSAFE')
        config.RECIPIENT_ADDRESS_REWRITE_RE = \
                config_file.get(section, 'RECIPIENT_ADDRESS_REWRITE_RE')

    def parse_backend_config(self):
        section = 'BACKEND'
        config = self.backend
        config_file = self.config

        config.socket = TcpClientSocket(
                host=config_file.get(section, 'DATABASE_HOST'),
                port=config_file.getint(section, 'DATABASE_PORT'),
        )
        config.username = config_file.get(section, 'USERNAME')
        config.password = config_file.get(section, 'PASSWORD')
        config.adapter = \
                getattr(backend, config_file.get(section, 'ADAPTER'))
        config.query_validate_recipient_enabled = \
                config_file.getboolean(
                        section,
                        'query_validate_recipient_enabled'
        )

        for query in [
                'query_validate_recipient',
                'query_record_response',
                'query_pending_responses',
                'query_update_sent_timestamp',
                'query_disable_expired_configs',
                'query_delete_old_response_records',
                'query_delete_records_of_disabled_configs',
        ]:
            setattr(config, query,
                    SPACE.join(config_file.get(section, query).split()))

    def parse_notify_config(self):
        section = 'NOTIFY'
        config = self.notify
        config_file = self.config

        config.smtp_host = config_file.get(section, 'SMTP_HOST')
        config.smtp_port = config_file.getint(section, 'SMTP_PORT')
        config.smtp_timeout = config_file.getint(section, 'SMTP_TIMEOUT')
        config.smtp_auth = config_file.getboolean(section, 'SMTP_AUTH')
        config.smtp_username = config_file.get(section, 'SMTP_USERNAME')
        config.smtp_password = config_file.get(section, 'SMTP_PASSWORD')
        config.smtp_starttls = config_file.getboolean(section, 'SMTP_STARTTLS')
        config.required_timedelta = \
                config_file.getint(section, 'REQUIRED_TIMEDELTA')
        config.smtp_envelope_from = \
                config_file.get(section, 'SMTP_ENVELOPE_FROM')
        config.message_charset = \
                config_file.get(section, 'MESSAGE_CHARSET').lower()
        config.message_insert_special_headers = \
                config_file.getboolean(section, 'MESSAGE_INSERT_SPECIAL_HEADERS')
        config.message_header_from_name = \
                config_file.get(section, 'MESSAGE_HEADER_FROM_NAME')
        config.message_header_from_address = \
                config_file.get(section, 'MESSAGE_HEADER_FROM_ADDRESS')
        config.message_header_subject_prefix = \
                config_file.get(section, 'MESSAGE_HEADER_SUBJECT_PREFIX')

    def parse_cleanup_config(self):
        section = 'CLEANUP'
        config = self.cleanup
        config_file = self.config

        config.delete_records_with_last_hit_before = \
                config_file \
                .getint(section, 'DELETE_RECORDS_WITH_LAST_HIT_BEFORE')

