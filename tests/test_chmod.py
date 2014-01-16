from __future__ import unicode_literals

import helper

import os
import unittest

import ops


class ChmodTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = helper.Workspace()

    def tearDown(self):
        self.workspace.destroy()

    def setup_file(self):
        self.path = self.workspace.join('file')
        with open(self.path, 'w') as f:
            f.write('hello world')

    def setup_directory(self):
        self.dir_path = self.workspace.join('dir')
        self.file_path = self.workspace.join('dir', 'file')
        os.makedirs(self.dir_path)
        with open(self.file_path, 'w') as f:
            f.write('hello world')

    def test_error(self):
        # OSError
        self.assertFalse(ops.chmod('/tmp/ops-chmod-missing', 0o777))
        # TypeError
        self.assertFalse(ops.chmod(0, 0o777))

    def test_file(self):
        self.setup_file()

        ops.chmod(self.path, 0o777)
        self.assertEqual(os.stat(self.path).st_mode, 33279)

        ops.chmod(self.path, 0o666)
        self.assertEqual(os.stat(self.path).st_mode, 33206)

        ops.chmod(self.path, 0o555)
        self.assertEqual(os.stat(self.path).st_mode, 33133)

        ops.chmod(self.path, 0o444)
        self.assertEqual(os.stat(self.path).st_mode, 33060)

        ops.chmod(self.path, 0o333)
        self.assertEqual(os.stat(self.path).st_mode, 32987)

        ops.chmod(self.path, 0o222)
        self.assertEqual(os.stat(self.path).st_mode, 32914)

        ops.chmod(self.path, 0o111)
        self.assertEqual(os.stat(self.path).st_mode, 32841)

        ops.chmod(self.path, 0o000)
        self.assertEqual(os.stat(self.path).st_mode, 32768)

        u = ops.perm(read=True, write=True, execute=True)
        g = ops.perm(read=True, write=True, execute=False)
        o = ops.perm(read=False, write=False, execute=False)

        ops.chmod(self.path, user=u, group=g, other=o)
        self.assertEqual(os.stat(self.path).st_mode, 33264)

    def test_recursive(self):
        self.setup_directory()

        ops.chmod(self.dir_path, 0o755)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16877)

        ops.chmod(self.file_path, 0o644)
        self.assertEqual(os.stat(self.file_path).st_mode, 33188)

        ops.chmod(self.dir_path, 0o777)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16895)
        self.assertEqual(os.stat(self.file_path).st_mode, 33188)

        ops.chmod(self.dir_path, 0o777, recursive=True)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16895)
        self.assertEqual(os.stat(self.file_path).st_mode, 33279)

        ops.chmod(self.dir_path, 0o555, recursive=True)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16749)
        self.assertEqual(os.stat(self.file_path).st_mode, 33133)

        ops.chmod(self.dir_path, 0o777, recursive=True)

if __name__ == '__main__':
    unittest.main()
