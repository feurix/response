# -*- coding: utf-8 -*-

'''Response Project - Exceptions'''

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


class Error(Exception):
    '''All exceptions raised by response are based on this one'''
    pass

class ConfigError(Error):
    pass

class BackendError(Error):
    pass

class DatabaseError(Error):
    pass

class DatabaseQueryError(Error):
    pass

class ProcessError(Error):
    pass

class ValidationError(ProcessError):
    pass

class RecordError(ProcessError):
    pass

class RecordResponseError(RecordError):
    pass

class InvalidHeaderError(ValidationError):
    pass

class InvalidSenderError(ValidationError):
    pass

class InvalidRecipientError(ValidationError):
    pass


# Special case not based on Error
class NotImplemented(NotImplementedError):
    pass
