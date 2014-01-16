from __future__ import unicode_literals

import logging
import os
import shutil
import sys
import uuid as uuid_


py3 = sys.version_info[0] > 2

if py3:
    bytes_type = bytes
    unicode_type = str
    basestring_type = str
else:
    bytes_type = str
    unicode_type = unicode
    basestring_type = basestring


if os.environ.get('OPS_TEST_LOGGING'):
    ops_logger = logging.getLogger('ops')
    ops_logger.setLevel(logging.DEBUG)
    ops_logger.addHandler(logging.StreamHandler())

PATH = os.path.join(os.path.realpath(os.path.dirname(__file__)), '.tmp')


def uuid():
    return uuid_.uuid4().hex


class Workspace(object):

    def __init__(self, name='default', path=PATH, create=True):
        self._path = os.path.join(path, name)
        if create:
            self.create()

    @property
    def path(self):
        return self._path

    def join(self, *args):
        return os.path.join(self.path, *args)

    def create(self):
        self.destroy()
        os.makedirs(self.path)

    def destroy(self):
        if not os.path.exists(self.path):
            return
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)
        elif os.path.isfile(self.path):
            os.remote(self.path)
        else:
            raise Exception('Test only deletes files and directories: %s' % self.path)
        try:
            os.rmdir(PATH)
        except OSError:
            pass
