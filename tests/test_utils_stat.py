import helper

import datetime
import grp
import pwd
import os
import unittest
import uuid
import ops.utils

class StatTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = helper.Workspace()
        self.uid = os.geteuid()
        self.user = pwd.getpwuid(self.uid)[0]
        self.gid = os.getgid()
        self.group = grp.getgrgid(self.gid)[0]

    def tearDown(self):
        self.workspace.destroy()

    def test_values(self):
        path = self.workspace.path
        stat = ops.utils.stat(path)

        self.assertTrue(isinstance(stat.st_mode, int))

        self.assertTrue(isinstance(stat.st_ino, int))
        self.assertEqual(stat.inode, stat.st_ino)

        self.assertFalse(stat.st_dev is None)
        self.assertEqual(stat.device, stat.st_dev)

        self.assertTrue(isinstance(stat.st_nlink, int))
        self.assertEqual(stat.nlink, stat.st_nlink)

        self.assertEqual(stat.st_uid, self.uid)
        self.assertTrue(isinstance(stat.user, ops.utils.user))
        self.assertTrue(stat.user.id, self.uid)
        self.assertTrue(stat.user.name, self.user)

        self.assertEqual(stat.st_gid, self.gid)
        self.assertTrue(isinstance(stat.group, ops.utils.group))
        self.assertTrue(stat.group.id, self.gid)
        self.assertTrue(stat.group.name, self.group)

        self.assertFalse(stat.st_size is None)
        self.assertEqual(stat.st_size, stat.size)

        self.assertFalse(stat.st_atime is None)
        self.assertTrue(isinstance(stat.atime, datetime.datetime))

        self.assertFalse(stat.st_mtime is None)
        self.assertTrue(isinstance(stat.mtime, datetime.datetime))

        self.assertFalse(stat.st_ctime is None)
        self.assertTrue(isinstance(stat.ctime, datetime.datetime))

        self.assertFalse(stat.file)
        self.assertTrue(stat.directory)

if __name__ == '__main__':
    unittest.main()
