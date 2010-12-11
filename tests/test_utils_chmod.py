import helper

import os
import unittest
import ops.utils

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

    def test_file(self):
        self.setup_file()

        ops.utils.chmod(self.path, 0777)
        self.assertEqual(os.stat(self.path).st_mode, 33279)

        ops.utils.chmod(self.path, 0666)
        self.assertEqual(os.stat(self.path).st_mode, 33206)

        ops.utils.chmod(self.path, 0555)
        self.assertEqual(os.stat(self.path).st_mode, 33133)

        ops.utils.chmod(self.path, 0444)
        self.assertEqual(os.stat(self.path).st_mode, 33060)

        ops.utils.chmod(self.path, 0333)
        self.assertEqual(os.stat(self.path).st_mode, 32987)

        ops.utils.chmod(self.path, 0222)
        self.assertEqual(os.stat(self.path).st_mode, 32914)

        ops.utils.chmod(self.path, 0111)
        self.assertEqual(os.stat(self.path).st_mode, 32841)

        ops.utils.chmod(self.path, 0000)
        self.assertEqual(os.stat(self.path).st_mode, 32768)


    def test_recursive(self):
        self.setup_directory()

        ops.utils.chmod(self.dir_path, 0755)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16877)

        ops.utils.chmod(self.file_path, 0644)
        self.assertEqual(os.stat(self.file_path).st_mode, 33188)

        ops.utils.chmod(self.dir_path, 0777)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16895)
        self.assertEqual(os.stat(self.file_path).st_mode, 33188)

        ops.utils.chmod(self.dir_path, 0777, recursive=True)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16895)
        self.assertEqual(os.stat(self.file_path).st_mode, 33279)

        ops.utils.chmod(self.dir_path, 0555, recursive=True)
        self.assertEqual(os.stat(self.dir_path).st_mode, 16749)
        self.assertEqual(os.stat(self.file_path).st_mode, 33133)

        ops.utils.chmod(self.dir_path, 0777, recursive=True)

if __name__ == '__main__':
    unittest.main()
