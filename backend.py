# -*- coding: utf-8 -*-

'''Response Project - Backend Manager and Adapters'''

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

from datetime import datetime

from logger import getModuleLog
log = getModuleLog(__name__)


class DatabaseBackend(object):
    '''Base class of database backend adapters with all public functions
    used by the backend manager.
    '''
    # Format of the result set doesn't matter
    CURSOR_DEFAULT = None

    # If connect() is called with this cursor class the result set must
    # return rows as dictionaries, with the column names as keys!
    CURSOR_DICT = None

    def connect(self, unicode, cursorclass):
        raise exception.NotImplemented

    def open_cursor(self, connection):
        raise exception.NotImplemented

    def close_cursor(self, cursor):
        raise exception.NotImplemented

    def commit(self, connection):
        raise exception.NotImplemented

    def rollback(self, connection):
        raise exception.NotImplemented

    def disconnect(self, connection):
        raise exception.NotImplemented

    def close(self):
        raise exception.NotImplemented

    def fetchrow(self, cursor):
        raise exception.NotImplemented

    def query(self, cursor, sql, sql_params):
        raise exception.NotImplemented

    def validate_recipient(self, cusor, address):
        raise exception.NotImplemented

    def record_response(self, cursor, sender, recipient):
        raise exception.NotImplemented

    def get_pending_responses(self, cursor, date, limit):
        raise exception.NotImplemented

    def update_sent_timestamp(self, cursor, id, date):
        raise exception.NotImplemented

    def disable_expired_configs(self, cursor, date):
        raise exception.NotImplemented

    def delete_old_response_records(self, cursor, date):
        raise exception.NotImplemented

    def delete_records_of_disabled_configs(self, cursor):
        raise exception.NotImplemented


class PostgreSQL(DatabaseBackend):
    '''PostgreSQL Backend Adapter'''

    # TODO: should be quite easy given the MySQL implementation
    pass


class MySQL(DatabaseBackend):
    '''MySQL Backend Adapter'''

    import MySQLdb
    import MySQLdb.cursors
    import _mysql_exceptions
    import sqlalchemy.pool as pool

    LABEL = 'MySQL'

    CURSOR_DEFAULT = MySQLdb.cursors.Cursor
    CURSOR_DICT = MySQLdb.cursors.DictCursor

    # Connection pooling
    DatabasePool = pool.manage(MySQLdb, recycle=120)

    def __init__(self, config):
        self.config = config

        if self.config.socket.type == 'UNIX':
            self.name = self.config.socket.path
            self.connection_params = {
                    'unix_socket': self.config.socket.path
            }
        else:
            self.name = self.config.socket.host
            self.connection_params = {
                    'host': self.config.socket.host,
                    'port': self.config.socket.port,
            }
        self.connection_params.update({
                    'user': self.config.username,
                    'passwd': self.config.password
        })

    def _log(self, _log, message):
        _log('%s: %s' % (self.LABEL, message))

    def connect(self, unicode=True, cursorclass=CURSOR_DEFAULT):
        self.connection_params.update({
                    'use_unicode': unicode,
                    'cursorclass': cursorclass,
        })
        self._log(log.info, 'Asking pool for a connection')
        try:
            connection = self.DatabasePool.connect(**self.connection_params)
        except self.MySQLdb.OperationalError, e:
            self._log(log.error, 'Unable to aquire a connection to server %s' \
                    % self.name)
            raise exception.DatabaseError(
                    '%s: Could not connect to server: %s' % (self.LABEL, e))
        self._log(log.debug, 'Successfully aquired connection from pool')
        return connection

    def open_cursor(self, connection):
        self._log(log.debug, 'Opening cursor for connection')
        return connection.cursor()

    def close_cursor(self, cursor):
        self._log(log.debug, 'Closing cursor for connection')
        cursor.close()

    def commit(self, connection):
        self._log(log.info, 'Committing changes')
        connection.commit()

    def rollback(self, connection):
        self._log(log.info, 'Rolling back changes')
        connection.rollback()

    def disconnect(self, connection):
        self._log(log.info, 'Releasing connection')
        connection.close()

    def close(self):
        self._log(log.info, 'Disposing connection pool...')
        self.DatabasePool.dispose()

    def query(self, cursor, sql, sql_params={}):
        if sql_params:
            # XXX normalize params? Not really... we quoted strings in the
            # query (see backend configuration) and e-mail addresses must not
            # contain any dangerous characters. Hint: MySQLdb can do that on
            # it's own if we pass it the params. Let's keep it specialized for
            # now.
            sql = sql % sql_params

        self._log(log.debug, 'Executing query: %s' % sql)
        try:
            return cursor.execute(sql)
        except self._mysql_exceptions.ProgrammingError, e:
            raise exception.DatabaseQueryError(
                    '%s: Error executing query: %s' % (self.LABEL, e), sql)
        except self._mysql_exceptions.IntegrityError, e:
            raise exception.DatabaseQueryError(
                    '%s: Integrity error: %s' % (self.LABEL, e), sql)

    def fetchrow(self, cursor):
        return cursor.fetchone()

    def validate_recipient(self, cursor, address):
        if not self.config.query_validate_recipient_enabled:
            return

        try:
            result = self.query(cursor, self.config.query_validate_recipient,
                    {'address': address})
            if result != 1:
                raise exception.DatabaseQueryError(
                        '%s: Unexpected number of rows returned' % self.LABEL)
            elif cursor.fetchall()[0][0] != 1:
                raise exception.DatabaseQueryError(
                        '%s: Unable to find valid recipient entry' % self.LABEL)
        except Exception, e:
            self._log(log.info, 'Unable to validate recipient %s - %s'
                    % (address, e))
            raise

    def record_response(self, cursor, sender, recipient):
        try:
            result = self.query(cursor, self.config.query_record_response, {
                'sender': sender,
                'recipient': recipient,
                'date': datetime.now(),
            })
            if result <= 0:
                raise exception.DatabaseQueryError(
                        '%s: Query affected no rows' % self.LABEL)
        except Exception, e:
            self._log(log.info, 'Unable to record autoresponse: %s -> %s - %s'
                    % (sender, recipient, e))
            raise

    def get_pending_responses(self, cursor, date, limit):
        try:
            return self.query(cursor, self.config.query_pending_responses,
                    {
                        'date': date,
                        'limit': limit,
                    })
        except Exception, e:
            self._log(log.info,
                    'Unable to query for pending responses: %s' % e)
            raise

    def update_sent_timestamp(self, cursor, id, date):
        try:
            return self.query(cursor, self.config.query_update_sent_timestamp,
                    {
                        'id': id,
                        'date': date,
                     })
        except Exception, e:
            self._log(log.info,
                    'Unable to update sent timestamp (record id %s): %s'
                    % (id, e))
            raise

    def disable_expired_configs(self, cursor, date):
        try:
            return self.query(cursor,
                    self.config.query_disable_expired_configs,
                    {'date': date})
        except Exception, e:
            self._log(log.info, 'Unable to disable expired configs: %s' % e)
            raise

    def delete_old_response_records(self, cursor, date):
        try:
            return self.query(cursor,
                    self.config.query_delete_old_response_records,
                    {'date': date})
        except Exception, e:
            self._log(log.info, 'Unable to delete old records: %s' % e)
            raise

    def delete_records_of_disabled_configs(self, cursor):
        try:
            return self.query(cursor,
                    self.config.query_delete_records_of_disabled_configs)
        except Exception, e:
            self._log(log.info,
                    'Unable to delete records of disabled configs: %s' % e)
            raise


class Manager(object):
    '''Backend Manager

    Each channel has one backend manager instance, resulting in:
    - one backend connection (if possible from a pool) per channel
    - thread safe query execution :-)
    '''

    def __init__(self, backend):
        self.backend = backend
        self.connection = None
        self.cursor = None

    def __nonzero__(self):
        return bool(self.connection)

    def connect(self, *args, **kwargs):
        if not self.connection:
            self.connection = self.backend.connect(*args, **kwargs)

    def close(self):
        if self.connection:
            if self.cursor:
                self.backend.close_cursor(self.cursor)
            self.backend.commit(self.connection)
            self.backend.disconnect(self.connection)

    def get_cursor(self):
        if not self.cursor:
            self.connect()
            self.cursor = self.backend.open_cursor(self.connection)

    def validate_recipient(self, *args, **kwargs):
        self.connect()
        self.get_cursor()
        self.backend.validate_recipient(self.cursor, *args, **kwargs)

    def record_response(self, *args, **kwargs):
        self.connect()
        self.get_cursor()
        self.backend.record_response(self.cursor, *args, **kwargs)

