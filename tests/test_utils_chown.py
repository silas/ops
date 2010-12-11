import helper

import grp
import os
import unittest
import ops.utils

class ChownTestCase(unittest.TestCase):

    def setUp(self):
        self.workspace = helper.Workspace()
        self.uid = os.geteuid()
        self.gid = os.getgid()
        self.user = os.getlogin()
        self.group = grp.getgrgid(self.gid)[0]

    def tearDown(self):
        self.workspace.destroy()

    def test_uid(self):
        ops.utils.chown(self.workspace.path, user=self.uid)

    def test_gid(self):
        ops.utils.chown(self.workspace.path, group=self.gid)

    def test_user(self):
        ops.utils.chown(self.workspace.path, user=self.user)

    def test_group(self):
        ops.utils.chown(self.workspace.path, group=self.group)

    def test_chown(self):
        ops.utils.chown(self.workspace.path, user=self.user, group=self.group)

    def test_recursive(self):
        ops.utils.chown(self.workspace.path, user=self.user, group=self.group, recursive=True)

if __name__ == '__main__':
    unittest.main()
