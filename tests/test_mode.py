import helper

import sys
import unittest
import ops

class PermTestCase(unittest.TestCase):

    def test_default(self):
        p = ops.perm()
        self.assertEqual(p.read, None)
        self.assertEqual(p.write, None)
        self.assertEqual(p.execute, None)

    def test_seven(self):
        p = ops.perm(7)
        self.assertTrue(p.read)
        self.assertTrue(p.write)
        self.assertTrue(p.execute)

    def test_six(self):
        p = ops.perm(6)
        self.assertTrue(p.read)
        self.assertTrue(p.write)
        self.assertFalse(p.execute)

    def test_five(self):
        p = ops.perm(5)
        self.assertTrue(p.read)
        self.assertFalse(p.write)
        self.assertTrue(p.execute)

    def test_four(self):
        p = ops.perm(4)
        self.assertTrue(p.read)
        self.assertFalse(p.write)
        self.assertFalse(p.execute)

    def test_three(self):
        p = ops.perm(3)
        self.assertFalse(p.read)
        self.assertTrue(p.write)
        self.assertTrue(p.execute)

    def test_two(self):
        p = ops.perm(2)
        self.assertFalse(p.read)
        self.assertTrue(p.write)
        self.assertFalse(p.execute)

    def test_one(self):
        p = ops.perm(1)
        self.assertFalse(p.read)
        self.assertFalse(p.write)
        self.assertTrue(p.execute)

    def test_zero(self):
        p = ops.perm(0)
        self.assertFalse(p.read)
        self.assertFalse(p.write)
        self.assertFalse(p.execute)

class ModeTestCase(unittest.TestCase):

    def test_default(self):
        m = ops.mode()

        self.assertEqual(m.user.read, None)
        self.assertEqual(m.group.write, None)
        self.assertEqual(m.other.execute, None)

    def test_get(self):
        m = ops.mode(0740)

        self.assertTrue(m.user.read)
        self.assertTrue(m.user.write)
        self.assertTrue(m.user.execute)

        self.assertTrue(m.group.read)
        self.assertFalse(m.group.write)
        self.assertFalse(m.group.execute)

        self.assertFalse(m.other.read)
        self.assertFalse(m.other.write)
        self.assertFalse(m.other.execute)

    def test_set(self):
        m = ops.mode(0640)

        m.group.write = True
        m.other.read = True
        self.assertEqual(m.numeric, 0664)

    def test_set_type(self):
        m = ops.mode()

        m.user = 7
        self.assertTrue(m.user.read)
        self.assertTrue(m.user.write)
        self.assertTrue(m.user.execute)

        m.group = 5
        self.assertTrue(m.group.read)
        self.assertFalse(m.group.write)
        self.assertTrue(m.group.execute)

        m.other = 2
        self.assertFalse(m.other.read)
        self.assertTrue(m.other.write)
        self.assertFalse(m.other.execute)

if __name__ == '__main__':
    unittest.main()
