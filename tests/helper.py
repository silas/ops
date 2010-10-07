import logging
import shutil
import os

if os.environ.get('OPSUTILS_TEST_LOGGING'):
    opsutils_logger = logging.getLogger('opsutils')
    opsutils_logger.setLevel(logging.DEBUG)
    opsutils_logger.addHandler(logging.StreamHandler())

PATH = os.path.join(os.path.realpath(os.path.dirname(__file__)), '.tmp')

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
