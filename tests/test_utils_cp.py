import helper

import os
import unittest
import uuid
import ops.utils

class CpTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = helper.Workspace()

    def tearDown(self):
        self.workspace.destroy()

    def setup_file(self):
        self.name1 = 'file1'
        self.name2 = 'file2'
        self.path1 = self.workspace.join(self.name1)
        self.path2 = self.workspace.join(self.name2)
        self.content = 'Hello World'
        with open(self.path1, 'w') as f:
            f.write(self.content)

    def setup_directory(self):
        self.name1 = 'dir1'
        self.name2 = 'dir2'
        self.path1 = self.workspace.join(self.name1)
        self.path2 = self.workspace.join(self.name2)
        os.makedirs(self.path1)
        self.src_file_path1 = self.workspace.join(self.name1, 'file1')
        self.src_file_path2 = self.workspace.join(self.name1, 'file2')
        self.dst_file_path1 = self.workspace.join(self.name2, 'file1')
        self.dst_file_path2 = self.workspace.join(self.name2, 'file2')
        self.content1 = 'Hello World 1'
        self.content2 = 'Hello World 2'
        with open(self.src_file_path1, 'w') as f:
            f.write(self.content1)
        with open(self.src_file_path2, 'w') as f:
            f.write(self.content2)

    def check_stat(self, path1, path2):
        stat1 = os.stat(path1)
        stat2 = os.stat(path2)
        self.assertEqual(stat1[0], stat2[0]) # st_mode
        self.assertNotEqual(stat1[1], stat2[1]) # st_ino
        self.assertEqual(stat1[2], stat2[2]) # st_dev
        self.assertEqual(stat1[3], stat2[3]) # st_nlink
        self.assertEqual(stat1[4], stat2[4]) # st_uid
        self.assertEqual(stat1[5], stat2[5]) # st_gid
        self.assertEqual(stat1[6], stat2[6]) # st_size
        self.assertEqual(stat1[7], stat2[7]) # st_atime
        self.assertEqual(stat1[8], stat2[8]) # st_ctime

    def check_same_file(self, path1, path2):
        content1 = uuid.uuid4().get_hex()
        content2 = uuid.uuid4().get_hex()
        with open(path1, 'r') as f:
            content1 = f.read()
        with open(path2, 'r') as f:
            content2 = f.read()
        self.assertEqual(content1, content2)
        self.check_stat(path1, path2)

    def test_file_to_file(self):
        self.setup_file()
        ops.utils.cp(self.path1, self.path2)
        self.check_same_file(self.path1, self.path2)

    def test_file_to_directory(self):
        self.setup_file()
        dir_path = self.workspace.join('dst')
        os.makedirs(dir_path)
        ops.utils.cp(self.path1, dir_path)
        path2 = os.path.join(dir_path, self.name1)
        self.check_same_file(self.path1, path2)

    def test_directory(self):
        self.setup_directory()
        ops.utils.cp(self.path1, self.path2)
        self.check_same_file(self.src_file_path1, self.dst_file_path1)
        self.check_same_file(self.src_file_path2, self.dst_file_path2)
        self.check_stat(self.path1, self.path2)

    def test_recursive(self):
        self.setup_directory()
        path = self.workspace.join('dst')
        ops.utils.cp(self.path1, path, recursive=False)
        self.assertFalse(os.path.exists(path))
        ops.utils.cp(self.path1, path, recursive=True)
        self.assertTrue(os.path.isdir(path))

if __name__ == '__main__':
    unittest.main()
