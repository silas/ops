import helper

import pwd
import os
import unittest
import uuid
import ops.utils

class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.id = os.geteuid()
        self.name = pwd.getpwuid(self.id)[0]

    def test_default(self):
        user = ops.utils.user(self.name)
        self.assertEqual(user.id, self.id)
        self.assertTrue(user)

    def test_get_by_id(self):
        user = ops.utils.user(id=self.id)
        self.assertEqual(user.name, self.name)
        self.assertTrue(user)

    def test_get_by_invalid_id(self):
        user = ops.utils.user(id=-1)
        self.assertTrue(user.id is None)
        self.assertTrue(user.name is None)
        self.assertFalse(user)

    def test_get_by_name(self):
        user = ops.utils.user(name=self.name)
        self.assertEqual(user.id, self.id)
        self.assertTrue(user)

    def test_get_by_invalid_name(self):
        user = ops.utils.user(name=uuid.uuid4().get_hex())
        self.assertTrue(user.id is None)
        self.assertTrue(user.name is None)
        self.assertFalse(user)

if __name__ == '__main__':
    unittest.main()
