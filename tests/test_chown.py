import helper

import grp
import os
import unittest
import ops

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
        ops.chown(self.workspace.path, user=self.uid)

    def test_gid(self):
        ops.chown(self.workspace.path, group=self.gid)

    def test_user(self):
        ops.chown(self.workspace.path, user=self.user)

    def test_group(self):
        ops.chown(self.workspace.path, group=self.group)

    def test_chown(self):
        ops.chown(self.workspace.path, user=self.user, group=self.group)

    def test_recursive(self):
        ops.chown(self.workspace.path, user=self.user, group=self.group, recursive=True)

    def test_error(self):
        path = '/tmp/ops-chown-error'
        self.assertFalse(ops._chown(path, uid=-2))
        self.assertFalse(ops._chown(path, gid=-2))

        self.assertFalse(ops.chown(path, user=lambda x: x))
        self.assertFalse(ops.chown(path, user='ops-chown'))
        self.assertFalse(ops.chown(path, user=ops.user('ops-chown')))

        self.assertFalse(ops.chown(path, group=lambda x: x))
        self.assertFalse(ops.chown(path, group='ops-chown'))
        self.assertFalse(ops.chown(path, group=ops.user('ops-chown')))

if __name__ == '__main__':
    unittest.main()
