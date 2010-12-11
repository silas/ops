import helper

import os
import unittest
import ops.utils

class RmTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = helper.Workspace()

    def tearDown(self):
        self.workspace.destroy()

    def setup_file(self):
        self.path = self.workspace.join('file1')
        with open(self.path, 'w') as f:
            f.write('Hello World')

    def setup_directory(self):
        self.dir1_path = self.workspace.join('dir1')
        self.dir2_path = self.workspace.join('dir1', 'dir2')
        self.dir3_path = self.workspace.join('dir1', 'dir2', 'dir3')
        os.makedirs(self.dir3_path)

    def test_file(self):
        self.setup_file()
        self.assertTrue(os.path.isfile(self.path))
        ops.utils.rm(self.path)
        self.assertFalse(os.path.exists(self.path))

    def test_directory(self):
        self.setup_directory()
        self.assertTrue(os.path.isdir(self.dir1_path))
        self.assertTrue(os.path.isdir(self.dir2_path))
        self.assertTrue(os.path.isdir(self.dir3_path))
        ops.utils.rm(self.dir3_path)
        self.assertFalse(os.path.exists(self.dir3_path))
        self.assertTrue(os.path.exists(self.dir2_path))
        ops.utils.rm(self.dir2_path)
        self.assertFalse(os.path.exists(self.dir2_path))
        self.assertTrue(os.path.exists(self.dir1_path))
        ops.utils.rm(self.dir1_path)
        self.assertFalse(os.path.exists(self.dir1_path))

    def test_recursive(self):
        self.setup_directory()
        self.assertTrue(os.path.isdir(self.dir1_path))
        self.assertTrue(os.path.isdir(self.dir3_path))
        ops.utils.rm(self.dir1_path, recursive=True)
        self.assertFalse(os.path.exists(self.dir1_path))
        self.assertFalse(os.path.exists(self.dir3_path))

    def test_not_recursive(self):
        self.setup_directory()
        self.assertTrue(os.path.isdir(self.dir3_path))
        ops.utils.rm(self.dir1_path, recursive=False)
        self.assertTrue(os.path.isdir(self.dir3_path))

if __name__ == '__main__':
    unittest.main()
