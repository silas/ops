import helper

import os
import unittest
import uuid
import opsutils

class DirsPushPopTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = helper.Workspace()
        self.name1 = 'dir1-%s' % uuid.uuid4().get_hex()[:5]
        self.name2 = 'dir2-%s' % uuid.uuid4().get_hex()[:5]
        self.name3 = 'dir3-%s' % uuid.uuid4().get_hex()[:5]
        self.path0 = os.getcwd()
        self.path1 = self.workspace.join(self.name1)
        self.path2 = self.workspace.join(self.name1, self.name2)
        self.path3 = self.workspace.join(self.name1, self.name2, self.name3)
        os.makedirs(self.path3)

    def check_path(self, path):
        self.assertEqual(os.getcwd(), path)

    def test_class(self):
        self.check_path(self.path0)
        opsutils.pushd(self.path1)
        self.check_path(self.path1)
        opsutils.pushd(self.path2)
        self.check_path(self.path2)
        opsutils.pushd(self.path3)
        self.check_path(self.path3)
        opsutils.popd()
        self.check_path(self.path2)
        opsutils.popd()
        self.check_path(self.path1)
        opsutils.popd()
        self.check_path(self.path0)

    def test_function(self):
        self.check_path(self.path0)
        opsutils.pushd(self.path1)
        self.check_path(self.path1)

        self.assertEqual(len(opsutils.dirs()), 1)

        def func():
            self.assertEqual(len(opsutils.dirs()), 0)
            opsutils.pushd(self.path3)
        func()

        self.assertEqual(len(opsutils.dirs()), 1)

        opsutils.pushd(self.path2)
        self.check_path(self.path2)
        opsutils.popd()
        self.check_path(self.path1)
        opsutils.popd()
        self.check_path(self.path0)

if __name__ == '__main__':
    unittest.main()
