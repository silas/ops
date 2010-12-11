import helper

import os
import unittest
import uuid
import ops.utils

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

        ops.utils.pushd(self.path1)
        self.check_path(self.path1)

        ops.utils.pushd(self.path2)
        self.check_path(self.path2)

        ops.utils.pushd(self.path3)
        self.check_path(self.path3)

        ops.utils.popd()
        self.check_path(self.path2)

        ops.utils.popd()
        self.check_path(self.path1)

        ops.utils.popd()
        self.check_path(self.path0)

    def test_no_class(self):
        self.check_path(self.path0)

        ops.utils.pushd(self.path1)
        self.check_path(self.path1)

        ops.utils.pushd(self.path2, no_class=True)
        self.check_path(self.path2)

        ops.utils.popd()
        self.check_path(self.path0)

        ops.utils.popd(no_class=True)
        self.check_path(self.path1)

    @staticmethod
    def assert_function_static():
        assert len(ops.utils.dirs()) == 0
        ops.utils.pushd(os.path.join(os.getcwd(), '..'))
        assert len(ops.utils.dirs()) == 1

    def test_function(self):
        self.check_path(self.path0)

        ops.utils.pushd(self.path3)
        self.check_path(self.path3)

        self.assertEqual(len(ops.utils.dirs()), 1)
        self.assert_function_static()
        self.assertEqual(len(ops.utils.dirs()), 1)
        self.check_path(self.path2)

        ops.utils.popd()
        self.check_path(self.path0)

if __name__ == '__main__':
    unittest.main()
