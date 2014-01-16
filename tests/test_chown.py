from __future__ import unicode_literals

import helper

import grp
import os
import unittest

import ops
from mock import patch


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

    @patch('sys.platform', 'darwin')
    @patch('os.chown', return_value=True)
    def test_uid_darwin(self, chown):
        ops.chown(self.workspace.path, user=self.uid)
        chown.assert_called_with(self.workspace.path, self.uid, self.gid)

    def test_gid(self):
        ops.chown(self.workspace.path, group=self.gid)

    @patch('sys.platform', 'darwin')
    @patch('os.chown', return_value=True)
    def test_gid_darwin(self, chown):
        ops.chown(self.workspace.path, group=self.gid)
        chown.assert_called_with(self.workspace.path, self.uid, self.gid)

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
