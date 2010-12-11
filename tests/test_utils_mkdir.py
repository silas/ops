import helper

import os
import unittest
import ops.utils

class MkdirTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = helper.Workspace()

    def tearDown(self):
        self.workspace.destroy()

    def check_dirs(self, single, multiple, **kwargs):
        path = self.workspace.join('single')
        ops.utils.mkdir(path, **kwargs)
        self.assertEqual(os.path.isdir(path), single)
        path = self.workspace.join('multiple', 'levels', 'here')
        ops.utils.mkdir(path, **kwargs)
        self.assertEqual(os.path.isdir(path), multiple)

    def test_default(self):
        self.check_dirs(True, True)

    def test_recursive(self):
        self.check_dirs(True, True, recursive=True)

    def test_no_recursive(self):
        self.check_dirs(True, False, recursive=False)

if __name__ == '__main__':
    unittest.main()
