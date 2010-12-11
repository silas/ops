import helper

import grp
import os
import unittest
import uuid
import ops.utils

class GroupTestCase(unittest.TestCase):

    def setUp(self):
        self.id = os.getgid()
        self.name = grp.getgrgid(self.id)[0]

    def test_default(self):
        group = ops.utils.group(self.name)
        self.assertEqual(group.id, self.id)
        self.assertTrue(group)

    def test_get_by_id(self):
        group = ops.utils.group(id=self.id)
        self.assertEqual(group.name, self.name)
        self.assertTrue(group)

    def test_get_by_invalid_id(self):
        group = ops.utils.group(id=-1)
        self.assertTrue(group.id is None)
        self.assertTrue(group.name is None)
        self.assertFalse(group)

    def test_get_by_name(self):
        group = ops.utils.group(name=self.name)
        self.assertEqual(group.id, self.id)
        self.assertTrue(group)

    def test_get_by_invalid_name(self):
        group = ops.utils.group(name=uuid.uuid4().get_hex())
        self.assertTrue(group.id is None)
        self.assertTrue(group.name is None)
        self.assertFalse(group)

if __name__ == '__main__':
    unittest.main()
