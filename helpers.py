# -*- coding: utf-8 -*-

'''Response Project - Various Helpers'''

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

import os
import exception


def prepare_filepath(file, ignoreExisting=True):
    '''Prepare the path to a file, make sure all subdirs exist and
    check if everything is writable by the effective uid'''

    p = os.path.abspath(str(file))
    f = os.path.basename(p)
    d = os.path.dirname(p)

    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except:
            raise exception.FilePathError(3,
                    'Unable to recursively mkdir directory %s' % d)

    if os.path.exists(p):
        if ignoreExisting:
            if not os.access(p, os.W_OK):
                raise exception.FilePathError(2, 'File %s not writable' % p)
        else:
            raise exception.FilePathError(1, 'File %s already existing' % p)
    else:
        if not os.path.isdir(d) or not os.access(d, os.W_OK):
            raise exception.FilePathError(2, 'Unable to write to dir %s' % d)


