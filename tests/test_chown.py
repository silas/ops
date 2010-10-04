import grp
import os
import unittest
import opsutils

import helper

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
        opsutils._chown(self.workspace.path, uid=self.uid)

    def test_gid(self):
        opsutils._chown(self.workspace.path, gid=self.gid)

    def test_user(self):
        opsutils._chown(self.workspace.path, user=self.user)

    def test_group(self):
        opsutils._chown(self.workspace.path, group=self.group)

    def test_chown(self):
        opsutils.chown(self.workspace.path, user=self.user, group=self.group)

    def test_recursive(self):
        opsutils.chown(self.workspace.path, user=self.user, group=self.group, recursive=True)

if __name__ == '__main__':
    unittest.main()
